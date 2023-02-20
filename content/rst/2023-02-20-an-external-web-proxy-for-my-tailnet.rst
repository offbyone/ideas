An External Web Proxy for my Tailnet
####################################

.. role:: raw-html(raw)
    :format: html

:slug: an-external-web-proxy-for-my-tailnet
:date: 2023-02-20T09:34:18.354245
:category: homelab
:tags: internet letsencrypt tailscale terraform
:author: Chris Rose
:email: offline@offby1.net
:status: published
:summary: Exposing web APIs on my tailnet to the world

I've become a huge fan of Tailscale_ as a VPN / software-defined network for my homelab. They've even introduced a really fantastic new alpha feature "Funnels" that lets you expose a service to the internet at :code:`https://<your-hostname>.<your-tailnet>`. It's really cool... **but** the URL you get is forever tied to Tailscale, instead of being on your own domain.

Now, there are ways around this; I could, for example, have a ``CNAME`` that points to the tailnet address. That'd be the *easy* way. Instead, what I built (and it's not super complicated!) is a reverse proxy living in a cloud provider, with a dedicated public IP, that acts as a bridge to my tailnet.

Bill of Materials
@@@@@@@@@@@@@@@@@

This solution uses 5 tools:

* Microsoft Azure - really, *any* cloud provider will work, but since my current employer provides me with some credits on Azure, I went with them.
* `Tailscale`_, already mentioned
* `Caddy`_, an easy-to-configure webserver that acts as the reverse proxy and provides TLS certificates via LetsEncrypt
* `Ansible`_, which I used to configure the webserver
* `Terraform`_, which I used to configure the cloud provider.

The Setup
@@@@@@@@@

===================
 The server itself
===================

On the server front, there isn't a lot to say here; I don't anticipate a heavy amount of traffic on this, since it's only going to be used for personal instances of Fediverse_ applications[ref]Expect a second post shortly on how I set up Bookwyrm_ using this[/ref] and other tiny web services that I feel the need to share with others. So, I picked the :code:`Standard_A1_v2` VM size from Azure[ref]It was the cheapest I could find there[/ref]. Interestingly, that constrained my choices of region quite a bit; a lot of regions had no capacity for it. So, my first step was to find out which regions *did* have it:

.. code-block:: shell-session

   $ az vm list-skus --size Standard_A1
   # ... some absolutely bananas amount of text
   $ az vm list-skus --size Standard_A1 | jq '.[] | select(.name == "Standard_A1_v2") | .locations[]'
   # A list of locations, including ``westus``

(A note on Azure data APIs; they are *shockingly* slow for simple information queries. If I were doing it over again, I would probably dump the full output to a local ``json`` file and then explore that, because *wow* did it ever take ages to do these queries!)

Once I nailed that down, I had to ensure I had the right SKU for an OS. That actually was harder than I expected, because the naming for Ubuntu SKUs changed between the writing of the blog posts I was following and today. This (as of 2023) found me what I needed for the OS image:

.. code-block:: shell-session

   $ az vm image list --all --publisher Canonical | jq .[].sku
   # a bunch of output. Like... a LOT. I wanted '22.04' though, so:
   $ az vm image list --all --publisher Canonical | jq -r .[].sku | grep 22.04 | sort -u
   # sort -u really helped here:
   22_04
   22_04-daily-lts
   22_04-daily-lts-arm64
   22_04-daily-lts-gen2
   22_04-gen2
   22_04-lts
   22_04-lts-arm64
   22_04-lts-cvm
   22_04-lts-gen2
   minimal-22_04-daily-lts
   minimal-22_04-daily-lts-gen2
   minimal-22_04-lts
   minimal-22_04-lts-gen2
   pro-22_04
   pro-22_04-gen2
   pro-22_04-lts
   pro-22_04-lts-gen2

(A note on generation; choosing a -gen2 image forces you on to the gen 2 hypervisor for Azure, which apparently the VM SKU I chose didn't support. So... don't just try gen2 without consideration.)

In the end, I had in hand a VM size, Image SKU, and region. On to terraform! I stared by copying the `Public IP example`_ from the terraform provider docs, with a few changes, mainly in the VM definition:

.. code-block:: terraform
   :hl_lines: 5 6 7 13 14 15 16 19 20 21 22

   resource "azurerm_linux_virtual_machine" "main" {
     name                            = "${local.prefix}-vm"
     resource_group_name             = azurerm_resource_group.main.name
     location                        = azurerm_resource_group.main.location
     size                            = "Standard_A1_v2"
     admin_username                  = "adminuser"
     disable_password_authentication = true
     network_interface_ids = [
       azurerm_network_interface.main.id,
       azurerm_network_interface.internal.id,
     ]

     admin_ssh_key {
       username   = "adminuser"
       public_key = file("~/.ssh/id_rsa.pub")
     }

     source_image_reference {
       publisher = "Canonical"
       offer     = "0001-com-ubuntu-server-jammy"
       sku       = "22_04-lts"
       version   = "latest"
     }

     os_disk {
       storage_account_type = "Standard_LRS"
       caching              = "ReadWrite"
     }
   }

