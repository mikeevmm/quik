#!/usr/bin/env python3
"""A bash helper file. You shouldn't be looking at this.

Usage:
    output_parse [options]

Options:
    --cd        Find the directory to change to.
    --output    Find the regular output.
"""

import re
import sys
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version="output_parse 1.0")

    input_txt = ''.join(x for x in sys.stdin)
    cd_regex = re.compile(r"^\s*\!cd \"?(.+?)\"?\s*$\n?", re.MULTILINE)
    
    if arguments['--cd']:
        print(cd_regex.search(input_txt).group(1).strip())
    elif arguments['--output']:
        print(cd_regex.sub("", input_txt).strip())