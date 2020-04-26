#!/usr/bin/env python
import os
import argparse
import docutils
import requests
import json
import pathlib
from datetime import datetime

import docutils.nodes
import docutils.parsers.rst
import docutils.utils

class Visitor(docutils.nodes.NodeVisitor):

    def __init__(self, doc, debug):
        super().__init__(doc)
        self.debug = debug

    def visit_reference(self, node: docutils.nodes.Node) -> None:
        if self.debug:
            print("--> reference: ", node.pformat())
            print(node.children)
            print(node.parent.children)

    def depart_reference(self, node: docutils.nodes.Node) -> None:
        if self.debug:
            print("<--- reference")

    def visit_Text(self, node: docutils.nodes.Node) -> None:
        node_text = node.astext()
        if "http" in node_text:
            # look for markdown; if we hit this, we've gotta look at siblings too
            if "](" in node_text:
                all_sibs = node.parent.children
                this_index = all_sibs.index(node)
                left, right = all_sibs[this_index - 1], all_sibs[this_index + 1]
                print(f"markdown link nodes: {left}{node_text}{right}")

            else:
                print(f"raw link node: {node}")

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        visit_method = node.__class__.__name__

        if self.debug:
            try:
                print(f"self.{visit_method}")
            except AttributeError:
                print(node)

def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(components=components).get_default_values()
    document = docutils.utils.new_document('<rst-doc>', settings=settings)
    parser.parse(text, document)
    return document

def fix_markup(path: pathlib.Path, debug: bool = False) -> None:
    print(path)
    doc = parse_rst(path.read_text(encoding="utf-8"))
    visitor = Visitor(doc, debug)
    doc.walk(visitor)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("fixer")
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--basedir", "-d", default="content")
    parser.add_argument("single_file", nargs="?")

    opts = parser.parse_args()

    if opts.single_file:
        fix_markup(pathlib.Path(opts.single_file), opts.debug)
    else:
        for dirpath, dirnames, filenames in os.walk(opts.base_dir):
            for name in filenames:
                if not name.endswith(".rst"):
                    continue
                
                fix_markup(pathlib.Path(dirpath) / name, opts.debug)



