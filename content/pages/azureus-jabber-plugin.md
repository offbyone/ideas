Title: Azureus IM Notification Plugin
date: 2006-12-31 19:00
author: offby1
slug: azureus-jabber-plugin
status: published

| \## Instant Messaging Notifications 1.0.4
| Copyright(c) 2006 Chris Rose and AIMedia.
| (GPL, blah blah\...)

  --------------------------------------- -----------------------------------------------
  MD5: b2472fbeb47da6731a4873c39057ad0e   [azjabber-1.0.4.zip](/?dl=azjabber-1.0.4.zip)

  --------------------------------------- -----------------------------------------------

\### Purpose

| This plugin grew out of my frustration with headless Azureus instances, and
| never knowing when they were finished downloading torrents. This plugin will
| send you an instant message when a torrent starts, finishes, etc\...

\### Usage

| The plugin doesn't ship configured to work with your IM service out of the box,
| obviously, so it won't do too much until you enter your password and username
| into the \`Jabber Notifications\` plugin page in the Plugins section of the
| Azureus configuration dialog.

| At that point, you'll receive the notifications you'd expect from the UI. Note
| that not all notifications are fully supported at this time.

\#### Security Notice

| The password is stored in plain text in the configuration, regrettably -- I need
| to pass it through to the chat service, and I don't know any safer way to do that.
| At some point I'll allow the option of storing it in some simple hashed way, or
| to enter it on startup.

\### Limitations

It currently only supports google talk for notifications.

Not all notifications are implemented.

\### Contact

| The plugin has a page at [http://www.offlineblog.com/projects/azureus-jabber-plugin](http://www.offlineblog.com/projects/azureus-jabber-plugin)
| for comment. Bug reports can be entered here: [OffByOne JIRA](http://offby1.no-ip.org:8080/browse/AZIM)

\### Version History

| - 1.0
| - initial release
| - 1.0.1
| - UI enhancements in the configuration dialog
| - Fixed some potential error conditions during Azureus shutdown
| - 1.0.2
| - Renamed the plugin to 'azjabber' from 'com.aimedia.azjabber'
| - 1.0.3
| - Fixed a few NPE conditions in the logging of messages.
| - Added a button to access the plugin configuration from the log view.
| - 1.0.4
| - Added reconnection logic

| If you have not received this file either from [http://azureus.sourceforge.net/](http://azureus.sourceforge.net/)
| or [http://offlineblog.com/](http://offlineblog.com/) I would suggest that you do so, since anyone could
| have done anything with it. There will always be a current version at
| [http://www.offlineblog.com/?dl=azjabber-current.zip](http://www.offlineblog.com/?dl=azjabber-current.zip)

Enjoy!

\### Files

\#### Current Version

  --------------------------------------- -----------------------------------------------
  MD5: b2472fbeb47da6731a4873c39057ad0e   [azjabber-1.0.4.zip](/?dl=azjabber-1.0.4.zip)

  --------------------------------------- -----------------------------------------------

\#### Older Versions

  --------------------------------------- -----------------------------------------------
  MD5: b4a227990136c3ca693819a313f5362d   [azjabber-1.0.3.zip](/?dl=azjabber-1.0.3.zip)

  MD5: 6d74e971b15c4fc236248df845a69e96   [azjabber-1.0.2.zip](/?dl=azjabber-1.0.2.zip)

  MD5: 344d5fb26d749244cb712d153e2fb65a   [azjabber-1.0.1.zip](/?dl=azjabber-1.0.1.zip)

  MD5: 59e6573ef2627b2ffdd55ab718c7e1c9   [azjabber-1.0.0.zip](/?dl=azjabber-1.0.0.zip)
  --------------------------------------- -----------------------------------------------
