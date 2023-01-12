#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quikly go to where you want to be.

Usage:
    quik <alias>
    quik add [--force] <alias> <path> 
    quik add <alias>
    quik --list
    quik get <alias>
    quik edit [--force] <alias> <new_path>
    quik remove <alias>
    quik --help | -h

Options:
    -h --help           Show this screen.
    --force             Ignore whether target directory exists.
    --list              List the existing aliases.
"""

import os
import os.path
import json
import sys
from internals.docopt import docopt
from internals.version import JSON_VERSION, QUIK_VERSION

class NoPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

NO_JSON_ENV_VAR = """Could not find quik.json.
Please make sure your QUIK_JSON environment variable is set up, and that the file exists."""
NO_JSON_VER = """Warning: quik.json does not have a version.
It's possible it's misformated."""
WRONG_JSON_VER = lambda given, expected: f"""Warning: expected version {expected} in quik.json, but got {given}.
A crash may be due to this."""
NO_ALIAS_IN_JSON = """Error: could not find `alias` property of quik.json.
Aborting."""
BAD_ALIAS_IN_JSON = """Error: `alias` property of quik.json is not a dictionary.
Please fix your quik.json.
Aborting."""
DUPLICATE_ALIAS_IN_JSON = lambda duplicate: f"""Warning: duplicate alias ({duplicate})
Ignoring second instance; you may have to fix quik.json manually."""
MISFORMATTED_ALIAS_IN_JSON = lambda alias: f"""Warning: misformatted alias in quick.json:
{alias}
Expected `alias name`: `directory`, but `directory` is not a string.
Ignoring this entry."""
BAD_PATH_IN_JSON = lambda alias, path: f"""Warning: alias {alias} points to non-existing directory
{path}
Please remove this alias, or change its path to a valid path."""
NEW_DIR_NO_EXIST = lambda short_dir, full_dir: f"""{short_dir} does not exist.
(Expanded as \"{full_dir}\")
Use --force to create an alias anyway."""
ALIAS_ALREADY_DEFINED = lambda alias, old_dir, new_dir: f"""Alias {alias} is already defined as
\"{old_dir}\"
Instead use
quik edit {alias} \"{new_dir}\" """
try:
    with NoPrint():
        print('→')
    def ALIAS_ASSIGN(alias, path):
        return f"\"{alias}\" → \"{path}\""
except UnicodeEncodeError:
    def ALIAS_ASSIGN(alias, path):
        return f"\"{alias}\" -> \"{path}\""
EDIT_NO_EXIST = lambda alias: f"""{alias} is not a defined alias.
Call `quik --list` for a list of defined aliases, or `quik add` to define a new alias."""
REMOVE_NO_EXIST = lambda alias: EDIT_NO_EXIST(alias) 
EDIT_BAD_PATH = lambda alias, path, full_path: f"""{path} does not exist.
Use --force if you want to set {alias}(*) to point to this directory anyway.
(*) Expanded to \"{full_path}\" """
EDIT_FEEDBACK = lambda alias, old, new: f"""Changed {alias} from
{ALIAS_ASSIGN(alias, old)}
to
{ALIAS_ASSIGN(alias, new)}"""
REMOVE_FEEDBACK = lambda alias, old: f"""Excluded {alias}, used to point to
{ALIAS_ASSIGN(alias, old)}"""
CD_NO_ALIAS = lambda alias: f"""{alias} is not defined.
Use `quik add` to add a new alias."""
CD_ALIAS_SUGGEST = lambda typo, suggestions: f"""{typo} is not defined.
Did you mean one of
{suggestions}
?"""


def err_print(msg):
    print(msg, file=sys.stderr)

def get_quik_json_loc():
    return os.environ.get("QUIK_JSON",
               os.path.join(os.path.dirname(__file__), "quik.json"))


def get_quik_json():
    """Get a dictionary-parsed version of the JSON file specifying the aliases.
    
    Returns:
        quik JSON as dictionary
    """
    # Check that quik.json exists, and load it into a json object
    quik_json_loc = get_quik_json_loc()
    if not os.path.exists(quik_json_loc):
        err_print(NO_JSON_ENV_VAR)
        exit(1)

    with open(quik_json_loc) as quik_json_io:
        quik_json = json.load(quik_json_io)

    return quik_json


def get_aliases(quik_json, warn=True):
    """Load the aliases in the JSON file.
    
    Arguments:
        quik_json   [dict] A parsed JSON file specifying the aliases, per the specification.

    Returns:
        Dictionary of aliases
    """
    # Check the version
    if "version" not in quik_json:
        err_print(NO_JSON_VER)
    elif quik_json["version"] != JSON_VERSION:
        err_print(WRONG_JSON_VER(quik_json["version"], JSON_VERSION))

    # Perform the parsing
    alias = {}
    if "alias" not in quik_json:
        if warn:
            err_print(NO_ALIAS_IN_JSON)
        exit(1)
    if type(quik_json["alias"]) is not dict:
        if warn:
            err_print(BAD_ALIAS_IN_JSON)
        exit(1)
    for json_alias in quik_json["alias"]:
        if json_alias in alias:
            if warn:
                err_print(DUPLICATE_ALIAS_IN_JSON(json_alias[0]))
            continue
        if type(quik_json["alias"][json_alias]) is not str:
            if warn:
                err_print(MISFORMATTED_ALIAS_IN_JSON(json_alias))
            continue

        alias_path = quik_json["alias"][json_alias]
        if not os.path.exists(alias_path):
            if warn:
                err_print(BAD_PATH_IN_JSON(json_alias, alias_path))
        alias[json_alias] = alias_path

    # Done
    return alias


if __name__ == '__main__':
    arguments = docopt(__doc__, version=f"quik {QUIK_VERSION}")

    quik_json_loc = get_quik_json_loc()
    quik_json = get_quik_json()

    # Load the aliases from the json
    alias = get_aliases(quik_json)

    # Aliases are loaded
    # Switch on operation mode
    if arguments['add']:
        # Register a new alias
        user_dir = arguments['<path>']
        if arguments['<path>']:
            directory = os.path.abspath(arguments['<path>'])
        else:
            directory = os.path.abspath(".")
        new_alias = arguments['<alias>']
        force = arguments['--force']

        # Don't allow non existing directories
        if not os.path.exists(directory) and not force:
            err_print(NEW_DIR_NO_EXIST(user_dir, directory))
            exit(1)

        # Check whether alias is already defined
        if new_alias in alias and not force:
            # Edge case; if adding with quik add <alias>, then
            # arguments['<path>'] = None; in this case, use a period instead
            if arguments['<path>'] is None:
                user_dir = "."
            else:
                user_dir = arguments['<path>']
            err_print(
                ALIAS_ALREADY_DEFINED(new_alias, alias[new_alias], user_dir))
            exit(1)

        # Add alias
        alias[new_alias] = directory

        # Give the user some feedback
        print(ALIAS_ASSIGN(new_alias, directory))

        # Write to json file
        quik_json["alias"] = alias
        with open(quik_json_loc, 'w') as quik_json_io:
            json.dump(quik_json, quik_json_io)

        # Done
        exit(0)
    elif arguments['--list']:
        # List all existing aliases
        for alias_name, alias_dir in alias.items():
            print(ALIAS_ASSIGN(alias_name, alias_dir))
        exit(0)
    elif arguments['get']:
        # Print an alias's path
        get = arguments['<alias>']
        if get not in alias:
            print('')
            exit(1)
        print(alias[get])
        exit(0)
    elif arguments['edit'] or arguments['remove']:
        # Edit an existing alias
        edit_alias = arguments['<alias>']
        if edit_alias not in alias:
            if arguments['edit']:
                err_print(EDIT_NO_EXIST(edit_alias))
            elif arguments['remove']:
                err_print(REMOVE_NO_EXIST(edit_alias))
            exit(1)

        if arguments['edit']:
            new_dir = arguments['<new_path>']
            new_dir_full = os.path.abspath(new_dir)
            if not os.path.exists(new_dir_full) and not arguments['--force']:
                err_print(EDIT_BAD_PATH(edit_alias, new_dir, new_dir_full))
                exit(1)

            # Set the alias to point to new directory and save
            used_to = alias[edit_alias]
            alias[edit_alias] = new_dir_full

            # Give the user some feedback
            print(EDIT_FEEDBACK(edit_alias, used_to, new_dir))

        elif arguments['remove']:
            used_to = alias[edit_alias]
            del alias[edit_alias]

            # Give the user some feedback
            print(REMOVE_FEEDBACK(edit_alias, used_to))
    
        # Save the changes and exit
        quik_json["alias"] = alias
        with open(quik_json_loc, 'w') as quik_json_io:
            json.dump(quik_json, quik_json_io)
        exit(0)
    else:
        # Normal operation (cd) mode
        cd_alias = arguments['<alias>']

        if cd_alias not in alias:
            # Maybe the user missed a key
            # If it's unambiguous, cd to that directory anyway
            compatible = [candidate for candidate in alias
                        if (candidate.startswith(cd_alias) or
                            candidate.endswith(cd_alias))]
            if len(compatible) == 1:
                cd_alias = compatible[0]
            else:
                if len(compatible) > 0:
                    suggestions = '\n'.join(' - ' + suggestion for suggestion in compatible)
                    err_print(CD_ALIAS_SUGGEST(cd_alias, suggestions))
                else:
                    err_print(CD_NO_ALIAS(cd_alias))
                exit(1)
        
        # The bash extension will handle it from here.
        print(f"+cd \"{alias[cd_alias]}\"")
        exit(0)
