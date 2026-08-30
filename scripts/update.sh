#!/usr/bin/env bash

set -euo pipefail

get_current_version() {
	grep -E '^version[[:space:]]*=' pyproject.toml | head -n 1 | sed -E 's/.*"([^"]+)".*/\1/'
}

CURRENT_VERSION="$(get_current_version)"

if [[ -z "$CURRENT_VERSION" ]]; then
	echo "Could not read current version from pyproject.toml" >&2
	exit 1
fi

echo "Current version: ${CURRENT_VERSION}"

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
	read -r -p "Enter new version: " VERSION
fi

if [[ -z "$VERSION" ]]; then
	echo "No version provided" >&2
	exit 1
fi

if [[ ! -f pyproject.toml || ! -f setup.py ]]; then
	echo "pyproject.toml and setup.py must exist in the current directory" >&2
	exit 1
fi

sed -i -E "s/(version\s*=\s*\")[^\"]*(\")/\1${VERSION}\2/" pyproject.toml
sed -i -E "s/(version\s*=\s*['\"])[^'\"]*(['\"])/\1${VERSION}\2/" setup.py

echo "New version: ${VERSION}"
