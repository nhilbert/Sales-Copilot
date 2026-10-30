#!/usr/bin/env python3
"""Block commits that contain private terms (client names, people, internal codes).

The denylist lives OUTSIDE this public repository, one term per line
(case-insensitive, whole words; lines starting with # are comments):

    ~/.config/sales-copilot/denylist.txt      (default)
    $SALES_COPILOT_DENYLIST                   (override)

Usage:
    python3 tools/public_guard.py            check files staged for commit
    python3 tools/public_guard.py --all      check every tracked file

Install as a git pre-commit hook:
    printf '#!/bin/sh\\npython3 tools/public_guard.py\\n' > .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT = Path.home() / ".config/sales-copilot/denylist.txt"


def load_terms() -> list[str]:
    path = Path(os.environ.get("SALES_COPILOT_DENYLIST", DEFAULT))
    if not path.exists():
        print(f"public_guard: no denylist at {path} — nothing to check against.", file=sys.stderr)
        return []
    return [ln.strip().lower() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def files(all_files: bool) -> list[str]:
    cmd = ["git", "ls-files"] if all_files else \
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    return [f for f in subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.splitlines() if f]


def main() -> int:
    terms = load_terms()
    if not terms:
        return 0
    hits = []
    for name in files("--all" in sys.argv):
        try:
            text = Path(name).read_text(encoding="utf-8", errors="ignore").lower()
        except (FileNotFoundError, IsADirectoryError):
            continue
        for term in terms:
            pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
            if re.search(pattern, text) or re.search(pattern, name.lower()):
                hits.append((name, term))
    for name, term in hits:
        print(f"public_guard: private term found in {name} (term #{terms.index(term) + 1} of denylist)")
    if hits:
        print("public_guard: commit blocked. Remove the terms or move the file to your private workspace.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
