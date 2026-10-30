#!/usr/bin/env python3
"""Set up and maintain a private account workspace from this repository.

    python3 tools/desk.py init <workspace>                      create a workspace (outside this repo)
    python3 tools/desk.py new-account <workspace> <slug> --name "Display Name"
    python3 tools/desk.py demo <workspace>                      copy the fictional demo workspace
    python3 tools/desk.py update <workspace>                    refresh rules, skills, tools, templates
    python3 tools/desk.py package [--out dist]                  zip each skill for upload to Claude

The workspace receives copies, not links, so it works on any OS and keeps
running if this repository moves. `update` overwrites only the copied rule,
skill, tool and template files — never anything under accounts/ or _shared/.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_TARGETS = (".claude/skills", ".agents/skills")


def refuse_inside_repo(ws: Path) -> None:
    ws = ws.resolve()
    if ws == REPO or REPO in ws.parents:
        sys.exit("Refusing: the workspace must live outside the Sales Copilot repository "
                 "(it is public; account data must never be inside it).")


def copy_rules(ws: Path) -> None:
    for name in ("POLICY.md", "CONVENTIONS.md"):
        shutil.copy2(REPO / name, ws / name)
    for name in ("AGENTS.md", "CLAUDE.md"):
        shutil.copy2(REPO / "templates/workspace" / name, ws / name)
    (ws / ".claude").mkdir(exist_ok=True)
    shutil.copy2(REPO / "templates/workspace/.claude/settings.json", ws / ".claude/settings.json")
    (ws / "tools").mkdir(exist_ok=True)
    shutil.copy2(REPO / "tools/lint.py", ws / "tools/lint.py")
    if (ws / "templates").exists():
        shutil.rmtree(ws / "templates")
    shutil.copytree(REPO / "templates", ws / "templates",
                    ignore=shutil.ignore_patterns("workspace"))
    for target in SKILL_TARGETS:
        dest = ws / target
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(REPO / "skills", dest)


def git(ws: Path, *args: str) -> None:
    if shutil.which("git"):
        subprocess.run(["git", "-C", str(ws), *args], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def cmd_init(args: argparse.Namespace) -> None:
    ws: Path = args.workspace.expanduser()
    refuse_inside_repo(ws)
    if ws.exists() and any(ws.iterdir()):
        sys.exit(f"{ws} exists and is not empty; use 'update' for an existing workspace.")
    for sub in ("accounts", "_shared/products", "_shared/competitors", "_shared/value-propositions"):
        (ws / sub).mkdir(parents=True, exist_ok=True)
        (ws / sub / ".gitkeep").touch()
    copy_rules(ws)
    (ws / ".gitignore").write_text("# private workspace — keep it out of public remotes\n")
    git(ws, "init", "-q")
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", "init workspace")
    print(f"Workspace created at {ws}. Never add a public git remote to it.")


def fill(text: str, values: dict[str, str]) -> str:
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), m.group(0)), text)


def cmd_new_account(args: argparse.Namespace) -> None:
    ws: Path = args.workspace.expanduser()
    refuse_inside_repo(ws)
    slug = args.slug
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        sys.exit("slug must be lowercase letters, digits and hyphens")
    folder = ws / "accounts" / slug
    if folder.exists():
        sys.exit(f"{folder} already exists")
    today = dt.date.today().isoformat()
    values = {"account": slug, "name": args.name or slug, "date": today}
    for sub in ("inbox", "archive", "episodes", "reviews"):
        (folder / sub).mkdir(parents=True)
        (folder / sub / ".gitkeep").touch()
    for tpl in sorted((REPO / "templates/account").glob("*.md")):
        (folder / tpl.name).write_text(fill(tpl.read_text(encoding="utf-8"), values), encoding="utf-8")
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", f"new account: {slug}")
    print(f"Account created at {folder}")


def cmd_demo(args: argparse.Namespace) -> None:
    ws: Path = args.workspace.expanduser()
    refuse_inside_repo(ws)
    if ws.exists() and any(ws.iterdir()):
        sys.exit(f"{ws} exists and is not empty")
    shutil.copytree(REPO / "examples/demo-workspace", ws, dirs_exist_ok=True)
    shutil.copytree(REPO / "examples/demo-inputs", ws / "demo-inputs")
    shutil.copy2(REPO / "examples/DEMO-SCRIPT.md", ws / "DEMO-SCRIPT.md")
    copy_rules(ws)
    git(ws, "init", "-q")
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", "demo workspace (fictional data)")
    print(f"Demo workspace (fictional data) created at {ws}. Reference date: 2026-10-30.")


def cmd_update(args: argparse.Namespace) -> None:
    ws: Path = args.workspace.expanduser()
    refuse_inside_repo(ws)
    if not (ws / "accounts").is_dir():
        sys.exit(f"{ws} does not look like a workspace (no accounts/ folder)")
    copy_rules(ws)
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", "update rules and skills from Sales Copilot")
    print(f"Rules, skills, tools and templates refreshed in {ws}")


def cmd_package(args: argparse.Namespace) -> None:
    out: Path = args.out if args.out.is_absolute() else REPO / args.out
    out.mkdir(parents=True, exist_ok=True)
    for skill in sorted(p for p in (REPO / "skills").iterdir() if (p / "SKILL.md").exists()):
        target = out / f"{skill.name}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(skill.rglob("*")):
                if f.is_file():
                    zf.write(f, Path(skill.name) / f.relative_to(skill))
        print(f"packaged {target.relative_to(REPO) if REPO in target.parents else target}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("workspace", type=Path); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("new-account"); p.add_argument("workspace", type=Path)
    p.add_argument("slug"); p.add_argument("--name"); p.set_defaults(fn=cmd_new_account)
    p = sub.add_parser("demo"); p.add_argument("workspace", type=Path); p.set_defaults(fn=cmd_demo)
    p = sub.add_parser("update"); p.add_argument("workspace", type=Path); p.set_defaults(fn=cmd_update)
    p = sub.add_parser("package"); p.add_argument("--out", type=Path, default=Path("dist"))
    p.set_defaults(fn=cmd_package)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
