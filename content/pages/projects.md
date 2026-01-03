---
title: Projects
slug: projects
date: "2005-03-18 21:29"
author: offby1
status: published
---

# The Hugo Awards

I am the lead, and nearly only, developer of the software package used by the Worldcon to collect Hugo Award nominations and votes since 2024, called [NomNom](https://nomnom.fans/)

NomNom is a [Python](https://python.org)/[Django](https://django.org) project that I wrote to support the Hugo Awards for [the Glasgow 2024 Worldcon](https://glasgow2024.org), and has been used since for the [Seattle in 2025 Worldcon](https://seattlein2025.org) and will be for [LACon V](https://lacon.org).

Contributions are always welcome.

# wandering.shop

I am the primary system operator for the [wandering.shop Mastodon instance](https://wandering.shop/); I was a random user, but when the original hosts decided they were done with it, and considered shutting it down, I stepped in to take over funding and operating it. Since then, with the help of our members, we are roughly self-funded and supported, and mostly my work is in making sure the database backups work (they do!) and ensuring the bills are paid (they are!).

# Hamcrest for Python

[hamcrest.org](https://hamcrest.org)

While this project's main model is the Java Hamcrest library, the Python library is still in active use as well. I started using Hamcrest when I was first learning Python, and ended up actively using it enough I fell into maintainership. It's a low-frequency task, but over the time I've been the lead maintainer, my collaborator on it ([Simon Brunning](https://brunn.ing)) have kept it modern, type-safe, and functional. 

# Small Projects

## Tailscale Stuff

I wrote a [tailscale s3 proxy](https://github.com/offbyone/tailscale-s3-proxy) to let me create a tailscale webserver backed by an S3 bucket. I use this to serve all the various documents pertaining to my house, like warranty information etc, as a sort of "house manual". 

Before [tailscale serve](https://tailscale.com/kb/1242/tailscale-serve) became a real thing, I used `tsnet` inspired by Xe Iaso to write [tailscale-reverse-proxy](https://github.com/offbyone/tailscale-reverse-proxy) as an authenticating proxy for some of my home web services.

I have a [tailscale sidecar docker image](https://github.com/offbyone/ops-containers/tree/main/sidecar) that publishes at [`ghcr.io/offbyone/sidecar`](https://github.com/offbyone/ops-containers/pkgs/container/sidecar) that I use to provide the network namespace to my other docker containers. This lets them act as their own individual tailnet hosts.

(I use a lot of tailscale!)

## Other things

- [fuckyour.email](https://github.com/offbyone/fuckyour.email), which is a simple web interface to the spam catcher that I run at `fuckyour.email`, for when I want your email logs to tell you what I think about your newsletter.

- [nazibar.com](https://nazibar.com), which is a (still very minor) site highlighting vendors and platforms that allow Nazi and fascist content to proliferate. This is, of course, 100% opinion.

# Ancient History

The projects linked here are projects I wrote, in some cases, 20+ years ago. I keep the pages here because I don't really like to let links die, but I neither work on these any more nor really have interest in the tools they're referencing. 

- [Azureus Plugin Tutorial]({filename}/pages/azureus-plugin-tutorial.md)
- [LibraryThing WordPress Widget]({filename}/pages/librarything-blog-widget.md)
- [Azureus AutoStop Plugin]({filename}/pages/azureus-autostop-plugin.md)
- [Azureus AutoCategorization Plugin]({filename}/pages/azureus-autocat-plugin.md)
- [Azureus IM Notification Plugin]({filename}/pages/azureus-jabber-plugin.md)
