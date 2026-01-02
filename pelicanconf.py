#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os
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
            self.icon_style = "fa-brands fa-{ self.style }"


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
DESCRIPTION = "This is such an <em>extremely</em> specific complaint"
SITEURL = "//offby1.website"
# Use relative URLs during development. This is overridden in publishconf.py
RELATIVE_URLS = True

PATH = Path("content")

# photos plugin configuration
PHOTO_LIBRARY = Path(__file__).parent / "photos"
# during development, the pelican listener and this feature are incompatible
PHOTO_RESIZE_JOBS = 1

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
    StyledLink("CV", "/cv.html", style="cv", icon_style="fa-solid fa-image-portrait"),
    StyledLink("Now", "/now.html", style="now", icon_style="fa-solid fa-clock"),
    StyledLink(
        "Tools", "/defaults.html", style="tools", icon_style="fa-solid fa-toolbox"
    ),
]

# Social widget
SOCIAL = (
    Social("Wandering.Shop", "https://wandering.shop/@offby1", network="mastodon"),
    Social("Github", "https://github.com/offbyone"),
    Social("Bluesky", "https://bsky.app/profile/offby1.net"),
)

DEFAULT_PAGINATION = 10

PLUGIN_PATHS = ["./plugins"]
PLUGINS = [
    "extract_linked_metadata",
    "pelican_edit_url",
    "pelican_embed_microblog",
    "pelican_gist",
    "pelican_redirect",
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

WEBASSETS_CONFIG = [
    ("SASS_LOAD_PATHS", [str(Path(__file__).parent.resolve() / "node_modules")]),
    # Silence SASS deprecation warnings from dependencies like @primer/css
    # These use deprecated @import syntax which we can't control
    ("SASS_BIN", "sass"),
    (
        "SASS_EXTRA_ARGS",
        (
            "--silence-deprecation=import",
            "--silence-deprecation=global-builtin",
        ),
    ),
]
WEBASSETS_BUNDLES = [
    (
        "theme_js",
        (
            "js/fuji.js",
            "js/bigfoot.js",
            "jquery.magnific-popup.js",
            "js/adblocker.js",
            # We don't include federated-comments.js here because it's loaded conditionally
        ),
        {
            "output": "js/fuji.min.js",
            "filters": ["jsmin"],
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
    "extra/.well-known/webfinger": {
        "path": ".well-known/webfinger",
    },
    "extra/js/federated-comments.js": {
        "path": "js/federated-comments.js",
    },
}

FLICKR_API_KEY = "b6948f5853252a6c1310523f2e3b1faa"
FLICKR_USER = "11217428@N00"

# PAGE_URL = "{slug}.html"
PAGE_SAVE_AS = "{slug}.html"
# PAGE_URL = "{slug}.html"

CONTENT_REDIRECT_CONFIGURATION = [
    {
        "PAGE_URL": "pages/{slug}.html",
    }
]

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

REPOSITORY_ROOT = f"file://{Path(__file__).parent.resolve()}/{PATH}"
EDIT_CONTENT_URL = "https://github.com/offbyone/ideas/edit/main/{file_path}"

MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.admonition": {},
        "markdown.extensions.codehilite": {"css_class": "highlight"},
        "markdown.extensions.extra": {},
        "markdown.extensions.meta": {},
        "markdown.extensions.toc": {
            "title": "Table of Contents",
        },
    },
    "output_format": "html5",
}

# MyST Reader configuration
MYST_READER = {
    "myst_enable_extensions": {
        "linkify",  # Auto-detect links
        "colon_fence",  # Enable ::: directive syntax for dropdowns
    },
    "myst_disable_syntax": [],  # Don't disable any syntax
    "myst_heading_anchors": 3,  # Add anchors to headings
}

if "IDEAS_EMIT_TIMING" in os.environ:
    import sqlite3
    import time

    from pelican import signals
    from pelican.generators import Generator

    timing_db = "timings.sqlite3"
    Path(timing_db).unlink(missing_ok=True)
    con = sqlite3.connect(timing_db)
    cur = con.cursor()
    cur.execute("CREATE TABLE timings(path, start, end)")

    @signals.article_generator_preread.connect
    def start_time(generator: Generator):
        with sqlite3.connect(timing_db) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO timings (path, start) VALUES (?, ?)",
                (generator.path, int(time.perf_counter() * 1000)),
            )

    @signals.article_generator_context.connect
    def stop_time(generator: Generator, metadata):
        with sqlite3.connect(timing_db) as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE timings SET end=? WHERE path = ?",
                (int(time.perf_counter() * 1000), generator.path),
            )
