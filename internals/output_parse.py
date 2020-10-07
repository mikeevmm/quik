#!/usr/bin/env python3
"""A bash helper file. You shouldn't be looking at this.

Usage:
    output_parse [options]

Options:
    --cd        Find the directory to change to.
    --output    Find the regular output.
    --complete  Produce an autocomplete wordlist.
"""

import re
import sys
from docopt import docopt


def get_input_text():
    return ''.join(x for x in sys.stdin)


if __name__ == '__main__':
    arguments = docopt(__doc__, version="output_parse 1.0")

    cmd_regex = re.compile(r"^\s*\!(?:cd|complete) \"?(.+?)\"?\s*$\n?", re.MULTILINE)
    
    if arguments['--cd']:
        print(cmd_regex.search(get_input_text()).group(1).strip())
    elif arguments['--output']:
        print(cmd_regex.sub("", get_input_text()).strip())
    elif arguments['--complete']:
        # Some ugly hacks so we can import quik.py
        import sys
        import os.path
        sys.path.append(
            os.path.abspath(os.path.join(
                os.path.dirname(__file__), os.path.pardir)))
        import quik
        aliases = quik.get_aliases(quik.get_quik_json())
        print(' '.join(aliases.keys()))
