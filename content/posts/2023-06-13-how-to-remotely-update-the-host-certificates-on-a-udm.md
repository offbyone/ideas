Title: How to remotely update the host certificates on a UDM
slug: how-to-remotely-update-the-host-certificates-on-a-udm
date: 2023-06-13T22:25:37.301572
category: homelab
tags: letsencrypt, iot, automation
author: Chris Rose
email: offline@offby1.net
summary: I combined a few tools -- lego and some helpers -- to get my UDM Pro's SSL certificate to renew automatically
status: published
toot: https://wandering.shop/users/offby1/statuses/110541002888289332

I struggled with whether this was worth writing up,

I upgraded my NAS to DSM7 about 3 months ago, which was a whole thing on its own, but one side effect of that was that it turns out it killed the letsencrypt updater I'd used. 90 days later, I got a certificate error when I used the web interface. And\... apparently at some point, without thinking about it, I'd also set up my Unifi Dream Machine Pro (yep, that's SEO right there!) with something that expired around the same time\[ref\]I honestly have no recollection of this. I wish I could remember what I did\![/ref\].

So\...

# Why is this hard for me?

There are a lot of ways I could have made this easier for myself. I could have set up a wildcard certificate somewhere that let me get my SSL in bulk, for example. Or, I could have compromised on the security of my Route53 credentials and just created a user with a permanent access key and secret key ([I clearly am not willing to do that]({filename}2021-10-06-automating-letsencrypt-route53-using-aws-iot.md)). Given that what I want is "DNS challenges, with short-lived credentials" I had to solve it with something else.

That means I can't use the built in HTTP challenges or the built in DNS challenges. I'd feel bad about that, but neither Synology nor Ubiquiti actually *have* support for ACME's `dns-01` challenge in the first place. So, the fact I'm doing it "the hard way" puts me on an equal footing with every other user of those platforms, even the ones who are way more relaxed about security.

The main groundwork here is that I have a modified version of the aforelinked IOT certificate -\> AWS credentials flow\[ref\]Writing this up is on my list; it tends to be pretty bespoke for each environment, so it's not well-organized yet\[/ref\] on the host. It's patched mainly so that it also generates an AWS CLI credentials file with a specific profile, so that I can use that in the ACME client instead of passing in AWS credentials (because [the AWS credential environment variables are not suppored in Lego](https://go-acme.github.io/lego/dns/route53/#credentials)).

# LetsEncrypt / ACME on the Synology

This part was surprisingly easy. Not because I solved it myself, but someone already did it\[ref\]the third-best kind of code is "working code that someone else wrote"\[/ref\], and it's basically perfect. [\@JessThysoee](https://github.com/JessThrysoee/synology-letsencrypt) made a package that sets up a complete suite of LetsEncrypt (well, really, ACME) tools on the Synology that does 95% of what I needed. Since that tool supports both customization (via an `env` file) and integration with Synology's certificate machinery (via `hooks`) I was sorted. The `AWS_SHARED_CREDENTIALS_FILE` is created by my IOT integration, renewed every 30 minutes (unless `us-east-1` is down, of course\![ref\]For context in the future, this post was written on a day where us-east-1 experienced a major outage.\[/ref\]).

My `env` looks like this:

``` bash
DOMAINS=(--domains "unifi.lan.offby1.net" --domains "unifi.vpn.offby1.net")
EMAIL="autoadmin@blob.lan.offby1.net"

DNS_PROVIDER="route53"
export AWS_SHARED_CREDENTIALS_FILE=/root/iot/letsencrypt/credentials
export AWS_PROFILE=iot_letsencrypt
```

The hooks file is the default from the `synology-letsencrypt` package. It really was that simple.

# The Unifi Dream Machine SSL Cert

To get the UDM certificates installed, though, I needed to [patch the letsencrypt script package](https://github.com/JessThrysoee/synology-letsencrypt/pull/6) a bit. Specifically, I added two features: One, don't nuke the hook script each run, and two, let me have more than one configuration. That second part isn't [strictly]{#strictly}\_ necessary, but it made it way easier.

I created an SSH key to access my UDM from my Synology as `root`. That makes the hook passwordless. Not perfect, but if someone has root access on my hosts, I have bigger problems\[ref\]Now that I think about it, I wonder if I could make a webhook on the Synology that just gives out a tarball of the latest certificates, and then run a cron job on the UDM\... nah, I don't think that's a good investment of my time.\[/ref\].

Once I had that, I set this as my hook script for certificate renewal:

``` bash
if [[ "$LEGO_CERT_DOMAIN" = unifi.*.offby1.net ]]; then
    bak_name=$(date +%Y%m%d-%H%M%S)
    ssh root@192.168.1.1 "mkdir -vp /root/backups/$bak_name && cp -v /data/unifi-core/config/unifi-core* /root/backups/$bak_name/"

    scp "$LEGO_CERT_PATH" \
        root@192.168.1.1:/data/unifi-core/config/unifi.host.crt
    scp "$issuer_cert" \
        root@192.168.1.1:/data/unifi-core/config/unifi.issuer.crt
    scp "$LEGO_CERT_KEY_PATH" \
        root@192.168.1.1:/data/unifi-core/config/unifi-core.key

    ssh root@192.168.1.1 "cat /data/unifi-core/config/unifi.host.crt /data/unifi-core/config/unifi.issuer.crt > /data/unifi-core/config/unifi-core.crt"

    ssh root@192.168.1.1 systemctl restart unifi-core
fi
```

What that's doing is:

1.  If the hostname is my UDM or any of its SANs, act.
2.  Specifically, back up the existing certificates.
3.  Then, copy the cert, the issuer chain, and the private key to the UDM.
4.  Merge the host cert and the issuer chain into a fullchain certificate.
5.  Restart the Unifi core web server

All that gets you a nice, renewed TLS cert!
