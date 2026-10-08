#!/usr/bin/env bash
#
# Update the production checkout on the Pi to the commit that just passed CI.
#
# Run by .github/workflows/ci.yml on the self-hosted runner. The runner checks
# the repo out into its own work directory, so $PWD here is *not* the
# production checkout — everything below operates on $DEPLOY_PATH.

set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-$HOME/Modules/email_dupes}"
UV="${UV:-$HOME/.local/bin/uv}"
RUN_WAIT="${RUN_WAIT:-3600}"

log() { printf '==> %s\n' "$*"; }

cd "$DEPLOY_PATH"
HERE=$(pwd -P)

# Cron runs drip_dupes.sh on Mondays at 07:00; it fetches every subscriber,
# builds the spreadsheet and emails it, which takes minutes. It imported its
# code at start-up, but syncing .venv underneath it is not safe, so wait for it
# to finish. RUN_WAIT (1 h) only catches a run that is stuck; then fail rather
# than deploy under it, and re-run the job once it's dealt with.
# A run is `uv run main.py` (from drip_dupes.sh, which cds here first) and its
# `.../python3.N main.py` child. Match only a command line that starts with
# python or `uv run`, so an editor or shell in this directory that merely
# mentions main.py doesn't count.
run_in_progress() {
    local pid
    for pid in $(pgrep -f '^([^ ]*/)?(python[0-9.]*|uv run) main\.py( |$)' || true); do
        [ "$(readlink -f "/proc/$pid/cwd" 2>/dev/null)" = "$HERE" ] && return 0
    done
    return 1
}
waited=0
while run_in_progress; do
    if [ "$waited" -ge "$RUN_WAIT" ]; then
        echo "a duplicate-subscriber run is still in progress after ${RUN_WAIT}s, longer than any" >&2
        echo "normal run; not deploying under it. Check it's not stuck (cron.log), then re-run" >&2
        echo "this job." >&2
        exit 1
    fi
    if [ $((waited % 600)) -eq 0 ]; then
        log "a duplicate-subscriber run is in progress; waiting for it to finish ($((waited / 60)) min so far)"
    fi
    sleep 30
    waited=$((waited + 30))
done

PREVIOUS=$(git rev-parse HEAD)
git fetch --quiet origin main
TARGET=$(git rev-parse origin/main)

log "current:  $PREVIOUS"
log "deploying: $TARGET"

if [ "$PREVIOUS" = "$TARGET" ]; then
    log "already up to date; nothing to do"
    exit 0
fi

# --ff-only rather than `reset --hard`: if the Pi has somehow picked up local
# commits, stop and report it instead of silently discarding them. A
# fast-forward also leaves untracked local state (.env, cron.log, files/)
# completely alone.
git merge --ff-only "$TARGET"

sync_deps() {
    # The same sync cron's `uv run main.py` does at start-up (dev group
    # included), so the next run doesn't reinstall anything.
    "$UV" sync --locked
}

# Syncing on every deploy would be wasted work; the lockfile is the only thing
# that can change what .venv needs to contain.
if git diff --quiet "$PREVIOUS" "$TARGET" -- pyproject.toml uv.lock; then
    log "no dependency changes"
else
    log "dependencies changed; syncing"
    sync_deps
fi

# Importing main imports every module (requests, openpyxl, smtplib) but runs
# nothing: no module does work at import time, and main() is only called under
# `if __name__ == '__main__'`. .env is not sourced, so no credentials are even
# in reach. find_duplicates() is pure, so running it on made-up addresses
# exercises the core logic with no network, email, Drip call or file write.
# Logging is switched off so the smoke test can't add to cron.log.
log "smoke test"
if ! .venv/bin/python -c '
import logging
logging.disable(logging.CRITICAL)
import main  # noqa: F401
from find_dupes import find_duplicates
assert find_duplicates(["a.b@gmail.com", "ab+x@gmail.com", "c@example.com"]) == [
    ("ab@gmail.com", ["a.b@gmail.com", "ab+x@gmail.com"])
]
'; then
    echo "smoke test failed; rolling back to $PREVIOUS" >&2
    git reset --hard "$PREVIOUS"
    sync_deps || true
    exit 1
fi

log "deployed $TARGET"
