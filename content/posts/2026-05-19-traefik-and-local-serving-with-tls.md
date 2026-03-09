---
Title: Traefik and local serving with TLS
Slug: traefik-and-local-serving-with-tls
Date: 2026-05-19T09:09:07.887293
Tags: hacking, traefik, development, workflow, mkcert
Category: hacking
Author: Chris Rose
Email: offline@offby1.net
Status: published
Toot: https://wandering.shop/@offby1/116603253315703055
Summary: Being a high level walkthrough of how I use traefik and mkcert to present my development servers as "real, secure websites" during development.
---
I have developed a patten for local web development that I really like that gives me a few features that you can probably get with some full stack toolchain, but I've cobbled together out of a collection of open source components instead. It gives me TLS termination, nice domain names, and 100% local networking. I alluded to it indirectly in my last post about [RFC 6761 domain names]({filename}./2026-04-03-rfc-6761-special-use-domain-names.md) but I thought it worth expanding here.

First, there are two software components that are relevant: [traefik](https://traefik.io) and [mkcert](https://github.com/FiloSottile/mkcert). It takes a bit of setup for each of them, but when you're done you'll be able to navigate in your browser to `https://<your-project>.dev.localhost` and access whatever you're working on, with no certificate warnings or anything else.

### install and enable traefik 

Traefik is a modern web server that is particularly popular in the container ecosystem, but it also acts as an excellent reverse proxy. I installed it from homebrew, and am running it with `brew services`:

```shellsession
$ brew install traefik
$ brew services start traefik
```

:::{tip}
 I made one tiny change, in that I prefer keeping my configuration in `$HOME/.config` instead of the brew preferred location of `/opt/homebrew/etc/traefik/traefik.toml` so, after installing traefik but before starting the service, I symlinked `$HOME/.config/traefik/traefik.toml` to `/opt/homebrew/etc/traefik/traefik.toml`: `ln -s ~/.config/traefik/traefik.toml /opt/homebrew/etc/traefik/traefik.toml`. This article assumes you've done the same. 
:::

:::{note}
For me, `$HOME` is `/Users/offby1`, so take that into account with any examples below.
:::

This is the main traefik configuration; you should have this in place before starting traefik:

```toml
# -*- toml -*- mode
[entryPoints]
  [entryPoints.web]
    address = ":80"

    [entryPoints.web.http.redirections.entryPoint]
      to = "websecure"
      scheme = "https"

  [entryPoints.websecure]
    address = ":443"
    [entryPoints.websecure.http.tls]

[providers]
  [providers.file]
    directory = "/Users/offby1/.config/traefik/providers.d/"
    watch = true
```

### mkcert and setting up your local CA

This part of the process involves creating a wildcard certificate for `*.dev.localhost` and installing the "root" CA for it in your system trust stores, so that your browser will trust it. The full instructions can be found in [mkcert's documentation](https://github.com/FiloSottile/mkcert) but the short version is this:

```shellsession
# install mkcert
$ brew install mkcert
# ...
$ mkcert -install
# ... includes some sudo steps
```

Then, make the certificate. This is the important piece, because it's critical which domains you put in this. The `*.dev.localhost` allows all `.dev.localhost` endpoints to be TLS terminated, with a certificate your browser will trust:

```shellsession
$ mkcert -cert-file ~/.config/traefik/certs/wildcard.localhost.pem \
    -key-file ~/.config/traefik/certs/wildcard.localhost-key.pem \
    "*.dev.localhost"
```

Once this is done, enable the tls provider by adding `tls.yaml` to your traefik `providers.d` directory:

```yaml
tls:
  stores:
    default:
      defaultCertificate:
        # regenerate this using mkcert:
        # mkcert -cert-file ~/.config/traefik/certs/wildcard.localhost.pem \
        #     -key-file ~/.config/traefik/certs/wildcard.localhost-key.pem \
        #     "*.dev.localhost" "traefik.localhost"
        certFile: /Users/offby1/.config/traefik/certs/wildcard.localhost.pem
        keyFile: /Users/offby1/.config/traefik/certs/wildcard.localhost-key.pem
```

Lastly, make any proxies you want. Any valid YAML or TOML configuration of a traefik reverse proxy in `~/.config/traefik/providers.d/*` will automatically become part of your configuration. As an example, I run the pelican livereload server for this blog on port `:8192` on localhost, and I've got this file in `~/.config/traefik/providers.d/ideas.yaml`:

```yaml
http:
  routers:
    ideas:
      rule: "Host(`ideas.dev.localhost`)"
      service: ideas
  services:
    ideas:
      loadBalancer:
        servers:
          - url: http://127.0.0.1:8192
```

The bare act of creating that file means `https://ideas.dev.localhost/` opens my site's dev server in what appears to all intents and purposes as a "real website".
