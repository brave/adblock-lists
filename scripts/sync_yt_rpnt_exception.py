#!/usr/bin/env python3
"""Sync the uAssets yt-rpnt script comment in brave-unbreak.txt."""
import re
import sys
import urllib.request
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "brave-unbreak.txt"
BEGIN = "! BEGIN uAssets/yt-rpnt AUTO-SYNC"
END = "! END uAssets/yt-rpnt AUTO-SYNC"
BLOCK_RE = re.compile(
    r"^! BEGIN uAssets/yt-rpnt AUTO[-=]SYNC[ \t\r]*$.*?^! END uAssets/yt-rpnt AUTO[-=]SYNC[ \t]*(?=\r?$)",
    re.S | re.M,
)
UPSTREAM_URL = "https://raw.githubusercontent.com/ublockorigin/uAssets/master/filters/quick-fixes.txt"
PREFIX = "www.youtube.com##+js(rpnt, script"

def normalize(text: str) -> str:
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("!"):
            s = s.lstrip("!").strip()
        elif "AUTO=SYNC" in s:
            s = s.replace("AUTO=SYNC", "AUTO-SYNC")
        lines.append(s)
    return "\n".join(lines)


def main() -> None:
    try:
        with urllib.request.urlopen(UPSTREAM_URL, timeout=30) as r:
            upstream = r.read().decode("utf-8").splitlines()
    except Exception as e:
        sys.exit(f"ERROR: reading upstream failed: {e}")

    matches = [line.strip() for line in upstream if line.strip().startswith(PREFIX)]

    if not matches:
        sys.exit(f"ERROR: no upstream rule starting with {PREFIX!r}; leaving file unchanged")

    # Always comment the rule out; the PR is just the commented script
    # catching up to the new upstream version.
    commented = [f"! {m}" for m in dict.fromkeys(matches)]

    # newline="" disables newline translation so existing line endings survive
    with TARGET.open(encoding="utf-8", newline="") as f:
        text = f.read()

    if not BLOCK_RE.search(text):
        sys.exit("ERROR: BEGIN/END markers not found in brave-unbreak.txt")

    eol = "\r\n" if "\r\n" in text else "\n"
    block = eol.join([BEGIN, *commented, END])

    # Replacer function keeps re.sub from interpreting backslashes / "$1" in the rule
    new_text = BLOCK_RE.sub(lambda _: block, text, count=1)

    if normalize(new_text) == normalize(text):
        return
    with TARGET.open("w", encoding="utf-8", newline="") as f:
        f.write(new_text)

if __name__ == "__main__":
    main()
