Title: Putting a dockerized service on your tailnet
slug: putting-a-dockerized-service-on-your-tailnet
date: 2023-06-09T16:14:16.627566
category: homelab
tags: internet, tailscale, docker
author: Chris Rose
email: offline@offby1.net
summary: Putting a single, secured webserver
status: published
toot: https://wandering.shop/@offby1/110518421975881346

I got an itch to stop having my homelab services running at `https://some-tailscale.my-tailnet/service`, and instead be able to reasonably cheaply have `https://service.my-tailnet/` be the order of the day. You may not have this desire, and if that's the case congratulations; you're probably in a healthier mental space than I am.

*If*, however, you find yourself wishing you could just have infinite hostnames for your services, and never deal with a webroot configuration again, then maybe this post is for you.

# First, a bit of background

I've been using [Tailscale](https://tailscale.com/) for a couple of years now; it provides me with a great way to maintain access to my home network wherever I am, securely, and with a few nice perks like acting as a VPN and [Private golinks](https://tailscale.com/blog/golink/) along the way.

A short time ago, Xe Iaso whipped [a neat proxy for Grafana](https://tailscale.com/blog/golink/) that I set up, so that I now have `https://grafana.my-tailnet` with all the good authentication stuff. That got me thinking\... what if I could trade in my current system \-- generally [Caddy](https://caddyserver.com/) with path-based reverse proxying to other services \-- for one where each service has what appears to be its own host in the tailnet? I'd never thought of it before; it's frankly fascinating what Tailscale does with their Go library, creating "hosts" out of whole cloth, but once the idea hit me, I started considering how I'd make it happen.

If you know Tailscale you might be asking yourself right now "why didn't he use `tailscale serve`?" and that's a great question! The reason is, `serve` for all its excellent functionality, is still 1:1 with the host; I would end up with `https://some-tailscale.my-tailnet` and not the service-specific URL I want. I'd either have just one per host, or different ports instead of hostnames, and I wanted something fancier than that.

# How I Didn't Do It

I decided a natural way to go about this would be to make a Docker iamge that contained the Tailscale proxy and the service, where the proxy would be installed and running alongside the supported service. That took way more time than you'd hope to get working, and actually came with a few frustrating hurdles that eventually soured me on the process[ref]Hey, did you know that there are no Linux/ARMv7 builds for the cryptography Python library? Did you also know that building that wheel can take over an hour on a GitHub action runner? I sure do\![/ref].

The reasons I moved on from this approach were a combination of "I didn't want to maintain a service manager in Docker" (supervisor did the job, but it always felt clunky) and "cramming service and proxy together in the container made for grotty build logic and weird versioning".

# How I Did Do It

What I eventually settled on relies on docker-compose; it turns out to be a pretty natural fit for the problem, and it gives me the flexibility I need to plug in any kind of backing service I want. Along the way, though, I had to solve a couple of problems:

## The Proxy

The Tailscale grafana proxy is a fantastic thing, but it doesn't set several key proxy headers for generic reverse proxy use. In order to have the proxy perform up to snuff, I needed to fork it, so I did: <https://github.com/offbyone/tailscale-reverse-proxy>. This is *not elegant*; I yoinked the reverse proxy code (note to self, I need to credit the Tailscale folks for it under the BSD license\...) and added support for the needed headers:

- `X-Forwarded-Proto`
- `X-Forwarded-Host`
- `X-Forwarded-Port`

These are sufficient to allow the proxy to function as a pure reverse proxy.

This project offers both `go` installation as a module and a Docker image:

``` shell-session
$ docker volume create tailscale-data
$ docker run --rm -it ghcr.io/offbyone/tailscale-reverse-proxy:edge \
     -v tailscale-data:/var/lib/tailscale \
     --env-file ./file-with-TS_AUTH_KEY-in-it \
     /usr/local/bin/tailscale-reverse-proxy \
     -state-dir=/var/lib/tailscale \
     -hostname=your-proxy-host \
     -backend-addr=local-service-reachable-from-the-container:8080
```

(I'm actually still trying to figure out how this is working without some of the capabilities I assumed Docker tailscale needed\... please feel free to tell me in comments!)

## The Service

Compared to this, the service is dead simple; literally ANY dockerized service that listens for HTTP on a TCP port can be dropped into this as a service in compose. Wiring them up couldn't be easier either; my compose file looks, roughly, like this:

``` yaml
---
version: "3.3"
services:
  proxy:
    image: ghcr.io/offbyone/tailscale-reverse-proxy:main
    links:
      - the-service
    volumes:
      - tailscale-data:/var/lib/tailscale
    # the `my-pretty-service-name` here is how you get the nice
    # https://my-pretty-service-name.my-tailnet URL
    command: /usr/local/bin/tailscale-reverse-proxy -state-dir=/var/lib/tailscale -hostname=my-pretty-service-name -backend-addr=the-service:8080 -use-https
    # this env file contains the TS_AUTH_KEY that the proxy uses to set
    # itself up.
    env_file: .proxy.env
  the-service:
    container_name: the-service  # because this is how the proxy references it
    image: the-service:latest
    restart: unless-stopped

volumes:
  tailscale-data:
```

When you start this compose service up, as long as you've provided `.proxy.env` with a Tailscale auth key, your tailnet will have a brand new "machine" at `https://my-pretty-service-name.my-tailnet` that forwards to your service, whatever it is.

Happy hacking on it!
