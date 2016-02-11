#!/usr/bin/env python
from __future__ import print_function, absolute_import
from xml.etree import ElementTree as ET
import click
import click.types

NS = dict(
    excerpt="http://wordpress.org/export/1.2/excerpt/",
    content="http://purl.org/rss/1.0/modules/content/",
    wfw="http://wellformedweb.org/CommentAPI/",
    dc="http://purl.org/dc/elements/1.1/",
    wp="http://wordpress.org/export/1.2/",
)

WP_KEYS = (
    'post_id',
    'post_date',
    'post_date_gmt',
    'comment_status',
    'ping_status',
    'post_name',
    'status',
    'post_parent',
    'menu_order',
    'post_type',
    'post_password',
    'is_sticky',
)

WP_COMMENT_KEYS = (
    'comment_id',
    'comment_author',
    'comment_author_email',
    'comment_author_url',
    'comment_author_IP',
    'comment_date',
    'comment_date_gmt',
    'comment_content',
    'comment_approved',
    'comment_type',
    'comment_parent',
    'comment_user_id',
)

@click.argument("output-dir", type=click.types.Path(exists=True, dir_okay=True, file_okay=True))
@click.argument("source-file", type=click.types.File())
@click.option("--overwrite/--no-overwrite", default=False)
@click.option("--dry-run/--no-dry-run", default=False)
@click.command()
def do_import(source_file, output_dir, overwrite=False, dry_run=False):
    print("source:", source_file)
    print("dest:", output_dir)

    if dry_run:
        post_writer = stdout_writer
    else:
        post_writer = file_writer

    et = ET.parse(source_file)
    #et = ET.fromstring(source_file.read())
    root = et.getroot()

    posts = root.findall("item")
    print(root)

def stdout_writer(post):
    click.echo(post)

def file_writer(post):
    click.echo(post)

def item_comments(item):
    return [xml_comment_to_comment(comment) for comment in item.findall('{%s}comment' % NS['wp'])]

def xml_comment_to_comment(item):
    _wp = lambda k: item.find('{%s}%s' % (NS['wp'], k)).text
    metadata = lambda: {
        i.find('{%s}meta_key' % NS['wp']).text: i.find('{%s}meta_value' % NS['wp']).text \
        for i in item.findall('{%s}commentmeta' % NS['wp'])
    }

    comment_keys = dict()
    for k in WP_COMMENT_KEYS:
        comment_keys[k] = _wp(k)

    comment_keys['metadata'] = metadata()

    return comment_keys

def item_to_post(item):
    _t = lambda k: item.find(k).text
    _wp = lambda k: item.find('{%s}%s' % (NS['wp'], k)).text
    categories = lambda: [{
        'domain': i.attrib['domain'],
        'nicename': i.attrib['nicename'],
        'category': i.text,
    } for i in item.findall('category')]

    metadata = lambda: {
        i.find('{%s}meta_key' % NS['wp']).text: i.find('{%s}meta_value' % NS['wp']).text \
        for i in item.findall('{%s}postmeta' % NS['wp'])
    }

    post_keys = dict(
        title=_t('title'),
        old_link=_t('link'),
        pub_date=_t('pubDate'),
        creator=_t('{%s}creator' % NS['dc']),
        guid=_t('guid'),
        description=_t('description'),
        content=_t('{%s}encoded' % NS['content']),
        excerpt=_t('{%s}encoded' % NS['excerpt']),
    )
    for k in WP_KEYS:
        post_keys[k] = _wp(k)

    post_keys['categories'] = categories()
    post_keys['metadata'] = metadata()
    post_keys['comments'] = item_comments(item)

    return post_keys

if __name__ == '__main__':
    do_import()
