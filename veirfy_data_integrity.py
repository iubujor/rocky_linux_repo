#!/usr/bin/env python3

import argparse
import gzip
import hashlib
import lzma
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS_REPOMD = "{http://linux.duke.edu/metadata/repo}"
NS_COMMON = "{http://linux.duke.edu/metadata/common}"

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

    for data in root.findall(f"{NS_REPOMD}data"):
        if data.attrib.get("type") == "primary":
            location = data.find(f"{NS_REPOMD}location")

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

def get_child(elem, name):
    return elem.find(f"{NS_COMMON}{name}")

def verify_repo(repo_root: Path, stop_after: int = 0) -> int:
    primary = find_primary_metadata(repo_root)

    print(f"[INFO] Repo: {repo_root}", flush=True)
    print(f"[INFO] Primary metadata: {primary}", flush=True)

    checked = 0
    failed = 0
    missing = 0
    processed = 0

    with open_metadata(primary) as f:
        context = ET.iterparse(f, events=("end",))

        for event, pkg in context:
            if pkg.tag != f"{NS_COMMON}package":
                continue

            location = get_child(pkg, "location")
            checksum = get_child(pkg, "checksum")

            if location is None or checksum is None:
                pkg.clear()
                continue

            href = location.attrib.get("href")
            expected = checksum.text
            algo = checksum.attrib.get("type", "sha256")

            if not href or not expected:
                pkg.clear()
                continue

            rpm_path = repo_root / href
            processed += 1

            if not rpm_path.exists():
                print(f"[MISSING] {rpm_path}", flush=True)
                missing += 1
                pkg.clear()
                continue

            try:
                actual = hash_file(rpm_path, algo)
            except Exception as e:
                print(f"[ERROR] Cannot hash {rpm_path}: {e}", flush=True)
                failed += 1
                pkg.clear()
                continue

            if actual.lower() != expected.lower():
                print(f"[FAILED] {rpm_path}", flush=True)
                print(f"         algo:     {algo}", flush=True)
                print(f"         expected: {expected}", flush=True)
                print(f"         actual:   {actual}", flush=True)
                failed += 1
            else:
                checked += 1

            if processed % 500 == 0:
                print(
                    f"[PROGRESS] processed={processed} checked={checked} missing={missing} failed={failed}",
                    flush=True
                )

            pkg.clear()

            if stop_after and processed >= stop_after:
                print(f"[INFO] Stopped after {processed} packages because --stop-after was set.", flush=True)
                break

    print(f"[RESULT] checked={checked} missing={missing} failed={failed}", flush=True)

    if missing or failed:
        return 1

    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Streaming RPM checksum verification against repository primary metadata."
    )

    parser.add_argument(
        "repo_roots",
        nargs="+",
        help="Repository roots, for example /home1/repos/rocky/9/BaseOS/x86_64/os"
    )

    parser.add_argument(
        "--stop-after",
        type=int,
        default=0,
        help="Optional test mode: stop after N packages."
    )

    args = parser.parse_args()

    exit_code = 0

    for repo in args.repo_roots:
        try:
            rc = verify_repo(Path(repo), args.stop_after)
            if rc != 0:
                exit_code = rc
        except Exception as e:
            print(f"[ERROR] {repo}: {e}", file=sys.stderr, flush=True)
            exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
