Title: Azureus Autostop Plugin 2.0
date: 2007-01-01 09:59
author: offby1
slug: azureus-autostop-plugin
status: published

| The purpose of this plugin is to help with people whose ISPs are anal-retentive
| about upload bandwidth usage, like mine is. Its purpose is to be a community-
| friendly implementation of an upload limiter. It will not permit upload cutoff
| at less than a 1.0 share ratio, but other than that it will disable uploads for
| a few ratios that are equal to or greater than that.

| The settings are, I hope, more or less self-explanatory. Feel free to comment on
| it at here.

The plugin itself can also be downloaded here:

  --------------------------------------- -----------------------------------------------
  MD5: c4930bdcf89781d07b395ef689dca743   [autostop-2.0.2.zip](/?dl=autostop-2.0.2.zip)

  --------------------------------------- -----------------------------------------------

\### Version History

| - 1.0.0
| - Version 1, just sorta works

| - 1.0.1
| - Fixed a stupid bug where the plugin.properties was not included in the build.

| - 2.0.0 Alpha 1
| - Support per-torrent download ratio specification.
| - Obligatory total rewrite.

| - 2.0.0 Alpha 2
| - [AZSTOP-4](http://offby1.no-ip.org:8080/browse/AZSTOP-4) - it helps if the download listener is actually initialized.
| - [AZSTOP-5](http://offby1.no-ip.org:8080/browse/AZSTOP-5) - fixed some message strings not being valid

| - 2.0.0 Alpha 3
| - [AZSTOP-6](http://offby1.no-ip.org:8080/browse/AZSTOP-6) - Fixed issue with multiple selections breaking the menu.

| - 2.0.0 Beta 1
| - [AZSTOP-8](http://offby1.no-ip.org:8080/browse/AZSTOP-8) - Fixed failure to check if a torrent was stopped before trying to stop it.

| - 2.0.0 Beta 2
| - [AZSTOP-13](http://offby1.no-ip.org:8080/browse/AZSTOP-13), [AZSTOP-14](http://offby1.no-ip.org:8080/browse/AZSTOP-14) - fixed incorrect start values for seed stop actions

| - 2.0.2
| - Oh, so much. Hopefully this works for you all.

\### Issue Tracking

If you find bugs, and I expect you will, or you want new features, I have an issue tracker for this plugin at [<http://offby1.no-ip.org:8080/browse/AZSTOP>](<http://offby1.doesntexist.com:8080/browse/AZSTOP>) (The URL is subject to change, so if you can't get to it at that address, check back here for new information)
