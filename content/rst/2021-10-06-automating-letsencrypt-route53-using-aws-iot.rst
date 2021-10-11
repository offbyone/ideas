Using AWS IoT to provision an IAM role for home lab devices
###########################################################

.. role:: raw-html(raw)
    :format: html

:slug: automating-letsencrypt-route53-using-aws-iot
:date: 2021-10-06T23:17:22.563676
:category: programming
:tags: aws, iot, terraform, ansible, letsencrypt, automation
:author: Chris Rose
:email: offline@offby1.net
:excerpt: Being a description of the steps I went through to turn my Raspberry Pi devices into IoT things so that I could eventually have them automatically use letsencrypt.
:status: published

I'm going to start with a bit of a rambling preamble (pre-ramble?) about what I wanted to achieve, and some of the semi-arbitrary constraints I set for myself.

I have been wanting to migrate from my homegrown self-signed CA for TLS on my home lab for some time. There are a few reasons for this, but chief among them is the pain in the ass of installing the trust root on every new device I get, and I just got a new phone. This was, as they say, the last straw. I decided that I needed to transition off this janky, hacked-together solution. However... I had some constraints.

First, I didn't want to open my home lab hosts to the internet. This meant that I couldn't use letsencrypt's HTTP challenge to manage certificates. I would have to use DNS.

Second, I didn't want to manage long term DNS management credentials on the hosts. I assume Linux has a keychain-like mechanism somewhere, but I've never been able to find one that made me comfortable in how it could be used, so I needed something I could use to give them a "host identity" that I could revoke if I needed to, but would mostly just "work" otherwise.

Third, I didn't want to spend a tonne of time manually managing this with every new host I got. The less effort it took to add a new host, the happier I'd be.

It took me a while, but I think I've hit on a solution that satisfies me. The short version is that I am:

* Creating an AWS IoT "Thing" for each machine in my home lab using Terraform to automate that.
* Installing the thing's X509.1 certificate in a "secure" way on each host (readable only by the ``iot`` service user)
* Using the host certificate to get temporary credentials for the host to perform a limited set of actions in the AWS account that controls my LAN subdomain.
* Installing and configuring certbot to use those credentials to satisfy an ACME challenge using my LAN subdomain

I'm going to cover the first half of that in this post, and I'll see if I can assemble a reasonable write-up for the second half sometime later.

Creating an IoT Thing for each machine in my lab
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

First... "Why would you do this, Chris?". Well, I took advantage of having access to a group of well informed AWS engineers at work to ask if there was a solution to my credential storage issue, and someone pointed me at a documentation on how I could `authorize direct calls to AWS services using IoT`_ and, with a bit of a hard think, I realized that yes, that would in fact solve my problem. What I gleaned from it was that once I could treat each machine in my lab as a "thing" in IoT, I could provide each of them with an X509.1 certificate that they could use to get credentials to act in other parts of my account.

I've been a big fan of Terraform for infrastructure automation, so I proceeded to whip up a piece of Terraform that did this for me. First, I needed a device role for the IoT credential provider, that could assume roles in my account:

.. code-block:: terraform

    # define a policy that allows the IoT thing to assume a role.
    data "aws_iam_policy_document" "iot-assume-role" {
      statement {
        actions = ["sts:AssumeRole"]

        effect = "Allow"

        principals {
          type        = "Service"
          identifiers = ["credentials.iot.amazonaws.com"]
        }
      }
    }

    resource "aws_iam_role" "certbot-dns-update" {
      name               = "certbot-dns-update"
      assume_role_policy = data.aws_iam_policy_document.iot-assume-role.json
    }

It was pretty important to me that this role only have limited access in my account. I didn't even want it to be able to touch general DNS records, only the LAN subdomain that I want a wildcard for. This zone doesn't contain actual DNS records for my LAN domain, but my top level domain delegates to it. .

.. code-block:: terraform

    data "aws_route53_zone" "lan" {
      name = "lan.offby1.net."
    }

    # Here's where the rubber meets the road on that policy; this allows
    # the assumed role to only modify the one specific zone.
    data "aws_iam_policy_document" "dns-access" {
      statement {
        effect    = "Allow"
        actions   = ["route53:ListHostedZones", "route53:GetChange"]
        resources = ["*"]
      }

      statement {
        effect    = "Allow"
        actions   = ["route53:ChangeResourceRecordSets"]
        resources = ["arn:aws:route53:::hostedzone/${data.aws_route53_zone.lan.zone_id}"]
      }
    }

    resource "aws_iam_policy" "dns-access" {
      name   = "dns-access"
      policy = data.aws_iam_policy_document.dns-access.json
    }

    resource "aws_iam_role_policy_attachment" "dns-access" {
      role       = aws_iam_role.certbot-dns-update.name
      policy_arn = aws_iam_policy.dns-access.arn
    }


