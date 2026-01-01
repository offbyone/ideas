---
title: Expose Your Tailnet Hosts as Ansible Facts
slug: tailnet-hosts-as-ansible-facts
date: 2025-06-01 08:02:42.139266
category: internet
tags:
  - tailscale
  - ansible
  - software
  - mastodon
  - infrastructure
  - wandering.shop
  - homelab
author: Chris Rose
email: offline@offby1.net
summary: Expose your Tailscale hosts as Ansible facts. Make peer node IPs and tags available in your playbooks
status: published
toot: "https://wandering.shop/@offby1/114608855854673274"
---
[Tailscale](https://tailscale.com) is an encrypted overlay network that "just works", so well that I have adopted it both for my homelab and for the infrastructure of [wandering.shop](https://wandering.shop). In the latter case, I've heavily used [Ansible](https://ansible.com) to make the infrastructure easy to replicate and manage.

Ansible makes information about your hosts available as ["facts"](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_vars_facts.html), which are expressed as a dictionary you can reference alongside other variables in your playbooks and roles. When building wandering.shop, I've often wanted to have access to information about other hosts in the tailent to craft configuration. To that end, I built a local tailnet facter. It does not depend on the Tailscale API, relying entirely on local information about nodes[ref]That has a consequence I'll explain below[/ref].

It reports several aspects of the current host (IP addresses and installed state) as well as peers. Because it can be useful, the current node is also included in the peer list.

```json
{
  "installed": true,
  "ip": "100.113.157.9",
  "ip_v4": "100.113.157.9",
  "ip_v6": "fd7a:115c:a1e0:ab12:4843:cd96:6271:9d09",
  "peers": {}
}
```

If tailscale is not available, it'll report just that `installed` is `false`.

### What does it look like?

Having the facts installed lets me perform variable lookups like this[ref]Something that I've seen repeatedly while using docker is that DNS is the _worst thing_ in Docker, and I've ended up with a lot of configuration using IP addresses. That might be a "me" problem[/ref]: 

```yaml
postgres_primary_tailnet_host: '{{ ansible_local["tailnet"]["peers"][db_primary_hostname]["ip"] }}'
```

In another case, I've used it to identify all peer nodes that are tagged with the `role-app` tag, to build a list of IP addresses to configure a reverse proxy. While this is slighly overcomplicated to account for peers without tags, the idea is hopefully clear?

```yaml
---
    - name: Process each peer
      ansible.builtin.include_tasks: process_peer.yml
      loop: "{{ ansible_local.tailnet.peers | dict2items }}"
      loop_control:
        loop_var: peer
---
# process_peer.yml
- name: Check if peer has tags and if tags is a list
  ansible.builtin.set_fact:
    has_tags: "{{ peer.value.tags is defined and peer.value.tags is iterable and peer.value.tags is not string }}"
  check_mode: false

- name: Check if peer has app tag
  ansible.builtin.set_fact:
    is_app_server: "{{ has_tags and 'tag:role-app' in peer.value.tags }}"
  check_mode: false
  when: has_tags | bool

- name: Add to app servers if it has the app tag
  ansible.builtin.set_fact:
    app_servers: "{{ app_servers + [peer] }}"
  check_mode: false
  when: is_app_server is defined and is_app_server | bool
```

### Installing the facts

```yaml
- name: install system dependencies
  package:
    name:
      # User tools
      - jq
  become: true
  
- ansible.builtin.file:
    path: /etc/ansible/facts.d
    state: directory
  become: true

- name: install the tailscale IP detection fact
  copy:
    src: discover-tailnet-ip.fact
    dest: /etc/ansible/facts.d/tailnet.fact
    mode: 0o755
    owner: root
  become: true
  register: tailnet_discovery

- name: refresh the local facts
  ansible.builtin.setup:
    filter: ansible_local
  when: tailnet_discovery.changed
```

### The fact code

```bash
#!/bin/bash

read -r -d '' peer_json_script <<-'EOF'
      [.Self] + [.Peer | to_entries[] | .value]
      | map(
          select(has("DNSName") and .DNSName !=)
          | {
              (.DNSName | sub("[.]$";)): {
                "ip": .TailscaleIPs[0],
                "ip_v4": .TailscaleIPs[0],
                "ip_v6": (if .TailscaleIPs[1] then .TailscaleIPs[1] else null end),
                "tags": (if has("Tags") then .Tags else [] end)
              }
          }
        )
      | add
EOF

get_peers() {
  tailscale status --self --json | jq "$peer_json_script"
}
if which tailscale >/dev/null 2>&1; then
  ip=$(tailscale ip -1)
  ip_v4=$(tailscale ip -4)
  ip_v6=$(tailscale ip -6)
  peers=$(get_peers)
  cat <<EOF
{
  "installed": true,
  "ip": "$ip",
  "ip_v4": "$ip_v4",
  "ip_v6": "$ip_v6",
  "peers": $peers
}
EOF
else
  cat <<EOF
{
  "installed" false,
}
EOF
fi
```

If you want to see the structure in detail, you can actually run this code on any machine that has bash and is in a tailnet:

```shell-session
$ bash ./roles/tailnet-host/files/discover-tailnet-ip.fact | head -n30
{
  "installed": true,
  "ip": "100.113.157.9",
  "ip_v4": "100.113.157.9",
  "ip_v6": "fd7a:115c:a1e0:ab12:4843:cd96:6271:9d09",
  "peers": {
  "void.mytailnet.ts.net": {
    "ip": "100.113.157.9",
    "ip_v4": "100.113.157.9",
    "ip_v6": "fd7a:115c:a1e0:ab12:4843:cd96:6271:9d09",
    "tags": []
  },
  "gb-mnc-wg-007.mullvad.ts.net": {
    "ip": "100.116.86.123",
    "ip_v4": "100.116.86.123",
    "ip_v6": "fd7a:115c:a1e0::c6b4:567b",
    "tags": [
      "tag:mullvad-exit-node"
    ]
  },
```

### Caveats

As I mentioned above, this does not depend on the Tailscale API at all, just on host-local data. One consequence of that is that the nodes that appear in this are only those where the host has access to them by ACL or grant. If there's no way to get traffic _to_ the other node, it won't appear in this list.

As you can also see above, exit nodes from mullvad are also included in the peer list, if the node you are running this on is configured to use that feature of Tailscale. You'll want to account for that, probably by filtering on the tailnet name either in the fact script itself, or in your Ansible code. Helpfully, those nodes are tagged for easy identification.
