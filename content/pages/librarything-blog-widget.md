---
title: LibraryThing Blog Widget
slug: librarything-blog-widget
date: "2006-04-06 18:27"
author: offby1
status: published
---
There's not a lot to show, here. This widget will show you a selection of books from LibraryThing in the sidebar of your WordPress weblog.

Get it here:
[widget-librarything.php](http://svn.wp-plugins.org/widget-librarything/tags/latest/widget-librarything.php)

There's a sample of it over to the right. I'd document it more, but at this time I'm just too lazy.

<details>
<summary>Source Code</summary>

```php
<?php
/*
Plugin Name: Library Thing widget
Description: Adds a sidebar widget to display your LibraryThing widget
Author: Chris Rose
Version: 1.0
Author URI: http://www.offlineblog.com/
*/

// Put functions into one big function we'll call at the plugins_loaded
// action. This ensures that all required plugin functions are defined.
function widget_librarything_init() {

	// Check for the required plugin functions. This will prevent fatal
	// errors occurring when you deactivate the dynamic-sidebar plugin.
	if ( !function_exists('register_sidebar_widget') )
		return;

	// This is the function that outputs our little Google search form.
	function widget_librarything($args) {
		
		// $args is an array of strings that help widgets to conform to
		// the active theme: before_widget, before_title, after_widget,
		// and after_title are the array keys. Default tags: li and h2.
		extract($args);

		// Each widget can store its own options. We keep strings here.
		$options = get_option('widget_librarything');
		$title = $options['title'];
	    $supported_lt_widget_version = 2;
	    // LibraryThing widget options
		$number_of_books = $options['number_of_books'];
	    //$show_covers = $options['show_covers'];
		$show_covers = 'small';
        $lt_user = $options['lt_user'];
	    $what_to_show = 'random';
	    $text_to_show = 'title';
	    $tags_to_show = 'all';
	    $use_lt_css = 1;
	    $lt_style_id = 1;
	    
	    $url_params = $options['url_params'];
	    if ( $url_params == "" ) {
	    
	    $url_params = 'reporton=' . $lt_user 
	            . '&show=' . $what_to_show . '&header=0&num=' . $number_of_books 
	            . '&covers=' . $show_covers . '&text=' . $text_to_show 
	            . '&tag=' . $tags_to_show . '&css=' . $use_lt_css 
	            . '&style=' . $lt_style_id . '&version=' . $supported_lt_widget_version;
	    }
	    
		// These lines generate our output. Widgets can be very complex
		// but as you can see here, they can also be very, very simple.
		echo $before_widget . $before_title . $title . $after_title;
		$url_parts = parse_url(get_bloginfo('home'));
	        echo '<script language="javascript" type="text/javascript"';
	        echo 'src="http://www.librarything.com/jswidget.php?' . $url_params . '">';
		echo '</script>';
		echo $after_widget;
	}

	// This is the function that outputs the form to let the users edit
	// the widget's title. It's an optional feature that users cry for.
	function widget_librarything_control() {

		// Get our options and see if we're handling a form submission.
		$options = get_option('widget_librarything');
		if ( !is_array($options) )
			$options = array('title'=>'Some of my Books', 
					 'lt_user'=>'', 
					 'number_of_books'=>5,
					 'url_params'=>'');
					 
		if ( $_POST['librarything-submit'] ) {

			// Remember to sanitize and format use input appropriately.
			$options['title'] = strip_tags(stripslashes($_POST['librarything-title']));
			$options['lt_user'] = strip_tags(stripslashes($_POST['librarything-lt_user']));
			$options['number_of_books'] = strip_tags(stripslashes($_POST['librarything-number_of_books']));
			$options['url_params'] = strip_tags(stripslashes($_POST['librarything-url_params']));
			update_option('widget_librarything', $options);
		}

		// Be sure you format your options to be valid HTML attributes.
		$title = htmlspecialchars($options['title'], ENT_QUOTES);
		$lt_user = htmlspecialchars($options['lt_user'], ENT_QUOTES);
		$number_of_books = htmlspecialchars($options['number_of_books'], ENT_QUOTES);
		$url_params = htmlspecialchars($options['url_params'], ENT_QUOTES);
		
		// Here is our little form segment. Notice that we don't need a
		// complete form. This will be embedded into the existing form.
		echo '<p style="text-align:right;"><label for="librarything-title">Section title: <input style="width: 200px;" id="librarything-title" name="librarything-title" type="text" value="'.$title.'" /></label></p>';
		echo '<p style="text-align:right;"><label for="librarything-lt_user">User name: <input style="width: 200px;" id="librarything-lt_user" name="librarything-lt_user" type="text" value="'.$lt_user.'" /></label></p>';
		echo '<p style="text-align:right;"><label for="librarything-number_of_books">Number of Books: <input style="width: 200px;" id="librarything-number_of_books" name="librarything-number_of_books" type="text" value="'.$number_of_books.'" /></label></p>';
		echo '<p style="text-align:right;"><labem for="librarything-url_params">ADVANCED: URL parameters: <input style="width: 350px;" id="librarything-url_params" name="librarything-url_params" type="text" value="' . $url_params . '" /> </label></p>';
		echo '<input type="hidden" id="librarything-submit" name="librarything-submit" value="1" />';
	}
	
	// This registers our widget so it appears with the other available
	// widgets and can be dragged and dropped into any active sidebars.
	register_sidebar_widget('LibraryThing Books', 'widget_librarything');

	// This registers our optional widget control form. Because of this
	// our widget will have a button that reveals a 300x100 pixel form.
	register_widget_control('LibraryThing Books', 'widget_librarything_control', 600, 140);
}

// Run our code later in case this loads prior to any required plugins.
add_action('plugins_loaded', 'widget_librarything_init');

?>
```

</details>

:::{note}
This is a note
:::
