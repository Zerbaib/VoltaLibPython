#!/usr/bin/env bash

set -euo pipefail

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
	echo "Usage: $0 <version>" >&2
	exit 1
fi

if [[ ! -f pyproject.toml || ! -f setup.py ]]; then
	echo "pyproject.toml and setup.py must exist in the current directory" >&2
	exit 1
fi

sed -i -E "s/(version\s*=\s*\")[^\"]*(\")/\1${VERSION}\2/" pyproject.toml
sed -i -E "s/(version\s*=\s*['\"])[][^'\"]*(['\"])/\1${VERSION}\2/" setup.py

echo "Updated version to ${VERSION}"
