DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PY_QUIK="$DIR/../quik.py"
PY_PARSE="$DIR/output_parse.py"
export QUIK_JSON="$DIR/../quik.json"

function quik {
	OUTPUT="$("$PY_QUIK" "$@")"
	RET=$!
	if [[ "$OUTPUT" == *"!cd "* ]]
	then
		echo -e -n "$(echo -n "$OUTPUT" | $PY_PARSE --output)"
		DIR="$(echo -e -n "$OUTPUT" | $PY_PARSE --cd)"
		cd "$DIR"
	else
		echo -n "$OUTPUT"
	fi

	return $RET
}
