---
title: Mastodon Hosting, Again
slug: mastodon-hosting-part-2
date: "2022-12-22T14:30:00-0700"
category: open web
tags:
  - wandering.shop
  - software
  - mastodon
  - open web
  - tailscale
  - internet
author: Chris Rose
email: offline@offby1.net
summary: How the wandering.shop is laid out as of today, and where it needs to go next.
status: published
toot: "https://wandering.shop/@offby1/109561595065450093"
---
A bit more than a month ago, during the first wave of the latest Twitter exodus, I described [how Wandering.Shop survived the initial rush of demand]({filename}/posts/2022-11-07-mastodon-hosting-part-1.md) and stabilized after running an upgrade at the same time as we got slammed with massive load.

In this post, I'll talk a bit about what the shop looks like today, where it can scale in the future, and some of the work I'll be putting into it to make it more robust.

# Infrastructure

For the sake of brevity, I'm going to pretend that wandering.shop runs on "real computers", but in truth the system is hosted in DigitalOcean, _usually_ on a trio of droplets. The original host runs the databases, the web server, and the streaming server. The other two hosts are the asynchronous processors that Mastodon uses to update timelines, push and pull ActivityPub messages, and schedule maintenance.

For historical reasons, the hosts that run the Shop are divided into two DigitalOcean accounts. The original web host is in @phildini@wandering.shop's account, because he co-founded the Shop, and the queue hosts are in a shop-specific account. This means that I couldn't use DigitalOcean's own VPC constructs to isolate them.

As a result, the hosts that make up the Shop are networked together using [Tailscale](https://tailscale.com), which provides secure connectivity between the hosts in the Shop and lets me treat them as a single network despite the physical separation between them. I chose Tailscale because I'm already familiar with it in my own personal use[ref]my home network has a Tailnet associated with it that allows me to access my house's network from anywhere in the world[/ref].

All of the hosts are firewalled off using DigitalOcean's networking controls, allowing inbound connections only on the ports that Tailscale uses for WireGuard, and in the case of the web server, also "the web"[ref]As tempting as turning that off is, we kind of want the Shop's actual users to be able to access the hosts[/ref].

The three hosts currently running are:

- web / app / DB: a 6 shared-vCPU droplet with 16GB RAM, 320 GB of disk. This host _constantly_ runs hot. If I had infinite money, I'd be moving the rails app server off it onto its own host.
- 2x queue servers: 2vCPU dedicated CPU servers, limited RAM and disk. These hosts do _all_ of the sidekiq processing for the shop.

On occasion, when the queue has gotten out of hand, I have thrown one of my homelab hosts at the task queue as well, thanks to tailscale[ref]Seriously, Tailscale is really just that damn cool![/ref]; I've given a host on my personal tailnet access to the sidekiq queues and the media bucket, which has allowed me to expand the shop's capacity on demand.

## Media Storage

The Shop's media is stored in cloud storage, which is necessary when the workload is distributed across multiple hosts. We're using S3, in a public bucket, and media URLs are handed out directly to that bucket[ref]This is on the to-be-fixed list[/ref].

## Topology

For an idea of how this is laid out in practice, this is the current topology[ref]I suck at diagrams. Sorry...[/ref].

![wandering.shop system diagram]({attach}/images/mastodon/system-diagram-2022-12.drawio.png)

# Software

## Mastodon

We are running the docker version of Mastodon, version 4.0.2 as of this writing. It is running in three configurations: the web application and ActivityPub endpoint, the streaming API, and the sidekiq worker. At present we are running the stock Mastodon docker image, but at some point we plan to start customizing our instance with better instrumentation and designs.

The software is the thing I'm least engaged with right now; it _just works_ for the purposes of running a Mastodon instance, which is exactly what you want.

## Managing the Server

Our service is configured nearly entirely using Ansible, in a set of playbooks and roles that define the different components of the application. That means I can spin up new queue servers relatively quickly (not _entirely_ from boot, but close!) and ensures we all know what we're running.

# The Future of the Service

I've got a few plans for the service that I want to make happen. First[ref]Actually, this is already done[/ref] I intend to move the Rails server so that it is not co-tenanted with the database. That'll be a huge win for scaling,

Second, I'm going to put the media behind a CDN, probably CloudFront to start, and then maybe Fastly if the costs work out. We are paying through the _nose_ to host our media on S3, and that bleeding needs to stop.

Third, I want to move the raw objects from the media store to a cheaper object store. DigitalOcean has options there.

Fourth, it'd be keen to get infrastructure code in place to manage our DNS and our tailnet. That's in the plans -- I'm betting terraform will end up in the story somewhere.

# Other Areas of Interest?

If there's any interest in more of how this works, I'd be happy to see your comments. Just link this page and ask me anything.