`From the docs <https://docs.aws.amazon.com/iot/latest/developerguide/authorizing-direct-aws.html#authorizing-direct-aws.walkthrough>`_:

    The device that is going to make direct calls to AWS services must know which role ARN to use when connecting to AWS IoT Core.  Hard-coding the role ARN is not a good solution because it requires you to  update the device whenever the role ARN changes. A better solution is to  use the CreateRoleAlias API to create a role alias that points to the role  ARN. If the role ARN changes, you simply update the role alias. No change  is required on the device.


.. code-block:: terraform

    resource "aws_iot_role_alias" "cert-dns" {
      alias               = "homelab-certbot-role-alias"
      role_arn            = aws_iam_role.certbot-dns-update.arn

      # this indicates how long the temporary credentials used by this role will
      # last for. This is an hour. Tune this if you want a better window for that.
      credential_duration = 3600
    }

When I said I wanted it to be easy to make >1 of these, I meant it. Rather than copying all of the hosts one after the other, I just put them in a set and then instantiated one of each using a module to set them up (see the next section).

.. code-block:: terraform

    variable "iot-things" {
      type = set(string)

      default = [
        "dashboard",
        "pi-hole",
      ]
    }

    module "iot-hosts" {
      for_each         = var.iot-things
      source           = "./homelab-host"
      hostname         = each.key
      certificate-path = "${path.module}/secrets/"
      role_arn         = aws_iot_role_alias.cert-dns.arn
    }


The last step here is to output some of the information I just found. This'll be used in the Ansible steps I document below, which will use this data to configure each host [ref]Yes, I know that there are formatting errors in this block. See `pygments #1909`_ [/ref].

.. code-block:: terraform

    data "aws_iot_endpoint" "credentials" {
      endpoint_type = "iot:CredentialProvider"
    }

    output "iot-endpoint" {
      value = data.aws_iot_endpoint.credentials.endpoint_address
    }

    # Export Terraform variable values to an Ansible var_file
    resource "local_file" "tf_ansible_vars_file_new" {
      content  = <<-DOC
        # Ansible vars_file containing variable values from Terraform.
        # Generated by Terraform mgmt configuration.

        iot_credential_provider_endpoint: ${data.aws_iot_endpoint.credentials.endpoint_address}
        iot_credential_role_alias: ${aws_iot_role_alias.cert-dns.alias}
        DOC
      filename = "./vars/tf_ansible_vars_file.yml"
    }

Host configuration using Terraform
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

This is the part where we create the certificate that we'll use to turn our home lab devices into IoT things. This is *not* a pretty, polished Terraform module; it's a single-file module that does the bare minimum to create a thing, and then write out its client certificate in a place that Ansible will search in order to install it.

There are two things to note in this: first is the :code:`resource "aws_iot_thing" "host"` section, where we slugify the hostname so that IoT allows it. Second is the :code:`resource "local_file` pair of resources. These write out the keys you'll be installing later. The output here *should not be checked into revision control*. You can configure the path for these in the module call, above. I've got that path added to :code:`.gitignore`.

.. code-block:: terraform

    variable "hostname" {
      type = string
    }

    variable "certificate-path" {
      type = string
    }
    variable "role_arn" {
      type = string
    }

    variable "domain" {
      type    = string
      default = "lan.offby1.net"
    }

    variable "active" {
      type    = bool
      default = true
    }

    resource "aws_iot_thing" "host" {
      name = replace("${var.hostname}.${var.domain}", ".", "-")
    }

    resource "aws_iot_certificate" "cert" {
      active = var.active
    }

    data "aws_iam_policy_document" "cert-dns" {
      statement {
        effect = "Allow"
        actions = [
          "iot:AssumeRoleWithCertificate",
        ]
        resources = [var.role_arn]
      }
    }

    resource "aws_iot_policy" "cert-dns" {
      name   = replace("${var.hostname}.${var.domain}-assume-dns-role", ".", "-")
      policy = data.aws_iam_policy_document.cert-dns.json
    }

    resource "aws_iot_policy_attachment" "cert-dns-policy" {
      policy = aws_iot_policy.cert-dns.name
      target = aws_iot_certificate.cert.arn
    }

    resource "aws_iot_thing_principal_attachment" "principal" {
      principal = aws_iot_certificate.cert.arn
      thing     = aws_iot_thing.host.name
    }

    resource "local_file" "private-key" {
      filename = "${var.certificate-path}/${var.hostname}.${var.domain}.key"
      content  = aws_iot_certificate.cert.private_key
    }

    resource "local_file" "device-cert" {
      filename = "${var.certificate-path}/${var.hostname}.${var.domain}.pem"
      content  = aws_iot_certificate.cert.certificate_pem
    }

