---
title: Azureus Autocat Plugin 1.0.1
slug: azureus-autocat-plugin
date: "2006-09-03 21:42"
author: offby1
status: published
---
This is a simple support page for the Azureus Autocat plugin (linked on the Azureus page itself at [this location](http://azureus.sourceforge.net/plugin_details.php?plugin=autocat)).

I've discontinued the mailbox that was receiving support requests, because of excessive spam, so I'd prefer that you place support requests in the comments on this page. I should warn you, however, that the plugin does what I want it to at the moment, so I'm a bit slow to add new features. Which is not to say I won't, just\... well, I've been very, very lazy for the last year.

The plugin itself can also be downloaded here:

<div class="download">

MD5: 0bcff6c2b2864843c7d3773645e4a428

[autocat-1.2.0.zip](http://www.offlineblog.com/?dl=autocat-1.2.0.zip)

</div>

\## Version History

------------------------------------------------------------------------

| * 0.1 - initial release
| - Matched regular expressions to torrent file names

| * 1.0.0 - The good one
| - Rewrote the whole thing from scratch (well, almost)
| - New config file format (backwards compatible, so far)
| - Now has the ability to match torrents based on tracker URL as well
| (by popular request)
| * 1.0.1 - The better one
| - Fixed a bug where the config file would not be created if it didn't
| already exist. For me, this didn't really happen, since I already
| had one. Sorry, guys.
| - There were some missing messages in the Messages file. Added those that
| I knew about.
| * 1.2.0 - Other things are improved
| - The rules are now stored as properties, making it (slightly) easier to
| modify them by hand without the UI.
| - Autocat no longer overwrites user-selected categories if that is the desired
| behaviour ([ACAT-5](http://offby1.no-ip.org:8080/browse/ACAT-5))

\## Issue Tracking

| If you have a bug or feature request, feel free to submit an issue report at my issue tracker:
| [http://offby1.no-ip.org:8080/browse/ACAT](http://offby1.no-ip.org:8080/browse/ACAT) (URL subject to change, always use this page to access it)
