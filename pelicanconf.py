#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Chris R'
AUTHOR_EMAIL = 'offline@offby1.net'
SITENAME = u'Ideas.Offby1'
DESCRIPTION = u'Close Enough'
SITEURL = '//ideas.offby1.net'

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('Jinja2', 'http://jinja.pocoo.org/'),
#          ('You can modify those links in your config file', '#'),)
LINKS = (
    ('Github', 'https://github.com/offbyone'),
)

# Social widget
SOCIAL = (
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = ['assets', 'pelican_gist', 'gravatar']

ARTICLE_URL = 'posts/{slug}.html'
ARTICLE_SAVE_AS = 'posts/{slug}.html'

DISPLAY_PAGES_ON_MENU = False

# THEME = 'monospace'
# THEME = 'pelican-elegant-1.3'
# THEME = 'pure-single'
THEME = 'Just-Read'

FLICKR_API_KEY = 'b6948f5853252a6c1310523f2e3b1faa'
FLICKR_USER = '11217428@N00'

THEMES_I_LIKE = ['svtble', 'simple-bootstrap', 'pelican-bootstrap3', 'monospace', 'irfan', 'blueidea', 'basic']

IGNORE_FILES = [".#&", "flycheck_*", "flymake_*"]
