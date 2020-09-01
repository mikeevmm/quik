#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "Making sure a quik.json exists..."
if [ -f "$DIR/quik.json" ]
then
	echo -e "\033[32mquik.json already exists.\033[0m"
else
	echo -e "\033[33mCouldn't find a quik.json here, checking env. variables...\033[0m"
	if [ -f "$QUIK_JSON" ]
	then
		echo -e "\033[32mFound a quik.json via environment variable.\033[0m"
	else
		read -p "Couldn't find a quik.json anywhere, would you like to create one now? [Y/n]" -r
		if [[ ! $REPLY =~ ^[Nn]$ ]]
		then
			echo "Writing a default quik.json onto $DIR/quik.json"
			if cp "$DIR/internals/quik_empty.json" "$DIR/quik.json"
			then
				echo -e "\033[32mDone.\033[0m"
			else
				echo -e "\033[91mSomething went wrong."
				echo "Please create a default quik.json file at $DIR/quik.json,"
				echo -e "or point to an existing one using \$QUIK_JSON.\033[0m"
			fi
		else
			echo "Ok, but a quik.json file is needed."
			echo "You should find an empty (default) quik.json file at"
			echo "$DIR/internals/quik_empty.json"
		fi
	fi
fi

echo ""
echo -e "\033[33mPlease add the following line to your ~/.bashrc or equivalent:\033[0m"
echo "source \"$DIR/internals/quik_setup.sh\""
source "$DIR/internals/quik_setup.sh"

echo ""
echo -e "Call \`quik --help\` for more info."
