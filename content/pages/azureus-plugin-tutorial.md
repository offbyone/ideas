Title: Azureus Plugin Tutorial v0.2
date: 2004-12-22 08:02
author: offby1
slug: azureus-plugin-tutorial
status: published

\[Azureus\](<http://azureus.sourceforge.net>) is my BitTorrent client of choice, but I\'ve found on occasion that its functionality is a bit lacking. However, fortunately for me it is extensible via plugins, which has enabled me to add my own functionality to it.

This is a brief tutorial on how to use the Azureus plugin interface to make a simple plugin that aggregates some basic information about your torrents and logs it. Some listeners are used, and some of the basic utilities for creating views and configuration pages are also included. Since this is my first tutorial, I\'m not sure it\'ll be adequate, but feel free to use this page\'s comment section to provide feedback on it and tell me how I went horribly, horribly wrong.

| \### Assumptions
| I assume a few things here, although I am trying to minimize them. However, I have not the time or energy to explain classpaths and jar building for every IDE, nor do I have any interest in teaching basic Java. If you need to know more about these things, there are other places to do so.

| \### Getting Started
| You\'ll need a few things in order to make your plugin. Since I use \[Eclipse\](<http://www.eclipse.org/>) for development, there is obviously going to be a bias towards the use of that tool. It\'s not perfect (I\'m still trying to get debugging working right) but for simple plugins it works well.

| \#### Build Environment (Eclipse)
| On the off chance you\'re not using it already, I recommend you download \[Eclipse\](<http://www.eclipse.org/>) to start with. Install it however you like.

| \#### Libraries (Azureus and SWT)
| You\'ll need the source code for Azureus, since at this time there is no pure Plugin SDK for it. This leads to a bit of confusion over what parts of the code to use, but I\'ll try clear that up. You can get the source \[here\](<http://azureus.sourceforge.net/download.php>) \-- download the source zip at the bottom of the page. This tutorial is based on the 2.2.0.0 code, but the parts I\'m using should be pretty basic across at least a few versions. Unzip the source zip into \[dev\]/Azureus_2.2.0.0_source (here\'s where the assumptions start \-- I\'ll be assuming a simple and clear folder layout for your files) Also download the actual Azureus jar from the above location, and install it wherever you like \-- you can use the jarfile from your existing Azureus installation, which is what I did. Although you may or may not need these for your plugin (for this tutorial it\'s not strictly necessary) it pays to have SWT(Standard Widget Toolkit) installed. Get it \[here\](<http://dev.eclipse.org/viewcvs/index.cgi/%7Echeckout%7E/platform-swt-home/main.html>) and unzip the source package into \[dev\]/swt-3.0.1-win32 (Note that I assume SWT v3.0.1 which is the release version as of this writing. The version number should remain more or less irrelevant as long as it begins with 3)

\### Eclipse Config

| \#### Libraries
| First thing you need to do with Eclipse (other IDEs are exercises left to the reader) is configure the above libraries. For each of them, you need open the Classpath Variables preferences page (Window-\>Preferences: Java -\> Build Path -\> Classpath Variables) and add the libraries:

\![Preferences Window\](<http://www.offlineblog.com/images/prefs.png>)

\![Classpath Preferences\](<http://www.offlineblog.com/images/classpath.png>)

You also have to add:

| - \`AZUREUS_SRC (\[dev\]/Azureus_2.2.0.0_source.zip)\`
| - \`SWT_LIB (\[dev\]/swt-3.0.1-win32/swt.jar)\`
| - \`SWT_SRC (\[dev\]/swt-3.0.1-win32/swtsrc.zip) \`

This assumes that you downloaded the source for SWT as well.

| \#### Project Layout
| Create a new Java project in Eclipse, and add \`AZUREUS_LIB\` and \`SWT_LIB\` to it as well (in the Libraries tab). If you wish to have javadoc popups and source code for the SWT/Azureus libraries, you have to add source attachments (the SRC variables were for this) to the jar files. Good luck with that! :) Also, in order to use the SWT you may or may not (depending on how you debug \-- I didn\'t need this) wish to copy the swt-awt-\* and swt-\* libraries (dll files, on windows) into the project root. My project layout defaults to putting all source files in a src/ subdirectory off of the project root, and this is what I\'ll assume. However, if it so happens that you do not do so, it\'s in fact \_easier\_ to export to a plugin jar. I have to jump through one extra hoop with my project layout. So I would recommend creating a flat project layout. However, I\'ll just assume that all of your source files are in \[src\]/\[stuff\] from here on out.

\### Down to Brass Tacks

| \#### plugin.properties
| The first thing that every plugin needs is a \_plugin.properties\_ file: The lines are as follows:

| 1. plugin.class: (\*REQUIRED\*) This is simply the base class of the plugin. This class must implement \`org.gudy.azureus2.plugins.Plugin\`.
| 2. plugin.name: (\*REQUIRED\*) At this time I\'m not 100% certain of the difference between this one and plugin.id, so I suggest that they both be the same for now.
| 3. plugin.langfile: This optional value indicates the package and name of the file to be used for internationalization. As far as the naming format goes, \"Messages\" is the basename, adding \`\_\[language\]\_\[country code\]\` onto it customizes it for local languages. Bear in mind, I have only worked in english, don\'t quote me on that format.
| 4. plugin.id: I assume that this must be unique, but I am not sure what its relation to plugin.name is, and as such I keep it the same.

\#### Messages.properties

The package I am using (\`edu.azureus.example\`) can be anything you want it to be, so long as you keep it in sync with the plugin.properties file.

| \#### plugin.java
| \*\*Download:\*\* \[plugin.java\](/code/plugin.java)

This is a skeleton of a plugin for logging status changes in torrents. It has a few features of immediate interest:

- Lines 3-8: Import statements

These are a subset of the plugin library imports. Assuming that you are using Eclipse, you shouldn\'t have to worry about these, it\'ll take care of it for you. However, I cannot assume that you\'re doing the right thing here ;)

- Line 10,11: Class declaration

As you can see, the class implements the \`org.gudy.azureus2.plugins.Plugin\`, \`org.gudy.azureus2.plugins.download.DownloadManagerListener\`, and \`org.gudy.azureus2.plugins.download.DownloadListener\` interfaces. These are the most basic of the lot, required for almost any operation on the torrent list.

- Lines 12-20: Property names

These constants identify values in \`Messages.properties\`. They are used for internationalization and string tables for the application.

The methods are, in order of importance:

- \`void initialize(PluginInterface)\`

This method initializes the plugin. What\'s going on in here is a bit complex, I\'ll get to that later.

- \`void downloadAdded(Download download)\`

This method is called whenever the downloadManager adds another download. All it is doing here is adding this plugin as a download listener for that download, which otherwise doesn\'t happen.

- \`void downloadRemoved(Download download)\`

This should be self-explanatory.

- \`void stateChanged(Download download, int old_state, int new_state)\`

The actual work takes place here, in this method inherited from \`DownloadListener.\` This method checks to see if the \`enabled\` property is set to true (See below) and if it is, logs the state change to the logger (Also, see below). \`Download\` has several constants regarding states beginning with \`ST\_\` and an array of names \`ST_NAMES\` that are used here.

- \`void positionChanged(Download download, int oldPosition, int newPosition)\`

We don\'t do anything with this in this example, but it would be used if you wanted to monitor the queue of downloads for changes in ordering.

| \#### initialize
| As promised, here\'s a rundown on what is going on in initialize()

- (line 43) First, we store the \`pluginInterface\` object for future use. Although nothing is done with it in this plugin, you may want subordinate classes to be able to get at it. We may also need it in other parts of this plugin class.
- (line 44) For convenience (and because I hate typing) I keep the \`localeUtilities\` referenced as well. This is necessary for any translates strings that you use manually,.
- (line 45) Set up the logger.

Note that log is a \`LoggerChannel\` object, which we assign by first getting the \`Logger\` for our plugin from the \`pluginInterface\`, and then a new channel which we can name whatever we like (although something at least a bit unique is probably a good idea here).

- (lines 47-51) Set up the plugin log viewer.

We use \`BasicPluginViewModel\` to set up a simple view for our plugin. This is gotten through the UI Manager of the \`pluginInterface\`, as should be pretty obious. The \`lu.getLocalisedMessage(BASENAME + \"name\")\` call is the basic format for all string use, this takes the property \`example.name\` from \`Messages.properties\` and uses that string. \`vm.getActivity()\` and \`vm.getProgress()\` calls disable elements of the view that we won\'t be needing for this plugin. You don\'t have to do anything else to make this view show up \-- by doing this you have already created the view and added it to the Plugins menu in Azureus.

- (lines 53-63) Set up the log listener.

Here, we add a \`LoggerChannelListener\` to the log we created above. Although we could do fancy things with it, there\'s not much point, and an anonymous class does the trick just as well. Either way, the listener must implement \`LoggerChannelListener\` at least, and the two methods it provides are pretty basic. In this instance, the listener just writes the message plus an end of line character to the \`LogArea\` of the basic view we created a moment ago. the \`LogArea\` is something that the basic view model provides, so don\'t worry about creating one.

- (lines 65-74) Configuration.

We create a \`BasicPluginConfigModel\` to act as a config page for our plugin. We use the UI manager for this, and give it a parent heading (\"plugins\", which you should always use for your plugins) and a lookup name for its own name (BASENAME + \"name\" in this case, but whatever property you want from your \`Messages.properties\` can be substituted here) that Azureus will use to place it in the preferences dialog. At this point, in fact, you have created a preference page (albeit a blank one) and it will already appear in the prefs dialog. Next, create the enabled parameter: call \`addBooleanParameter2\` (the 2 is, I assume, for the more modern versions. There is a version w/0 2 on it, but I believe that it is deprecated) with the ID of the name from your Messages file, a key to store the config value under (this MUST be unique \-- I recommend prefixing it with your plugin name as I have done here, and then making certain that you have no duplicate values for your key names) and the default value, a boolean parameter. After that, create the prefix string parameter: call \`addStringParameter2\` and the parameters are the same as \`addBooleanParameter2\` in general, although a string parameter using \`getLocalisedMessage\` is what the default calls for. Lastly, make the prefix\'s enabled state depend on the \`booleanParameter\` as in line 74.

- (line 76) Finally, we add this plugin as a \`downloadManagerListener\` and off we go!

\### Deployment

Deploying your plugin requires that you create a Jar file containing the classes, the plugin.properties file, and any ancillary files that the plugin requires. I do it by right-clicking on my \[src\] directory (your mileage will vary on this one depending on where you put the source code \-- q.v. my earlier comment on project layout) and selecting \"Export\" from the resulting menu. I then export to Jar with ONLY the \[src\] directory and nothing above it highlighted, and I place that jar file in \[azureus install dir\]/plugins/\[plugin name\], although you can call the latter directory whatever you want. Debugging is, however, not working out for me. If anyone knows of a way to debug plugins in a running instance of Azureus, I\'d love to know!

\### Gotchas

The plugin API for Azureus is not terribly well documented. Generally, though, if you stick to public methods of the pluginInterface and classes from the org.gudy.azureus2.plugins package tree, you\'re probably going to be okay. If you get stumped, you can post questions as comments to this page, and I\'ll try to answer them. Also, there\'s an IRC channel \[#azureus\](<irc://irc.freenode.net/azureus>) and the sourceforge plugin developer \[forum\]([http://sourceforge.net/forum/forum.php?forum\\\_id=377614](http://sourceforge.net/forum/forum.php?forum\_id=377614)) to try. Hopefully this helps!
