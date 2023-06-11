#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = "https://offby1.website"
RELATIVE_URLS = False

FEED_DOMAIN = SITEURL
FEED_MAX_ITEMS = 15
FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"
TAG_FEED_ATOM = "feeds/tag-{slug}.atom.xml"

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

GOOGLE_ANALYTICS = "UA-55657377-1"

DEFAULT_METADATA = {
    "status": "draft",
}

# for publication, let's really hammer the jobs.
PHOTO_RESIZE_JOBS = max(multiprocessing.cpu_count(), 1)

_repository = os.environ.get("GITHUB_REPOSITORY", "offbyone/ideas")
_tree = os.environ.get("GITHUB_SHA", "main")
REPOSITORY_ROOT = f"https://github.com/{_repository}/tree/{_tree}/content"
