Serve an S3 bucket over tailscale
#################################

.. role:: raw-html(raw)
    :format: html

:slug: serve-an-s3-bucket-over-tailscale
:date: 2023-12-09T22:24:21.463022
:category: homelab
:tags: tailscale, s3,
:author: Chris Rose
:email: offline@offby1.net
:summary: A short intro to the idea of serving an S3 bucket on your tailnet
:toot: https://wandering.shop/@offby1/111555217869127815
:status: published

I found myself wanting to host a private website that I could reliably update, but only serve it to users on my tailnet.

I didn't find anything obvious that could do the job, but I *did* realize that between the existence of `s3fs <https://github.com/jszwec/s3fs>`_, `tsnet <https://pkg.go.dev/tailscale.com/tsnet>`_, and the batteries that come with Go, I could probably bodge together something that does the job for me.

This is it: `offbyone/tailscale-s3-proxy <https://github.com/offbyone/tailscale-s3-proxy>`_.

It's not complicated, thanks to Go's tools to merge a custom network listner -- thanks, tailscale! -- and the adapter from ``fs.FS`` to ``http.FileSystem``. I almost feel like I didn't really do the work, honestly, but I can't find any extant code that does this.

Now, I'm hoping someone can read this and recommend to me a viable release process; I *can* build it myself, and just toss the binary around (and I will!) but I really would love to have this better-packaged. Suggestions? Keep in mind, I am a total* go newb.
