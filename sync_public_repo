#!/usr/bin/env bash
set -euo pipefail

UPSTREAM="rsync://CHOOSE_PUBLIC_REPOSITORY"
DEST="/home1/repos/rocky"
LOGDIR="/var/log/rocky-sync"
DATE="$(date +%F_%H-%M-%S)"
LOGFILE="${LOGDIR}/sync-${DATE}.log"

mkdir -p "$DEST" "$LOGDIR"

RSYNC_OPTS=(
  -avH
  --delete
  --delete-delay
  --delay-updates
  --safe-links
  --numeric-ids
  --partial
  --partial-dir=.rsync-partial
  --timeout=600
  --contimeout=60
  --info=stats2,progress2
)

REPOS=(
  "8/BaseOS/x86_64/os/"
  "8/AppStream/x86_64/os/"
  "8/extras/x86_64/os/"
  "8/PowerTools/x86_64/os/"
  "9/BaseOS/x86_64/os/"
  "9/AppStream/x86_64/os/"
  "9/extras/x86_64/os/"
  "9/CRB/x86_64/os/"
)

echo "===== Rocky sync started: $(date -Is) =====" | tee -a "$LOGFILE"
echo "Upstream: $UPSTREAM" | tee -a "$LOGFILE"
echo "Destination: $DEST" | tee -a "$LOGFILE"

for repo in "${REPOS[@]}"; do
  echo "---- Syncing ${repo} ----" | tee -a "$LOGFILE"
  mkdir -p "${DEST}/${repo}"

  rsync "${RSYNC_OPTS[@]}" \
    "${UPSTREAM}/${repo}" \
    "${DEST}/${repo}" \
    2>&1 | tee -a "$LOGFILE"
done

echo "===== Rocky sync finished: $(date -Is) =====" | tee -a "$LOGFILE"
