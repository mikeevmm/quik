#!/usr/bin/env python3
"""Quikly go to where you want to be.

Usage:
    quik <alias>
    quik add [--force] <directory> <alias>
    quik --list
    quik edit ((--change=<new> [--force]) | --remove) <alias>
    quik --help | -h

Options:
    -h --help           Show this screen.
    --force             Ignore whether target directory exists.
    --list              List the existing aliases.
    --change=<new>      Change an alias to a new directory.
    --remove            Remove the given alias.
"""

import os
import os.path
import json
from internals.docopt import docopt

EXPECTED_JSON_VERSION = 1.0

if __name__ == '__main__':
    arguments = docopt(__doc__, version="quik 1.0")

    # Check that quik.json exists, and load it into a json object
    quik_json_loc = os.environ.get("QUIK_JSON",
                                   os.path.join(os.path.basename(__file__), "quik.json"))

    if not os.path.exists(quik_json_loc):
        print("Could not find quik.json.")
        print("Please make sure your QUIK_JSON environment variable is " +
              "set up, and that the file exists.")
        exit(1)

    with open(quik_json_loc) as quik_json_io:
        quik_json = json.load(quik_json_io)

    # Check the version
    if "version" not in quik_json:
        print("Warning: quik.json does not have a version.")
        print("It's possible it's misformated.")
    elif quik_json["version"] != EXPECTED_JSON_VERSION:
        print(f"Warning: expected version {EXPECTED_JSON_VERSION} " +
              f"in quik.json, but got {quik_json['version']}.")
        print("A crash may be due to this.")

    # Load the aliases from the json
    alias = {}
    if "alias" not in quik_json:
        print("Error: could not find `alias` property.")
        print("Aborting.")
        exit(1)
    if type(quik_json["alias"]) is not dict:
        print("Error: `alias` property is not a dictionary.")
        print("Please fix your quik.json.")
        print("Aborting.")
        exit(1)
    for json_alias in quik_json["alias"]:
        if json_alias in alias:
            print("Warning: duplicate alias ({json_alias[0]})")
            print("Ignoring second instance; you may have to fix quik.json manually.")
            continue
        if type(quik_json["alias"][json_alias]) is not str:
            print("Warning: misformatted alias in quick.json:")
            print(json_alias)
            print("Expected `alias name`: `directory`, but `directory` is not a string.")
            print("Ignoring this entry.")
            continue

        alias_path = quik_json["alias"][json_alias]
        if not os.path.exists(alias_path):
            print(
                f"Warning: alias {json_alias} points to non-existing directory")
            print(alias_path)
            print("Please remove this alias, or change its path to a valid path.")
        alias[json_alias] = alias_path

    # Aliases are loaded
    # Switch on operation mode
    if arguments['add']:
        # Register a new alias
        user_dir = arguments['<directory>']
        directory = os.path.abspath(arguments['<directory>'])
        new_alias = arguments['<alias>']
        force = arguments['--force']

        # Don't allow non existing directories
        if not os.path.exists(directory) and not force:
            print(f"{user_dir} does not exist.")
            print("Use --force to create an alias anyway.")
            exit(1)

        # Check whether alias is already defined
        if new_alias in alias and not force:
            print(f"Alias {new_alias} is already defined as")
            print(alias[new_alias])
            print("Instead use")
            print(f"quik edit --change=\"{directory}\" {new_alias}")
            exit(1)

        # Add alias
        alias[new_alias] = directory

        # Give the user some feedback
        print(f"\"{new_alias}\" → \"{directory}\"")

        # Write to json file
        quik_json["alias"] = alias
        with open(quik_json_loc, 'w') as quik_json_io:
            json.dump(quik_json, quik_json_io)

        # Done
        exit(0)
    elif arguments['--list']:
        # List all existing aliases
        for alias_name, alias_dir in alias.items():
            print(f"\"{alias_name}\": \"{alias_dir}\"")
    elif arguments['edit']:
        # Edit an existing alias
        edit_alias = arguments['<alias>']
        if edit_alias not in alias:
            print(f"{edit_alias} is not a defined alias.")
            print(
                "Call `quik list` for a list of defined aliases, or `quik add` to define a new alias.")
            exit(1)

        if arguments['--change']:
            new_dir = arguments['<new>']
            if not os.path.exists(os.path.abspath(new_dir)) and not arguments['--force']:
                print(f"{new_dir} does not exist.")
                print(
                    f"Use --force if you want to set {edit_alias} to point to this directory anyway.")
                exit(1)

            # Set the alias to point to new directory and save
            used_to = alias[edit_alias]
            alias[edit_alias] = os.path.abspath(new_dir)

            # Give the user some feedback
            print(f"Changed {edit_alias} from")
            print(f"{edit_alias} → {used_to}")
            print("to")
            print(f"{edit_alias} → {alias[edit_alias]}")

        elif arguments['--remove']:
            used_to = alias[edit_alias]
            del alias[edit_alias]

            # Give the user some feedback
            print(f"Excluded {edit_alias}, used to point to")
            print(f"{edit_alias} → {used_to}")
    
        # Save the changes and exit
        quik_json["alias"] = alias
        with open(quik_json_loc, 'w') as quik_json_io:
            json.dump(quik_json, quik_json_io)
        exit(0)
    else:
        # Normal operation (cd) mode
        cd_alias = arguments['<alias>']

        if cd_alias not in alias:
            print(f"{cd_alias} is not defined.")
            print("Use `quik add` to add a new alias.")
            exit(1)
        
        # The bash extension will handle it from here.
        print(f"!cd \"{alias[cd_alias]}\"")
        exit(0)
