#!/usr/bin/env bash
set -euo pipefail

REPOS=(
  "/home1/repos/rocky/8/BaseOS/x86_64/os"
  "/home1/repos/rocky/8/AppStream/x86_64/os"
  "/home1/repos/rocky/8/extras/x86_64/os"
  "/home1/repos/rocky/8/PowerTools/x86_64/os"
  "/home1/repos/rocky/9/BaseOS/x86_64/os"
  "/home1/repos/rocky/9/AppStream/x86_64/os"
  "/home1/repos/rocky/9/extras/x86_64/os"
  "/home1/repos/rocky/9/CRB/x86_64/os"
)

for repo in "${REPOS[@]}"; do
  repomd="${repo}/repodata/repomd.xml"
  sig="${repo}/repodata/repomd.xml.asc"

  echo "Checking signature: ${repo}"

  if [[ ! -f "$repomd" ]]; then
    echo "[ERROR] Missing $repomd"
    exit 1
  fi

  if [[ ! -f "$sig" ]]; then
    echo "[ERROR] Missing $sig"
    exit 1
  fi

  gpg --verify "$sig" "$repomd"
done

echo "All repomd.xml signatures verified."
