Title: Bits: Prometheus on Tailscale and fly.io
Slug: bits-prometheus-on-tailscale-and-fly-io
Date: 2023-02-21T21:21:58.326668
Category: sys
Tags: docker, tailscale, homelab, fly.io
Author: Chris Rose
Email: offline@offby1.net
Status: draft
Summary: A quick post about running Prometheus on fly.io (even on the free tier!) connected to tailscale

As an admin for [wandering.shop](https://wandering.shop) I find it useful to be able to see how the shop is doing, metrics-wise. I'm not a genius at operations, but I can read a dashboard... so I wanted to have one for the shop.

I tried out hosted Grafana, but it just didn't quite work the way I wanted it to, so I decided it was time to host my own Prometheus. The shop's budget isn't infinite, though, and cost is a factor. I'd heard of [fly.io](https://fly.io) in a few techie circles and decided to try it out for this.

Since the Shop's hosts are all connected via the Shop's Tailnet, the first thing I needed to do was get tailscale and prometheus into a single docker image. Fly's deployment model, at least in the simple case I need, is that you provide them a `Dockerfile`, and then they build it and run it. The dockerfile here ended up looking like this (you can actually find all of this code in our [monitoring repository](https://github.com/wandering-shop/monitor/tree/main/prometheus/) so feel free to just look there):

```dockerfile
FROM alpine:latest as builder
WORKDIR /app
COPY . ./
# This is where one could build the application code as well.


FROM alpine:latest as tailscale
WORKDIR /app
ENV TSFILE=tailscale_1.36.1_amd64.tgz
RUN wget https://pkgs.tailscale.com/stable/${TSFILE} && \
  tar xzf ${TSFILE} --strip-components=1

# https://docs.docker.com/develop/develop-images/multistage-build/#use-multi-stage-builds
FROM alpine:latest
RUN apk update && apk add ca-certificates iptables ip6tables prometheus && rm -rf /var/cache/apk/*

# Copy binary to production image
COPY --from=builder /app/start.sh /app/start.sh
COPY --from=builder /app/prometheus.yml /app/prometheus.yml
COPY --from=tailscale /app/tailscaled /app/tailscaled
COPY --from=tailscale /app/tailscale /app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale

# mounted data
VOLUME /data

# Run on container startup.
CMD ["/app/start.sh"]
```

The main things here are that we pull the tailscale static binary and put it in `/app/`. The other key bits are having a `/var/*/tailscale` set of directories to persist the tailscale authentication state.

The startup script is pretty minimal:

```bash
#!/bin/sh
set -x

hostname=${APP_HOSTNAME:-shop-monitor}

# ensure we have our data
mkdir -p /data/tailscale /data/tsdb

/app/tailscaled --state=/data/tailscale/tailscaled.state \
    --socket=/var/run/tailscale/tailscaled.sock &
/app/tailscale up --authkey="$TAILSCALE_AUTHKEY" --hostname=$hostname
/usr/bin/prometheus \
    --config.file=/app/prometheus.yml \
    --storage.tsdb.path=/data/tsdb \
    --storage.tsdb.retention.size=2GB
```

Basically, it kicks off a tailnet configuration and sets the hostname by default. That hostname can be overridden by environment configuration, but I'm not doing that.

Note that we've configured tailscale to store its state on `/data/` which is also where the Prometheus data store is. When we set up the Fly application, we're goint to create a persistent volume for it there.

The other thing to note is that we are limiting our Prometheus data retention to 2GB. Fly has a free tier with 3Gb of persistent storage, and 2Gb is _more_ than enough for current metrics for the Shop; if I needed more, we'd have to pay for it.

The Fly app configuration is similarly basic:

```toml
# fly.toml file generated for shop-watcher on 2023-01-10T17:43:32-08:00

app = "shop-watcher"
kill_signal = "SIGINT"
kill_timeout = 5
processes = []

[env]

[mounts]
source="shop_watcher_ts"
destination="/data"

[experimental]
  allowed_public_ports = []
  auto_rollback = true

[[services]]
  internal_port = 9090
  processes = ["app"]
  protocol = "tcp"
  script_checks = []
  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"

  [[services.http_checks]]
    interval = 10000
    grace_period = "5s"
    method = "get"
    path = "/metrics"
    protocol = "http"
    restart_limit = 0
    timeout = 2000
```

The interesting bits here are the `[mounts]` section, where we mount a volume at `/data`, and the checks, which enasure that our service is up; `fly.io` performs health checks on your app.

The last thing we need on `fly.io` is a secret: `TAILSCALE_AUTHKEY`; this allows your tailscale instance to start up and run headless. Create a key in your TailScale [admin page](https://login.tailscale.com/admin/settings/keys) that is ephemeral, pre-approved, and has tags consistent with your tailnet ACLs (I tag these instances as `tag:monitor` for example, but you can do whatever you like).

And with that, you can `flyctl deploy` this app!

On the Tailscale side, you want an ACL that allows this Prometheus instance to talk to the exporters on your hosts. For the shop, that looked a bit like this:

```json
{
	"action": "accept",
	"src":    ["tag:monitor"],
	"dst": [
		"*:9090",
		"*:9102",
		"tag:exporter:*",
		"tag:web:9113",
		"tag:web:9219",
	],
},
```