Using Ansible to turn a machine into an IoT thing
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

I created an Ansible role -- :code:`iot-thing` -- that does this, that I can associate with any host in my inventory. It's a simple enough role, that defines an :code:`iot` user that owns a restricted folder that contains the host certificate, and writes out credentials to a less-restricted folder that can be read by any user in the :code:`iot-credentials` group.

I was considering breaking it down into smaller bits, but I hope it's pretty simple. The first section loads the :code:`tf_ansible_vars_file.yml` that was written out above, to get the credential provider endpoint and role. After, we create the :code:`iot` user and its groups. Laying out the folders is important, after; the iot certificate needs to be in a place that only the :code:`iot` user can read, but the credentials need to be shared with the group. We use the sticky bit to manage that.

Lastly, we install the systemd unit that refreshes the credentials and the timer that invokes it every half hour (to match our one hour credential expiry; we don't want to be too aggressive, but we also need some freshness.)

========================
 :code:`tasks/main.yml`
========================

.. code-block:: yaml

    ---
    - name: terraform variables
      include_vars:
        file: tf_ansible_vars_file.yml
        name: tf

    - name: iot group
      group:
        name: iot
        state: present
      become: yes

    - name: iot credential group
      group:
        name: iot-credentials
        state: present
      become: yes

    - name: iot user
      user:
        name: iot
        state: present
        group: iot
        groups:
          - iot-credentials
      become: yes

    - name: iot base directory
      file:
        path: /opt/iot
        state: directory
        owner: iot
        group: iot-credentials
        mode: 0750
      become: yes

    - name: iot credential directory
      file:
        path: /opt/iot/credentials
        state: directory
        owner: iot
        group: iot-credentials
        mode: 02750
      become: yes

    - name: iot service directories
      file:
        path: "{{ item }}"
        state: directory
        owner: iot
        group: iot
        mode: 0700
      with_items:
        - /opt/iot/certs
        - /opt/iot/bin
        - /opt/iot/etc
      become: yes

    - name: install the device certificate
      copy:
        src: "secrets/{{ ansible_fqdn }}.pem"
        dest: /opt/iot/certs/device.pem.crt
        owner: iot
        group: iot
        mode: 0600
      become: yes

    - name: install the device key
      copy:
        src: "secrets/{{ ansible_fqdn }}.key"
        dest: /opt/iot/certs/device.pem.key
        owner: iot
        group: iot
        mode: 0600
      become: yes

    - name: install the CA cert
      get_url:
        url: "https://www.amazontrust.com/repository/{{ item.path }}"
        dest: "/opt/iot/certs/{{ item.path }}"
        owner: iot
        group: iot
        mode: 0600
        checksum: "{{ item.checksum }}"
      with_items:
        - path: AmazonRootCA1.pem
          checksum: sha256:2c43952ee9e000ff2acc4e2ed0897c0a72ad5fa72c3d934e81741cbd54f05bd1
      become: yes
      check_mode: no

    - name: install the credential update script
      copy:
        src: update-credentials.sh
        dest: /opt/iot/bin/update-credentials.sh
        owner: iot
        group: iot
        mode: 0750
      become: yes

    - name: install the credential environment variables
      template:
        src: iot-credentials.env.j2
        dest: /opt/iot/etc/iot-credentials.env
        owner: iot
        group: iot
        mode: 0600
      become: yes

    - name: install the credential update service
      copy:
        src: update-iot-credentials.service
        dest: /lib/systemd/system/update-iot-credentials.service
      become: yes

    - name: install the credential update cron
      copy:
        src: update-iot-credentials.timer
        dest: /lib/systemd/system/update-iot-credentials.timer
      become: yes

    - name: reload the systemd daemon
      systemd:
        daemon_reload: yes
      become: yes

    - name: run the credential updater
      service:
        name: update-iot-credentials.service
        state: started
      become: yes

    - name: enable the credential update timer
      service:
        name: update-iot-credentials.timer
        state: started
        enabled: yes
      become: yes

==========================================
 :code:`templates/iot-credentials.env.j2`
==========================================

.. code-block:: jinja2

    # This uses the same transform as in the terraform module, above.
    # The output should match
    IOT_THING_NAME={{ ansible_fqdn | replace('.', '-') }}
    IOT_ENDPOINT_URL=https://{{ tf.iot_credential_provider_endpoint }}
    IOT_ROLE_ALIAS={{ tf.iot_credential_role_alias }}

==============================================
 :code:`files/update-iot-credentials.service`
==============================================

.. code-block:: ini

    [Unit]
    Description = Update the device IOT credentials

    [Service]
    ExecStart = /opt/iot/bin/update-credentials.sh
    EnvironmentFile = /opt/iot/etc/iot-credentials.env
    WorkingDirectory = /opt/iot
    User = iot


============================================
 :code:`files/update-iot-credentials.timer`
============================================

.. code-block:: ini

    [Unit]
    Description=Run the credential updater every half hour
    Requires=update-iot-credentials.service

    [Timer]
    Unit=update-iot-credentials.service
    OnBootSec=1min
    OnUnitInactiveSec=30m
    RandomizedDelaySec=1m
    AccuracySec=1s

    [Install]
    WantedBy=timers.target


=====================================
 :code:`files/update-credentials.sh`
=====================================

This is the meat of the credential retrieval tool. It uses CURL to call the :code:`IOT_ENDPOINT` using a role alias/thing-specific set of headers and URL construction. What it gets back is a json document containing the credentials for this "Thing" lasting as long as we've allowed in the resource definitions above.

It then uses :code:`jq` to extract the keys, and write them into a credentials file that the AWS SDK can be configured to use (and will be, in part 2!).

All the paths in here are hardcoded to their final locations, but if (when?) I generalize this as an ansible-galaxy module, they'll probably be configurable.

.. code-block:: bash

    #!/usr/bin/env bash

    set -eu -o pipefail

    CERT_ROOT=/opt/iot/certs
    CREDENTIAL_JSON=/opt/iot/credentials/latest.json
    CREDENTIAL_FILE=/opt/iot/credentials/default

    curl -o "$CREDENTIAL_JSON" \
        --cert "$CERT_ROOT/device.pem.crt" \
        --key "$CERT_ROOT/device.pem.key" \
        --cacert "$CERT_ROOT/AmazonRootCA1.pem" \
        -H "x-amzn-iot-thingname: $IOT_THING_NAME" \
        "$IOT_ENDPOINT_URL/role-aliases/$IOT_ROLE_ALIAS/credentials"

    AWS_ACCESS_KEY_ID="$(jq -r -e '.credentials.accessKeyId' <"$CREDENTIAL_JSON")"
    AWS_SECRET_ACCESS_KEY="$(jq -r -e '.credentials.secretAccessKey' <"$CREDENTIAL_JSON")"
    AWS_SESSION_TOKEN="$(jq -r -e '.credentials.sessionToken' <"$CREDENTIAL_JSON")"

    cat <<EOF >$CREDENTIAL_FILE.tmp
    [default]
    aws_access_key_id=$AWS_ACCESS_KEY_ID
    aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
    aws_session_token=$AWS_SESSION_TOKEN
    EOF

    mv $CREDENTIAL_FILE.tmp $CREDENTIAL_FILE

    chmod 640 "$CREDENTIAL_FILE" "$CREDENTIAL_JSON"

Where are We? What's Next?
@@@@@@@@@@@@@@@@@@@@@@@@@@

By the time you get here, you have a few things: One, you have AWS IoT "things" that are 1:1 with your homelab hosts. Each one is configured to be able to provide short-lived credentials for accessing specific other AWS resources, in this case a DNS subdomain zone that can be polled for ACME challenges. The other thing you have is a simple systemd-invoked timer that will refresh your host-specific credentials using the keys you generated when creating the thing.

Next, well, once you've got all of this put together, the next step is to wire up letsencrypt's certbot to use these credentials to answer ACME's DNS challenge, and install the certificates. That'll be in Part 2.

.. _`authorize direct calls to AWS services using IoT`: https://docs.aws.amazon.com/iot/latest/developerguide/authorizing-direct-aws.html
.. _`pygments #1909`: https://github.com/pygments/pygments/issues/1909
