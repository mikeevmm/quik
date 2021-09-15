#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PY_QUIK="$DIR/../quik.py"
PY_PARSE="$DIR/output_parse.py"
export QUIK_JSON="$DIR/../quik.json"

function _quik_autocomplete {
	COMPL_OUT="$(${PY_PARSE} --complete="$COMP_LINE")"
	SUCCESS=$?
	COMPREPLY=()
	if [ $SUCCESS == 0 ]
	then
		readarray -t COMPREPLY <<<"$COMPL_OUT"
	else
		local cur
		case "$2" in
			\~*)    eval cur="$2" ;;
			*)      cur=$2 ;;
		esac
		COMPREPLY=( $(compgen -d -- "$cur") )
	fi
}

function quik {
	OUTPUT="$(${PY_QUIK} "$@")"
	RET=$?
	if [[ "${OUTPUT}" == *"!cd "* ]]
	then
		echo -e -n "$(echo -n "${OUTPUT}" | ${PY_PARSE} --output)"
		DIR="$(echo -e -n "${OUTPUT}" | ${PY_PARSE} --cd)"
		cd "${DIR}"
	else
		echo -n "${OUTPUT}"
	fi

	return ${RET}
}

complete -F _quik_autocomplete -o dirnames quik
