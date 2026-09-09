#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
source /home/skk/miniconda3/etc/profile.d/conda.sh
conda activate contract-fuzz
exec python "$ROOT/analyzer/b5_runner.py" "$@"
