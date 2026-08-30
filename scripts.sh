#!/usr/bin/env bash
set -euo pipefail

# Menu to select and run a script from ./scripts/*.sh
SCRIPTS_DIR="./scripts"

if [ ! -d "$SCRIPTS_DIR" ]; then
	echo "Directory '$SCRIPTS_DIR' not found."
	exit 1
fi

mapfile -d '' scripts < <(find "$SCRIPTS_DIR" -maxdepth 1 -type f -name "*.sh" -print0 | sort -z)

if [ ${#scripts[@]} -eq 0 ]; then
	echo "No scripts found in $SCRIPTS_DIR"
	exit 0
fi

echo "Available scripts:"
for i in "${!scripts[@]}"; do
	idx=$((i+1))
	name=$(basename "${scripts[i]}")
	echo "  $idx) $name"
done
echo "  q) Quit"

while true; do
	read -rp $'Select a script number to run (or q to quit): ' choice
	if [[ "$choice" =~ ^[Qq]$ ]]; then
		echo "Exiting."
		exit 0
	fi
	if [[ "$choice" =~ ^[0-9]+$ ]]; then
		if (( choice >= 1 && choice <= ${#scripts[@]} )); then
			sel=${scripts[choice-1]}
			echo "Running: $sel"
			# Ensure executable then run in a new shell
			chmod +x "$sel" 2>/dev/null || true
			bash "$sel"
			exit_code=$?
			echo "Script exited with code: $exit_code"
			exit $exit_code
		fi
	fi
	echo "Invalid selection."
done

