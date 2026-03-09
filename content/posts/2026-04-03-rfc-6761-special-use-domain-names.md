---
title: TIL about RFC 6761 "Special-Use" domain names
slug: rfc-6761-special-use-domain-names
date: 2026-04-03T09:16:13.851773
category: til
tags:
  - til
author: Chris Rose
email: offline@offby1.net
summary: How to use .localhost for fun and profit
status: published
---

I had formed a loose memory at work of having had to install some kind of special software so that all of the `.localhost` hostnames would resolve for development, but it turns out that they are actually a special use domain name, per [RFC 6761]((https://www.rfc-editor.org/rfc/rfc6761#section-6.3).

They have special treatment in curl and browsers, and have for years.
