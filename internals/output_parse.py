#!/usr/bin/env python3
"""A bash helper file. You shouldn't be looking at this.

Usage:
    output_parse [options]

Options:
    --cd                Find the directory to change to.
    --output            Find the regular output.
    --complete=<cur>    Suggest completion for the currently typed text.
"""

import re
import sys
import shlex
from docopt import docopt
from itertools import chain


def get_input_text():
    return ''.join(x for x in sys.stdin)


class Graph:
    class Node:
        def __init__(self, name):
            self.name = name

    class MemoizedTree:
        def __init__(self, name):
            self.name = name

    def __init__(self, root):
        self.root = root
        self.memoized_trees = {}
        self.connection_graph = {root: []}

    def to_explicit(self, node):
        if type(node) is Graph.Node:
            return [node.name]
        elif type(node) is Graph.MemoizedTree:
            return self.memoized_trees[node.name]
        else:
            raise Exception(f"Tried to call to_explicit on object {node}")

    def memoize_tree(self, name, tree):
        self.memoized_trees[name] = tree

    def connect(self, this, that):
        if that in self.memoized_trees:
            self.connection_graph[this].append(Graph.MemoizedTree(that))
        else:
            self.connection_graph[this].append(Graph.Node(that))
        self.connection_graph.setdefault(that, [])

    def get_connections(self, name):
        return [y for x in self.connection_graph.get(name, []) for y in self.to_explicit(x)]


def suggest(suggestions):
    if len(suggestions) == 0:
        exit(1)
    print('\n'.join(suggestions), end='')
    exit(0)


if __name__ == '__main__':
    arguments = docopt(__doc__, version="output_parse 1.0")

    cmd_regex = re.compile(r"^\s*\!(?:cd) \"?(.+?)\"?\s*$\n?", re.MULTILINE)

    if arguments['--cd']:
        print(cmd_regex.search(get_input_text()).group(1).strip())
    elif arguments['--output']:
        print(cmd_regex.sub("", get_input_text()).strip())
    elif arguments['--complete'] is not None:
        try:
            words = shlex.split(arguments['--complete'])
        except ValueError:
            # Could not parse
            exit(1)

        # HACK: Include quik.py, which is in parent directory
        def aliases():
            import os
            import sys
            sys.path.append(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))))
            from quik import get_aliases, get_quik_json
            return list(get_aliases(get_quik_json()).keys())

        grammar_graph = Graph("root")
        grammar_graph.memoize_tree("aliases", [alias for alias in aliases()])
        grammar_graph.connect("root", "quik")
        grammar_graph.connect("quik", "aliases")
        grammar_graph.connect("quik", "add")
        grammar_graph.connect("quik", "--list")
        grammar_graph.connect("quik", "edit")
        grammar_graph.connect("quik", "remove")
        grammar_graph.connect("quik", "--help")
        grammar_graph.connect("quik", "-h")
        grammar_graph.connect("add", "--force")
        grammar_graph.connect("edit", "--force")
        grammar_graph.connect("remove", "aliases")

        if len(words) == 0 or words[0] != "quik":
            # That's weird... how are you invoking this?
            exit(1)

        candidates = grammar_graph.get_connections(words[-1])
        if len(candidates) > 0:
            suggest(candidates)
        elif len(words) > 1:
            candidates = [candidate \
                    for candidate in grammar_graph.get_connections(words[-2]) \
                    if candidate != words[-1] and candidate.startswith(words[-1])]
            suggest(candidates)