Notable things in this block are that I disabled ssh with a password, provided my own RSA public key to the instance (Azure doesn't support ed25519 keys for some reason), and set the instance size and source image.

==============
 The Software
==============

I'm going to skip the Ansible part of my setup, because it's got a lot of other complexity that doens't matter here, and just dig into how I installed the two key software components on the host.

First, install tailscale. This follows `their instructions <https://tailscale.com/kb/1031/install-linux/>`_ more or less to a T:

.. code-block:: shell-session

   $ curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
   $ curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
   $ sudo apt-get update
   $ sudo apt-get install tailscale

I set up the tailscale daemon so the adminuser could operate it, and requested the ``border`` tag, which I'd pre-created in my ACL. The Tailnet section, below, will cover that aspect.

.. code-block:: shell-session

   $ tailscale up --operator adminuser --advertise-tags tag:border

Next, I installed Caddy, again following the `developer's instructions <https://caddyserver.com/docs/install#debian-ubuntu-raspbian>`_:

.. code-block:: shell-session

   $ sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
   $ curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   $ curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
   $ sudo apt update
   $ sudo apt install caddy

This installs a caddy systemd service, a default configuration, and sets up Caddy with http validation. While I've written `a post about getting LetsEncrypt to work with DNS <{filename}2021-10-06-automating-letsencrypt-route53-using-aws-iot.rst>`_, we won't need that here, since HTTP validation will work just fine; this server, unlike the rest of my homelab, will be on the internet.

The most important line of the caddyfile is this one::

   import /etc/caddy/sites-enabled.d/*.conf

``/etc/caddy/sites-enabled.d/`` is where we'll be putting each reverse proxy configuration.

My initial goal in building this setup was to create `my Bookwyrm instance <https://bookwyrm.offby1.net/>`_ so, I'll set that up. First, I'll make the site *available* by putting a configuration for it in ``/etc/caddy/sites-available.d/`` (this is a common pattern; define sites that are available, and then link them into the enabled directory to turn them "on"):

.. code-block:: caddyfile

   bookwyrm.offby1.net {
   	log {
   		output stdout
   	}

   	reverse_proxy http://100.68.30.64:8001
   }

The IP and port there are coming from my tailnet; they won't apply to you, but they're relevant in the tailscale configuration.

Once that file is created, link it in to sites-enabled.d and reload caddy:

.. code-block:: shell-session

   $ ln -s /etc/caddy/sites-available.d/bookwyrm.offby1.net.conf \
           /etc/caddy/sites-enabled.d/bookwyrm.offby1.net.conf
   $ sudo systemctl reload caddy

=======================
 Configuring Tailscale
=======================

This host will be on the internet, with all the attendant risks. While you could give it unfettered access to your tailnet, I don't recommend it. Instead, I defined some minimal ACL rules that allow it only access to the specific tailnet hosts and ports that my services are running on. For this example, my tailscale machine name is "bastion-vm"

On the `Tailscale ACL admin page <https://login.tailscale.com/admin/acls>`_, you want three things. First, you want to have a named host for this VM (why this doesn't come from Tailscale DNS, I'll never know!).

.. code-block:: json

   "hosts": {
      "bastion-vm": "100.0.0.1",
      "bookwyrm": "100.68.30.64",
   }

You'll want a test that makes sure the bastion is limited, but able to access what it needs, and that it can't be used to ssh freely around your tailnet:

.. code-block:: json

   "tests": [
       {
           "src": "tag:border",
           "deny": [
               "tag:homelab:22",
           ],
           "accept": [
               "bookwyrm:8001",
           ],
       },
    ]

Lastly, enable the ACL too:

.. code-block:: json

   "acls": [
       {
          "action": "accept",
          "src":    ["tag:border"],
          "dst": [
              "bookwyrm:8001",
          ],
       },
   ]

=====
 DNS
=====

The last thing to do is to set up DNS. I use AWS Route53 for my DNS, so all of the records are there. Rather than copy the public IP over from Azure to it, I take advantage of the ability of Terraform to interact with multiple cloud providers. The ``bastion-pip`` and ``bastion-resources`` names in the data below refer to the public IP resource name and group that the public IP server example defined.

I created a ``bastion.offby1.net`` A record, which is the default server for the bastion, and then defined a ``CNAME`` for bookwyrm. I'm ... honestly not sure it's the best way. Should I have created an A record for the subsite? I don't know; please feel free to tell me in the comments :D

.. code-block:: terraform

   terraform {
     required_providers {
       aws = {
         source = "hashicorp/aws"
         version = "~> 4.0"
       }
       azurerm = {
         source  = "hashicorp/azurerm"
         version = "=3.0.1"
       }
   }

   provider "aws" {
     profile = "me"
     region  = "us-west-2"
   }

   provider "azurerm" {
     features {}
   }

   data "azurerm_public_ip" "bastion_ip" {
     name                = "bastion-pip"
     resource_group_name = "bastion-resources"
   }

   resource "aws_route53_record" "bastion-offby1-net-A" {
     zone_id = aws_route53_zone.offby1-net.zone_id
     name    = "bastion.offby1.net"
     type    = "A"
     records = [
       data.azurerm_public_ip.bastion_ip.ip_address,
     ]
     ttl = "1800"
   }

   resource "aws_route53_record" "bookwyrm-offby1-net-CNAME" {
     zone_id = aws_route53_zone.offby1-net.zone_id
     name    = "bookwyrm.offby1.net"
     type    = "CNAME"
     records = [
       "bastion.offby1.net",
     ]
     ttl = "300"
   }


.. _Tailscale: https://tailscale.com/
.. _Caddy: https://caddyserver.com/
.. _Ansible: https://www.ansible.com/
.. _Terraform: https://www.terraform.io/
.. _Fediverse: https://fediverse.party/
.. _Bookwyrm: https://joinbookwyrm.com/
.. _Public IP example: https://github.com/hashicorp/terraform-provider-azurerm/tree/main/examples/virtual-machines/linux/public-ip
