# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal blog website built with [Pelican](https://getpelican.com/), a Python-based static site generator. The site is deployed to AWS S3 with CloudFront for distribution.

- Content is written in Markdown (.md) and reStructuredText (.rst) 
- Uses a custom theme ("offby1")
- Includes custom plugins for social media integration
- Deploys to AWS S3/CloudFront

## Development Commands

### Core Commands

```bash
# Start development server with live reload
just serve

# Build the site with development settings
just build

# Build with production settings
just generate

# Build and deploy to S3 + invalidate CloudFront cache
just publish

# Create a new blog post
just new_post
```

### Dependency Management

```bash
# Compile dependencies
just compile-deps

# Install dependencies 
just install-deps

# Both compile and install dependencies
just deps

# Update dependencies
just update-deps
```

### Content Management

```bash
# Generate gallery metadata for photos
uv run invoke photo-gallery-gen --location=path/to/gallery

# List all used tags
uv run invoke list-tags

# List all categories
uv run invoke list-categories
```

## File Structure

- `content/`: All blog content
  - `posts/`: Blog posts
  - `pages/`: Static pages
  - `images/`: Image files
  - `extra/`: Extra files like robots.txt, favicon.ico
- `themes/offby1/`: Custom theme
- `plugins/`: Custom Pelican plugins
- `pelicanconf.py`: Development settings
- `publishconf.py`: Production settings

## Content Creation

### Blog Posts

New posts should follow this format (Markdown):

```markdown
Title: Post Title
Slug: post-title-slug
Date: YYYY-MM-DDTHH:MM:SS
Tags: tag1, tag2
Category: CATEGORY
Author: Chris Rose
Email: offline@offby1.net
Status: draft
Summary: Brief summary
```

### Photo Galleries

Photo galleries should have:
- Image files
- `captions.txt`: Photo captions
- `exif.txt`: EXIF metadata

## Build and Deployment

The site uses:
- `uv` for Python dependency management
- `just` as a command runner
- `invoke` for more complex tasks
- AWS S3 for hosting
- CloudFront for distribution

The deployment workflow:
1. Build site with production settings
2. Upload to S3 bucket `ideas.offby1.net`
3. Invalidate CloudFront distribution to refresh caches

## Code Style

- Python code follows `ruff` formatting style
- Follows modern Python practices (pathlib over os, etc.)
- When possible, make minimal changes to maintain compatibility