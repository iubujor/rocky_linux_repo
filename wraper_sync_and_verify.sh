#!/usr/bin/env bash
set -euo pipefail

LOGDIR="/var/log/rocky-sync"
DATE="$(date +%F_%H-%M-%S)"
LOGFILE="${LOGDIR}/sync-and-verify-${DATE}.log"

mkdir -p "$LOGDIR"

{
  echo "===== START $(date -Is) ====="

  /usr/local/sbin/sync-rocky-local.sh

  echo "===== CHECKSUM VERIFICATION START $(date -Is) ====="

  /usr/local/sbin/verify-rocky-repo-checksums.py \
    /home1/repos/rocky/8/BaseOS/x86_64/os \
    /home1/repos/rocky/8/AppStream/x86_64/os \
    /home1/repos/rocky/8/extras/x86_64/os \
    /home1/repos/rocky/8/PowerTools/x86_64/os \
    /home1/repos/rocky/9/BaseOS/x86_64/os \
    /home1/repos/rocky/9/AppStream/x86_64/os \
    /home1/repos/rocky/9/extras/x86_64/os \
    /home1/repos/rocky/9/CRB/x86_64/os

  echo "===== GPG REPOMD VERIFICATION START $(date -Is) ====="

  /usr/local/sbin/verify-rocky-repomd-signatures.sh

  echo "===== FIX PERMISSIONS START $(date -Is) ====="

  chown -R root:root /home1/repos/rocky
  find /home1/repos/rocky -type d -exec chmod 755 {} \;
  find /home1/repos/rocky -type f -exec chmod 644 {} \;

  echo "===== SUCCESS $(date -Is) ====="
} 2>&1 | tee -a "$LOGFILE"
