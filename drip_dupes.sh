#!/bin/bash
set -euo pipefail

# Run from the directory this script lives in, wherever it's checked out
cd "$(dirname "$0")"

set -a
source .env
set +a

# cron runs with a minimal PATH; uv's default install location is ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"
uv run main.py
