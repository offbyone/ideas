"""
Pelican plugin to automatically extract social card images from articles.

This plugin:
- Looks for an explicit 'social_image' metadata field
- Falls back to extracting the first figure/image from the article content
- Provides a default fallback image (light/headshot.png)

Usage in article metadata:
    social_image: /images/my-hero-image.jpg

Or let it auto-detect from content.
"""

import re

from pelican import signals


def extract_image_from_content(content):
    """
    Extract the first image from article content.

    Supports both Markdown and reStructuredText image syntax.
    Returns the image path or None if no image found.
    """
    # Try to find reStructuredText figure directive
    rst_figure_match = re.search(r"\.\. figure::\s+\{static\}(/[^\s]+)", content)
    if rst_figure_match:
        return rst_figure_match.group(1)

    # Try to find Markdown image syntax
    md_image_match = re.search(r"!\[.*?\]\((?:\{static\})?(/images/[^\)]+)\)", content)
    if md_image_match:
        return md_image_match.group(1)

    # Try to find HTML img tags
    html_image_match = re.search(
        r'<img[^>]+src=["\'](?:\{static\})?(/images/[^"\']+)["\']', content
    )
    if html_image_match:
        return html_image_match.group(1)

    return None


def add_social_image(generator, metadata):
    """
    Add social_image to article metadata if not already present.
    """
    # If social_image is already set, we're done
    if "social_image" in metadata:
        return

    # Try to extract from content if available
    if "_content" in metadata:
        content = metadata.get("_content", "")
        extracted_image = extract_image_from_content(content)
        if extracted_image:
            metadata["social_image"] = extracted_image
            return

    # Fall back to the configured OPEN_GRAPH_IMAGE if set
    if generator.settings.get("OPEN_GRAPH_IMAGE") and "social_image" not in metadata:
        metadata["social_image"] = generator.settings["OPEN_GRAPH_IMAGE"]
        return


def add_social_image_to_article(article_generator, metadata):
    """Signal handler for article_generator_context."""
    add_social_image(article_generator, metadata)


def register():
    """Register the plugin with Pelican."""
    signals.article_generator_context.connect(add_social_image_to_article)
