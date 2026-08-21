#!/usr/bin/env bash

# Print the repository root without depending on a particular checkout path.
# Invoke with: bash scripts/resolve_repo_root.sh

set -euo pipefail

script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(git -C "${script_directory}/.." rev-parse --show-toplevel 2>/dev/null)" || {
    echo "Error: not inside a Git checkout" >&2
    exit 1
}

printf "%s\n" "${repository_root}"
