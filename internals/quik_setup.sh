#!/bin/bash
# The glue between the core contents of quik and the shell you are using.
#
# If you want to parse quik, what you need is to parse this file to your
# favorite shell. Likely, you should expect that this file is sourced (say, at
# shell startup) and not ran, because it provides functionality within the
# user's session, and requires the ability to change the user's working
# directory. This is achieved, in this case, by defining a function. See below.

# Get this file's directory, so that we can reference other quik files
# as relative paths to it.
# (It is an invariant that this file, or ports of it, live in
# `<quik's installation directory>/internal`. )
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Get the path for the main quik (python) script.
# This file is responsible for taking in the users input, and producing output
# that can signal the directory should be changed or just report some
# information to the user.
PY_QUIK="$DIR/../quik.py"

# Get the path for the output parsing (python) script.
# This script is just responsible for taking the raw output of the PY_QUIK
# process and doing the parsing for us, both into the directory we should `cd`
# into, or just into the output that the user should see.
PY_PARSE="$DIR/output_parse.py"

# Quik expects this environment variable to be set to the JSON file where
# the user's bookmarked directories are saved.
export QUIK_JSON="$DIR/../quik.json"

# The function that the user will call when they type `quik` into the terminal.
#
# This may have to be an alias or some other kind of construction if you are
# porting this file to other shells. In any case, the user never directly calls
# the PY_QUIK python file, because that wouldn't be able to change the user's
# working directory as an external process (for every shell I'm aware of).
#
# See also the PowerShell port, where `quik` is an alias to a function, or the
# Windows (Batch) port, which switches mode based on an environment variable.
function quik {
    # Run the PY_QUIK python script, and capture the raw output.
    # PY_QUIK takes whatever arguments the user called this function with.
    # We save also the return code of this main script, so that we can exit the
    # function with that same return code.
    OUTPUT="$(${PY_QUIK} "$@")"
    RET=$?

    # We can use the PY_PARSE auxiliary script to split the raw output into
    # what the output that should be shown to the user, and the directory
    # that we should change into.
    #
    # These two modes of operation can be achieved with the `--output` and
    # `--cd` flags.
    #
    # If the `--cd` mode output is empty, that means that there is no directory
    # to change to.
    DIR="$(echo -e -n "${OUTPUT}" | ${PY_PARSE} --cd)"
    echo -e -n "$(echo -n "${OUTPUT}" | ${PY_PARSE} --output)"
    if  [[ $param = *[!\ ]* ]] # output is anything other than whitespace
    then
        cd "${DIR}"
    fi

    return ${RET}
}

# Since quik is a "speed" tool, it is fairly important to have autocomplete
# functionality for the aliases. (There are only so many terse aliases you can
# define and remember.)
#
# While the autocomplete mechanisms are very specific to the shell, PY_QUIK
# helps with this task via the `--complete` mode of operation, where, when given
# a stub for a command, like
#
#       quik --
#
# passing this as a string to `PY_QUIK --complete` returns a list of possible
# completions to the last word, separated by newlines. So, in this case, we
# would get as an output to `PY_QUIK --complete 'quik --'` something like
#
#       --list
#       --help
#
# The main convenience for this is that autocompletion for the user's defined
# aliases is also provided.
# If there are no suggestions to the provided stub, the process exits with
# non-zero return code. In this case, your code should attempt to autocomplete
# the stub as a path. This is due to the case where the user does something like
#
#       quik add my_alias ./dire<tab>
#
# and expects an expansion to `./directory`.
function _quik_autocomplete {
    COMPL_OUT="$(${PY_PARSE} --complete="$COMP_LINE")"
    SUCCESS=$?
    COMPREPLY=()
    if [ $SUCCESS == 0 ]
    then
        # We have an autocompletion suggestion from PY_PARSE
        readarray -t COMPREPLY <<<"$COMPL_OUT"
    else
        # There are no autocompletion suggestions; we suggest elements from the
        # current directory.
        local cur
        case "$2" in
                \~*)    eval cur="$2" ;;
                *)      cur=$2 ;;
        esac
        COMPREPLY=( $(compgen -d -- "$cur") )
    fi
}

complete -F _quik_autocomplete -o dirnames quik
