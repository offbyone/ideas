#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import multiprocessing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz


@dataclass
class StyledLink:
    name: str
    link: str
    style: Optional[str] = None
    icon_style: Optional[str] = None

    def __post_init__(self):
        if self.style is None:
            self.style = self.name.lower()
        if self.icon_style is None:
            self.icon_style = f"fa-brands fa-{{ self.style }}"


@dataclass
class Social(StyledLink):
    network: Optional[str] = None

    def __post_init__(self):
        if self.network is None:
            self.network = self.name.lower()
        self.style = f"sc-{self.network}"
        self.icon_style = f"fa-brands fa-{self.network}"


AUTHOR = "Chris R"
AUTHOR_EMAIL = "offline@offby1.net"
SITENAME = "Ideas.Offby1"
DESCRIPTION = "Close Enough"
SITEURL = "//offby1.website"
# Use relative URLs during development. This is overridden in publishconf.py
RELATIVE_URLS = True

PATH = Path("content")

# photos plugin configuration
PHOTO_LIBRARY = Path(__file__).parent / "photos"
PHOTO_RESIZE_JOBS = max(multiprocessing.cpu_count(), 1)

PHOTO_WATERMARK_TEXT = "© Chris Rose"
PHOTO_EXIF_KEEP = True
PHOTO_EXIF_REMOVE_GPS = True
PHOTO_EXIF_COPYRIGHT = "CC-BY-NC-SA"
PHOTO_EXIF_COPYRIGHT_AUTHOR = "Chris Rose"

SITEMAP = {"format": "xml", "exclude": ["tag/", "category/"]}

TIMEZONE = "America/Los_Angeles"
TZ = pytz.timezone(TIMEZONE)
PUBLICATION_TIME = datetime.now(TZ)


DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('Jinja2', 'http://jinja.pocoo.org/'),
#          ('You can modify those links in your config file', '#'),)
LINKS = [
    StyledLink("CV", "/pages/cv.html", style="cv", icon_style="fa-solid fa-file"),
]

# Social widget
SOCIAL = (
    Social("Twitter", "https://twitter.com/offby1"),
    Social("Wandering.Shop", "https://wandering.shop/@offby1", network="mastodon"),
    Social("Github", "https://github.com/offbyone"),
    Social("Keybase", "https://keybase.io/offby1"),
)

DEFAULT_PAGINATION = 10

PLUGIN_PATHS = ["./plugins"]
PLUGINS = [
    "embed_tweet",
    "pelican_gist",
    "photos",
    "simple_footnotes",
    "sitemap",
    "tag_cloud",
    "webassets",
]

ARTICLE_URL = "posts/{slug}.html"
ARTICLE_SAVE_AS = "posts/{slug}.html"

DISPLAY_PAGES_ON_MENU = False

TEMPLATE_EXTENSIONS = [".html.j2", ".html"]

# THEME = 'monospace'
# THEME = 'pelican-elegant-1.3'
# THEME = 'pure-single'
THEME = "themes/offby1"
# THEME = "twenty"
THEME_STATIC_PATHS = ["static"]
# set the SASS load path
WEBASSETS_SOURCE_PATHS = [
    "static/css",
    "sass",
    "scss",
]

# find all node modules that contain min.js files and add thoes to the source paths
for p in Path("node_modules").resolve().glob("**/*min.js"):
    WEBASSETS_SOURCE_PATHS.append(str(p.parent))

WEBASSETS_CONFIG = [("SASS_LOAD_PATHS", [str(Path(__file__).parent.resolve() / "node_modules")])]
WEBASSETS_BUNDLES = [
    (
        "theme_js",
        (
            "js/fuji.js",
            "js/bigfoot.js",
            "jquery.magnific-popup.js",
        ),
        {
            "output": "js/fuji.min.js",
            "filters": ["closure_js"],
        },
    ),
    # Disabled - STILL - because for some reason this CSS doesn't apply in the site
    # ... but the one in base.html.j2 _does_. Why? Who the hell knows?
    # (
    #     "theme_css",
    #     ("fuji.scss", "bigfoot-default.scss", "magnific-popup.css"),
    #     {
    #         "output": "css/style.min.js",
    #         "filters": "scss",
    #         "depends": ("**/_*.scss",),
    #     },
    # ),
]

STATIC_PATHS = ["images", "extra"]

EXTRA_PATH_METADATA = {
    "extra/robots.txt": {
        "path": "robots.txt",
    },
    "extra/favicon.ico": {
        "path": "favicon.ico",
    },
}

FLICKR_API_KEY = "b6948f5853252a6c1310523f2e3b1faa"
FLICKR_USER = "11217428@N00"

THEMES_I_LIKE = [
    "svtble",
    "simple-bootstrap",
    "pelican-bootstrap3",
    "monospace",
    "irfan",
    "blueidea",
    "basic",
]

IGNORE_FILES = [".#&", "flycheck_*", "flymake_*"]

REPOSITORY_ROOT = f"file://{ Path(__file__).parent.resolve() }/{ PATH }"
