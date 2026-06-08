#!/usr/bin/env python3
"""Refresh star counts embedded in the profile README files."""

import json
import math
import os
import re
import sys
import urllib.request

OWNER = "Ricardozm2020"
FILES = ["README.md", "README.zh-CN.md"]
MARKER = re.compile(r"(<!--stars:([\w.\-]+)-->)(.*?)(<!--/stars-->)")
TOKEN = os.environ.get("GITHUB_TOKEN")


def format_count(n: int) -> str:
    if n < 1000:
        return str(n)

    thousands = math.floor(n / 100 + 0.5) / 10
    label = f"{thousands:.1f}".rstrip("0").rstrip(".")
    return f"{label}k"


def fetch_stars(repo: str) -> int:
    req = urllib.request.Request(f"https://api.github.com/repos/{OWNER}/{repo}")
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["stargazers_count"]


def main() -> None:
    cache: dict[str, str] = {}
    changed = False

    for path in FILES:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()

        def replace(match: "re.Match[str]") -> str:
            slug = match.group(2)
            if slug not in cache:
                cache[slug] = format_count(fetch_stars(slug))
                print(f"{slug}: {cache[slug]}")
            return match.group(1) + cache[slug] + match.group(4)

        new_text = MARKER.sub(replace, text)
        if new_text != text:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_text)
            changed = True
            print(f"updated {path}")

    if not changed:
        print("no changes")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
