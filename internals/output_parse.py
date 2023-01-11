#!/usr/bin/env python3
"""A helper file to parse output. You shouldn't be looking at this.

Usage:
    output_parse --cd
    output_parse --output
    output_parse --complete=<cur> [--alias=<alias>]

Options:
    --cd                Find the directory to change to.
    --output            Find the regular output.
    --complete=<cur>    Suggest completion for the currently typed text.
    --alias=<alias>     Hint that the completion is being called for a command alias.
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
        self.aliases = {}

    def to_explicit(self, node):
        if type(node) is Graph.Node:
            return [node.name]
        elif type(node) is Graph.MemoizedTree:
            return self.memoized_trees[node.name]
        else:
            raise Exception(f"Tried to call to_explicit on object {node}")

    def memoize_tree(self, name, tree):
        self.memoized_trees[name] = tree

    def alias(self, name, alias):
        self.aliases[alias] = name

    def connect(self, this, that):
        if that in self.aliases:
            self.connect(self, this, self.aliases[that])
        else:
            if that in self.memoized_trees:
                self.connection_graph.setdefault(this, []).append(Graph.MemoizedTree(that))
            else:
                self.connection_graph.setdefault(this, []).append(Graph.Node(that))
            self.connection_graph.setdefault(that, [])

    def get_connections(self, name):
        if name in self.aliases:
            return self.get_connections(self.aliases[name])
        else:
            return [y for x in self.connection_graph.get(name, [])
                        for y in self.to_explicit(x)]

    def contains(self, name):
        if name in self.aliases:
            return self.contains(self.aliases[name])
        else:
            return (name in self.connection_graph
                    or any(name in tree for tree in self.memoized_trees))


def suggest(suggestions):
    if len(suggestions) == 0:
        exit(1)
    print('\n'.join(suggestions), end='')
    exit(0)


if __name__ == '__main__':
    arguments = docopt(__doc__, version="output_parse 3.0")

    cmd_regex = re.compile(r"^\s*\+(?:cd) \"?(.+?)\"?\s*$\n?", re.MULTILINE)

    if arguments['--cd']:
        match_obj = cmd_regex.search(get_input_text())
        if match_obj is None:
            # Exit with no output
            pass
        else:
            print(match_obj.group(1).strip())
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
            return list(get_aliases(get_quik_json(), warn=False).keys())

        grammar_graph = Graph('root')
        grammar_graph.memoize_tree('aliases', [alias for alias in aliases()])
        grammar_graph.memoize_tree('cmds',
                ['add', '--list', 'get', 'edit', 'remove', 
                    '--help', '-h'])
        grammar_graph.connect('root', 'aliases')
        grammar_graph.connect('root', 'cmds')
        grammar_graph.connect('add', '--force')
        grammar_graph.connect('get', 'aliases')
        grammar_graph.connect('edit', '--force')
        grammar_graph.connect('--force', 'aliases')
        grammar_graph.connect('edit', 'aliases')
        grammar_graph.connect('remove', 'aliases')
        
        grammar_graph.alias('root', 'quik')
        if arguments['--alias'] is not None:
            grammar_graph.alias('root', arguments['--alias'])

        # "Edge" case; doing something like
        #  quik add<tab>
        # results in
        #  quik --force
        # because the autocomplete looks at add and returns --force,
        # but bash reads this as "replace add by --force"
        # so if the word matches something in the graph already, 
        # just return that.
        if (len(words) > 0 and 
                not arguments['--complete'].endswith(' ') and 
                grammar_graph.contains(words[-1])):
            suggest([words[-1]])

        if len(words) > 0:
            candidates = grammar_graph.get_connections(words[-1])
        else:
            candidates = grammar_graph.get_connections('root')
        if len(candidates) > 0:
            suggest(candidates)
        elif len(words) > 1:
            candidates = [candidate \
                    for candidate in grammar_graph.get_connections(words[-2]) \
                    if candidate != words[-1] and candidate.startswith(words[-1])]
            suggest(candidates)
