#!/usr/bin/env python3
"""Check an account workspace against CONVENTIONS.md.

Usage:
    python3 tools/lint.py <account-folder | accounts-folder> [--today YYYY-MM-DD] [--quiet]

Exit code 0 = no errors (warnings and notes may exist), 1 = errors found.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

STATEFUL = {
    "readme", "account-plan", "stakeholders", "actions", "decisions", "proposals",
    "news", "value-proposition", "delivery", "roadmap", "episode",
}
LOG_ONLY = {"comm-log"}
SKIP_FILES = {"review", "inbox-item"}  # saved reports, inbox items

RECORD_TYPES = {
    # prefix: (id regex, required keys, leased, allowed status values)
    "S": (r"S-[a-z0-9-]+", ["role", "influence", "stance", "last_contact"], False, None),
    "G": (r"G-\d+", ["measure", "target_date", "status"], False,
          {"on-track", "at-risk", "off-track", "done", "dropped"}),
    "Q": (r"Q-\d{8}-\d{2}", ["status", "review_by"], True,
          {"open", "answered", "parked", "dropped"}),
    "A": (r"A-\d{8}-\d{2}", ["status", "owner", "review_by"], True,
          {"open", "waiting", "done", "parked", "dropped"}),
    "D": (r"D-\d{8}-\d{2}", ["decided", "status", "revisit"], False,
          {"active", "revisited", "reversed"}),
    "P": (r"P-\d{8}-\d{2}", ["kind", "status"], False,
          {"open", "accepted", "rejected", "done"}),
    "N": (r"N-\d{8}-\d{2}", ["relevance", "status", "review_by"], True,
          {"watch", "acted", "parked", "dropped"}),
    "AVP": (r"AVP-\d+", ["library", "status"], False,
            {"candidate", "active", "retired", "parked", "dropped"}),
    "DL": (r"DL-[a-z0-9-]+", ["status", "review_by"], True,
           {"green", "amber", "red", "closed", "parked"}),
    "RM": (r"RM-[a-z0-9-]+", ["product", "status"], False, None),
}
OPEN_STATES = {"open", "waiting", "watch", "green", "amber", "red"}
LEASE_EXEMPT = {"done", "dropped", "parked", "answered", "acted", "closed"}
DATE_KEYS = {"due", "review_by", "last_contact", "target_date", "decided", "revisit"}
ENUMS = {
    "vis": {"private", "team", "crm"},
    "influence": {"high", "medium", "low", "unknown"},
    "stance": {"champion", "supporter", "neutral", "sceptic", "blocker", "unknown"},
    "buying_role": {"decision-maker", "economic", "technical", "user", "coach",
                    "gatekeeper", "unknown"},
    "kind": {"crm-update", "confirm-stakeholder", "merge-actions", "plan-change",
             "priorities", "vp-change", "other"},
}

HEADING_RE = re.compile(r"^### ((?:AVP|DL|RM|[SGQADPN])-[A-Za-z0-9-]+) · (.+)$")
KEY_RE = re.compile(r"^- ([a-z_]+): (.*)$")
LOG_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) · ")
TAG_RE = re.compile(r"\{src: [^;{}]+; vis: (private|team|crm)\}\s*$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value.strip())
    except ValueError:
        return None


def split_front_matter(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line.startswith((" ", "-")):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.split(" #")[0].strip()
    return fm, text[end + 5:]


def lint_file(path: Path, account: str, rep: Report, ids: dict[str, str],
              records: list[tuple[str, dict[str, str], str]]) -> None:
    rel = str(path)
    text = path.read_text(encoding="utf-8")
    parsed = split_front_matter(text)
    if parsed is None:
        rep.err(rel, "missing YAML front matter")
        return
    fm, body = parsed
    role = fm.get("file", "")
    if role in SKIP_FILES:
        return
    for key in ("file", "account", "updated"):
        if key not in fm:
            rep.err(rel, f"front matter lacks '{key}'")
    expected = "readme" if path.name == "README.md" else path.stem
    if role != "episode" and role and role != expected:
        rep.err(rel, f"front matter file '{role}' does not match filename")
    if fm.get("account") and fm["account"] != account:
        rep.err(rel, f"front matter account '{fm['account']}' is not folder '{account}'")
    if "updated" in fm and parse_date(fm["updated"]) is None:
        rep.err(rel, "front matter 'updated' is not an ISO date")
    if role == "episode":
        for key in ("id", "opened", "status"):
            if key not in fm:
                rep.err(rel, f"episode front matter lacks '{key}'")

    body = COMMENT_RE.sub("", body)
    lines = body.splitlines()
    h2 = [(i, ln[3:].strip()) for i, ln in enumerate(lines) if ln.startswith("## ")]
    names = [n for _, n in h2]
    if role in STATEFUL:
        if names[:2] != ["Current", "History"] or len(names) != 2:
            rep.err(rel, f"needs exactly '## Current' then '## History', found {names}")
    elif role in LOG_ONLY and names != ["History"]:
        rep.err(rel, f"needs exactly '## History', found {names}")

    section = None
    current: tuple[str, dict[str, str], int] | None = None

    def close_record() -> None:
        nonlocal current
        if current is not None:
            rid, keys, line_no = current
            records.append((rid, keys, f"{rel}:{line_no}"))
        current = None

    for i, line in enumerate(lines, start=1):
        if line.startswith("## "):
            close_record()
            section = line[3:].strip()
            continue
        if line.startswith("### "):
            close_record()
            m = HEADING_RE.match(line)
            if m and section == "Current":
                rid = m.group(1)
                if rid in ids:
                    rep.err(f"{rel}:{i}", f"duplicate ID {rid} (also in {ids[rid]})")
                ids[rid] = f"{rel}:{i}"
                current = (rid, {}, i)
            elif m and section == "History":
                rep.err(f"{rel}:{i}", f"record {m.group(1)} under History; History holds log entries only")
            continue
        if current is not None:
            km = KEY_RE.match(line)
            if km:
                current[1][km.group(1)] = km.group(2).strip()
            continue
        if section == "History" and line.startswith("- "):
            if not LOG_RE.match(line):
                rep.err(f"{rel}:{i}", "log entry must start with '- YYYY-MM-DD · '")
            elif not TAG_RE.search(line):
                rep.err(f"{rel}:{i}", "log entry must end with '{src: …; vis: private|team|crm}'")
    close_record()


def check_records(records, ids, today: dt.date, rep: Report) -> list[str]:
    expired: list[str] = []
    for rid, keys, where in records:
        prefix = rid.split("-")[0]
        id_re, required, leased, statuses = RECORD_TYPES[prefix]
        if not re.fullmatch(id_re, rid):
            rep.err(where, f"ID {rid} does not match pattern {id_re}")
        for key in ["src", "vis", *required]:
            if key not in keys or keys[key] == "":
                rep.err(where, f"{rid} lacks '{key}'")
        for key, allowed in ENUMS.items():
            if key in keys and keys[key] not in allowed:
                rep.err(where, f"{rid} {key} '{keys[key]}' not in {sorted(allowed)}")
        status = keys.get("status", "")
        if statuses and status and status not in statuses:
            rep.err(where, f"{rid} status '{status}' not in {sorted(statuses)}")
        for key in DATE_KEYS & keys.keys():
            if keys[key] != "unknown" and parse_date(keys[key]) is None:
                rep.err(where, f"{rid} {key} '{keys[key]}' is not an ISO date or 'unknown'")
        if keys.get("src", "").startswith("inferred") and prefix != "P":
            rep.err(where, f"{rid} has src 'inferred' — inferences belong in proposals")
        if leased and status not in LEASE_EXEMPT:
            rb = parse_date(keys.get("review_by", ""))
            if rb and rb < today:
                expired.append(f"{rid} (review_by {rb}) — {where}")
        for dep in [d.strip() for d in keys.get("depends_on", "").split(",") if d.strip()]:
            if dep not in ids:
                rep.err(where, f"{rid} depends_on unknown ID {dep}")
    return expired


def lint_account(folder: Path, today: dt.date, rep: Report) -> None:
    account = folder.name
    ids: dict[str, str] = {}
    records: list = []
    files = sorted(folder.glob("*.md")) + sorted((folder / "episodes").glob("*.md"))
    present = {p.name for p in folder.glob("*.md")}
    for name in ("README.md", "account-plan.md", "stakeholders.md", "comm-log.md", "actions.md",
                 "decisions.md", "proposals.md", "news.md", "value-proposition.md",
                 "delivery.md", "roadmap.md"):
        if name not in present:
            rep.err(str(folder), f"missing {name}")
    for path in files:
        lint_file(path, account, rep, ids, records)
    expired = check_records(records, ids, today, rep)

    readme = folder / "README.md"
    budget = None
    if readme.exists():
        parsed = split_front_matter(readme.read_text(encoding="utf-8"))
        if parsed:
            fm = parsed[0]
            for key in ("name", "owner", "phase", "last_review", "last_ingest", "reminder_budget"):
                if key not in fm:
                    rep.warn(str(readme), f"settings lack '{key}'")
            budget = fm.get("reminder_budget")

    inbox = [p.name for p in (folder / "inbox").glob("*") if p.name != ".gitkeep"] \
        if (folder / "inbox").exists() else []
    open_actions = sum(1 for rid, k, _ in records
                       if rid.startswith("A-") and k.get("status") in OPEN_STATES)
    open_props = sum(1 for rid, k, _ in records
                     if rid.startswith("P-") and k.get("status") == "open")
    rep.note(f"[{account}] records {len(records)} · open actions {open_actions} · "
             f"open proposals {open_props} · inbox {len(inbox)} · reminder budget {budget}")
    if expired:
        rep.note(f"[{account}] expired leases ({len(expired)}):")
        rep.notes.extend(f"    {e}" for e in expired)
    if inbox:
        rep.note(f"[{account}] not yet ingested: {', '.join(sorted(inbox))}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path)
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--quiet", action="store_true", help="errors only")
    args = ap.parse_args()

    target: Path = args.path
    if not target.is_dir():
        print(f"not a folder: {target}", file=sys.stderr)
        return 2
    if (target / "README.md").exists() and (target / "inbox").exists():
        accounts = [target]
    else:
        accounts = sorted(p for p in target.iterdir()
                          if p.is_dir() and not p.name.startswith(("_", ".")))
    rep = Report()
    for folder in accounts:
        lint_account(folder, args.today, rep)

    for e in rep.errors:
        print(f"ERROR   {e}")
    if not args.quiet:
        for w in rep.warnings:
            print(f"WARNING {w}")
        for n in rep.notes:
            print(f"NOTE    {n}")
    print(f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s), {len(accounts)} account(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
