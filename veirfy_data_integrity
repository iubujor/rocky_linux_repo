#!/usr/bin/env python3

import argparse
import gzip
import hashlib
import lzma
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS_REPOMD = {"repo": "http://linux.duke.edu/metadata/repo"}
NS_COMMON = {"common": "http://linux.duke.edu/metadata/common"}

def open_metadata(path: Path):
    if path.name.endswith(".gz"):
        return gzip.open(path, "rb")
    if path.name.endswith(".xz"):
        return lzma.open(path, "rb")
    return open(path, "rb")

def hash_file(path: Path, algo: str) -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def find_primary_metadata(repo_root: Path) -> Path:
    repomd = repo_root / "repodata" / "repomd.xml"

    if not repomd.exists():
        raise FileNotFoundError(f"Missing {repomd}")

    tree = ET.parse(repomd)
    root = tree.getroot()

    for data in root.findall("repo:data", NS_REPOMD):
        if data.attrib.get("type") == "primary":
            location = data.find("repo:location", NS_REPOMD)
            if location is None:
                continue

            href = location.attrib.get("href")
            if not href:
                continue

            primary = repo_root / href

            if not primary.exists():
                raise FileNotFoundError(f"Primary metadata referenced but missing: {primary}")

            return primary

    raise RuntimeError(f"No primary metadata found in {repomd}")

def verify_repo(repo_root: Path) -> int:
    primary = find_primary_metadata(repo_root)

    print(f"[INFO] Repo: {repo_root}")
    print(f"[INFO] Primary metadata: {primary}")

    checked = 0
    failed = 0
    missing = 0

    with open_metadata(primary) as f:
        tree = ET.parse(f)

    root = tree.getroot()

    for pkg in root.findall("common:package", NS_COMMON):
        location = pkg.find("common:location", NS_COMMON)
        checksum = pkg.find("common:checksum", NS_COMMON)

        if location is None or checksum is None:
            continue

        href = location.attrib.get("href")
        expected = checksum.text
        algo = checksum.attrib.get("type", "sha256")

        if not href or not expected:
            continue

        rpm_path = repo_root / href

        if not rpm_path.exists():
            print(f"[MISSING] {rpm_path}")
            missing += 1
            continue

        actual = hash_file(rpm_path, algo)

        if actual.lower() != expected.lower():
            print(f"[FAILED] {rpm_path}")
            print(f"         algo:     {algo}")
            print(f"         expected: {expected}")
            print(f"         actual:   {actual}")
            failed += 1
        else:
            checked += 1

    print(f"[RESULT] checked={checked} missing={missing} failed={failed}")

    if missing or failed:
        return 1

    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Verify RPM checksums against repository primary metadata."
    )

    parser.add_argument(
        "repo_roots",
        nargs="+",
        help="Repository roots, for example /home1/repos/rocky/9/BaseOS/x86_64/os"
    )

    args = parser.parse_args()

    exit_code = 0

    for repo in args.repo_roots:
        try:
            rc = verify_repo(Path(repo))
            if rc != 0:
                exit_code = rc
        except Exception as e:
            print(f"[ERROR] {repo}: {e}", file=sys.stderr)
            exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
