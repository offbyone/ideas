Title: Mastodon Hosting, Part 1
Slug: mastodon-hosting-part-1
Date: 2022-11-07T17:01:33.869988
Category: internet
Tags: software, mastodon, tailscale, infrastructure, wandering.shop
Author: Chris Rose
Email: offline@offby1.net
Status: published
Summary: I inherited the system admin role for a Mastodon instance a couple of months ago, and recently I've needed to scale it. Here's a bit of how that went (and it's not done yet!)

A few months ago, the owners of [wandering.shop](https://wandering.shop)[ref]A small [Mastodon](https://joinmastodon.org) instance focusing on SF/F and crafty folk, mainly[/ref] decided they were looking to hand off ownership (and paying for hosting) for the instance. As I had settled on that instance some time ago for [my own Mastodon home](https://wandering.shop/@offby1), I had a vested interest in seeing it stay viable, so I volunteered to take over the technical side of running it.

Fast forward to last week, when _nothing of interest whatsoever occurred in social media_[ref]Actually, [things were rather dramatic](https://web.archive.org/web/20221107081949/https://www.washingtonpost.com/technology/2022/11/06/elon-musk-inner-circle/)[/ref] and we undertook to upgrade the instance software, Mastodon, to the latest, greatest, and hopefully most secure and stable version.

It did, as they say, not go well.

What we learned then was that we were already extremely close to the limits of the instance we were on; it took us 20 hours to catch up from the backlog generated when we were down for two hours, and the whole time we were recovering, all of the background processing that lets the Mastodon timeline work was not occurring, or was occurring hours late.

What I'm going to cover in this and subsequent posts is a look at what the infrastructure _is_, what I've done to mitigate the scaling issues, and where we need to go next. A lot of this information was drawn from the [Mastodon scaling guide](https://docs.joinmastodon.org/admin/scaling/) which identifies a lot of what is needed, but I had to put a bit of it together myself.

## What we started with

Wandering.Shop started out as a decent-sized basic droplet on DigitalOcean. 6 vCPUs, reasonable RAM and storage. Mastodon was installed using a variation on the `docker-compose` model, which had evolved over time. The system was set up with a relatively standard setup: nginx on the host, providing TLS termination via [LetsEncrypt](https://letsencrypt.org/), and the Mastodon web, queue, Redis, and Postgres 9.6 components running in compose. This kept the site running for quite a while, and was reasonably easy to upgrade when the time came.

Importantly, the queue was configured with a default, and very conservative, 10 threads to process incoming messages, as well as the updates and interactions on the site itself. When the site was sleepily handling the pre-Twitter load, that was plenty[ref]Ominous foreshadowing here[/ref]. Our media is stored in [S3](https://docs.joinmastodon.org/admin/config/#s3) rather than on the filesystem.

## Upgrading to Mastodon 3.5

The upgrade to Mastodon 3.5 took a bit of a turn, though; unlike other upgrades, this required a database migration, from postgres 9 to 14. The safest way to do that given the current setup (and we're still there... I'll get to that) was to turn off the site, dump the DB, create a new version 14 database, and then restore the backup into it. That took two hours, during which the rest of the fediverse moved on, and a backlog built at the same time as we started to see Twitter users deciding to use Mastodon, including several SF/F authors who for social reasons selected Wandering.Shop as their home instance.

## Catching up

It took us 20 hours to catch up, is the short version. The long version is that we actually were not able to process the backlog as fast as the incoming messages were arriving, not initially. The 10 threads of the worker queue were falling behind constantly, and at the rate of inbound messages we'd never catch up.

### Mitigation 1 - increase the worker queue size incrementally

I started conservatively, by increasing the worker queue size from 10 to 20. That ... didn't even slow the growth of the backlog, and the site remained (as I put it in a toot) "Wonky". I nudged it up a bit again, and still, nothing.

### Mitigation 2 - split the queues

Looking closer at the queues, I realized that we were actually trying to process multiple kinds of jobs and failing to get to the next queue, including the federation queues, because of the backlog. Mastodon has support for splitting out these work queues, so that was my next plan, leading to a split where I used one worker process to handle the default queue (which handles, among other things, local timeline updates and media uploads), a second worker to handle federation and email, and a third, tiny one, to deal with scheduled jobs.

And this got us to the end of day one. Bit by bit, 20 hours later, we had burned down the backlog... until the next morning when our users woke up again.

### Mitigation 3 - the database connection pool

By midmorning the next day, we had again hit a significant backlog. It seems that the steady state usage of the system was too high for our queue processors as they were.

I looked into the logs of each component more closely and noticed that the database was rejecting a _lot_ of connections, as it would only permit a certain number of concurrent connections at any time. After a few hours of tweaking the queues to have the "right" pool size to try manage this, I took the [scaling guide's suggestion of pgbouncer](https://docs.joinmastodon.org/admin/scaling/#pgbouncer) to provide a buffer between the database and the systems using it. This helped reduce the number of errors in the course of steady state operations, but didn't mitigate the host slowdown because...

### A Sidebar on Shared CPUs

I haven't gone and asked for confirmation of this, but after spending some time troubleshooting with <a href="https://infosec.exchange/@tacertain">Andrew Certain</a> looking at performance numbers, we formed the hypothesis that the shared CPU nature of the instance was giving us misleading load numbers, and we were in fact fully exhausting the CPU we had available despite appearing to be only at 70%.

The only way out of this was either to optimize the Mastodon code -- and that's not off the table! -- or to offload some work.

### Mitigation 4 - move the default queue off-host

One of the things we started noticing was that media uploads were in particular slow. This was a side effect of the `default` queue being behind; that queue both handled timeline updates for local posts _and_ media resizing and storage.

Realizing this, today I spun up a CPU-optimized, much-smaller droplet to handle some of this work. That instance, however, was for historical reasons _not_ in the account where the existing Shop was hosted, so I needed a way to securely communicate between the instances. Enter [Tailscale](https://tailscale.com/), a fantastic frontend for configuring [WireGuard](https://www.wireguard.com/), which I was able to use quickly to connect my new instance to the database on the old one.

As of this writing, all of our queues are empty, and the web is relatively responsive.

I plan to put the configuration up on our [server configuration repository](https://github.com/wanderingship/server) as soon as I get the two organized.
