#!/usr/bin/env python3
"""Maintainer tool: build workspaces and release downloads from this repository.

End users need none of this. They download the release zips, unzip a
workspace, connect it in the Claude desktop app and upload the skill zips.

    python3 tools/desk.py release [--out dist]                  build all release zips
    python3 tools/desk.py init <workspace>                      create an empty workspace
    python3 tools/desk.py demo <workspace>                      create the fictional demo workspace
    python3 tools/desk.py new-account <workspace> <slug> --name "Display Name"
    python3 tools/desk.py update <workspace>                    refresh rules, skills, templates
    python3 tools/desk.py package [--out dist]                  zip each skill for upload to Claude

Workspaces receive copies, not links, so they work on any OS. `update`
overwrites only rule, skill, tool and template files, never accounts/ or
_shared/. If git is installed, init/demo/new-account/update also commit;
nothing depends on it. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_TARGETS = (".claude/skills", ".agents/skills")
RULE_FILES = ("POLICY.md", "CONVENTIONS.md")
WORKSPACE_FILES = ("AGENTS.md", "CLAUDE.md", "PROJECT-INSTRUCTIONS.md")


def refuse_inside_repo(ws: Path) -> None:
    ws = ws.resolve()
    if ws == REPO or REPO in ws.parents:
        sys.exit("Refusing: the workspace must live outside the Sales Copilot repository "
                 "(it is public; account data must never be inside it).")


def skills() -> list[Path]:
    return sorted(p for p in (REPO / "skills").iterdir() if (p / "SKILL.md").exists())


def copy_rules(ws: Path) -> None:
    for name in RULE_FILES:
        shutil.copy2(REPO / name, ws / name)
    for name in WORKSPACE_FILES:
        shutil.copy2(REPO / "templates/workspace" / name, ws / name)
    (ws / ".claude").mkdir(exist_ok=True)
    shutil.copy2(REPO / "templates/workspace/.claude/settings.json", ws / ".claude/settings.json")
    (ws / "tools").mkdir(exist_ok=True)
    shutil.copy2(REPO / "tools/lint.py", ws / "tools/lint.py")
    shutil.copy2(REPO / "viewer/account-desk.html", ws / "Account-Desk-Viewer.html")
    if (ws / "templates").exists():
        shutil.rmtree(ws / "templates")
    shutil.copytree(REPO / "templates", ws / "templates", ignore=shutil.ignore_patterns("workspace"))
    for target in SKILL_TARGETS:
        dest = ws / target
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(REPO / "skills", dest)


def build_empty(ws: Path) -> None:
    for sub in ("accounts", "_shared/products", "_shared/competitors", "_shared/value-propositions"):
        (ws / sub).mkdir(parents=True, exist_ok=True)
        (ws / sub / ".gitkeep").touch()
    copy_rules(ws)


def build_demo(ws: Path) -> None:
    shutil.copytree(REPO / "examples/demo-workspace", ws, dirs_exist_ok=True)
    shutil.copytree(REPO / "examples/demo-inputs", ws / "demo-inputs")
    shutil.copy2(REPO / "examples/DEMO-SCRIPT.md", ws / "DEMO-SCRIPT.md")
    copy_rules(ws)


def git(ws: Path, *args: str) -> None:
    if shutil.which("git"):
        subprocess.run(["git", "-C", str(ws), *args], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def commit(ws: Path, message: str, init: bool = False) -> None:
    if init:
        git(ws, "init", "-q")
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", message)


def fresh(ws: Path) -> Path:
    ws = ws.expanduser()
    refuse_inside_repo(ws)
    if ws.exists() and any(ws.iterdir()):
        sys.exit(f"{ws} exists and is not empty")
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def cmd_init(args: argparse.Namespace) -> None:
    ws = fresh(args.workspace)
    build_empty(ws)
    commit(ws, "init workspace", init=True)
    print(f"Workspace created at {ws}. Keep it private.")


def cmd_demo(args: argparse.Namespace) -> None:
    ws = fresh(args.workspace)
    build_demo(ws)
    commit(ws, "demo workspace (fictional data)", init=True)
    print(f"Demo workspace (fictional data) created at {ws}. Reference date: 2026-10-30.")


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
    commit(ws, f"new account: {slug}")
    print(f"Account created at {folder}")


def cmd_update(args: argparse.Namespace) -> None:
    ws: Path = args.workspace.expanduser()
    refuse_inside_repo(ws)
    if not (ws / "accounts").is_dir():
        sys.exit(f"{ws} does not look like a workspace (no accounts/ folder)")
    copy_rules(ws)
    commit(ws, "update rules and skills from Sales Copilot")
    print(f"Rules, skills, tools and templates refreshed in {ws}")


def zip_dir(src: Path, target: Path, root_name: str) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(src.rglob("*")):
            if f.is_file() and ".git" not in f.relative_to(src).parts:
                zf.write(f, Path(root_name) / f.relative_to(src))


def out_dir(arg: Path) -> Path:
    out = arg if arg.is_absolute() else REPO / arg
    out.mkdir(parents=True, exist_ok=True)
    return out


def package_skills(out: Path) -> list[Path]:
    made = []
    for skill in skills():
        target = out / f"{skill.name}.zip"
        zip_dir(skill, target, skill.name)
        made.append(target)
    return made


def cmd_package(args: argparse.Namespace) -> None:
    for target in package_skills(out_dir(args.out)):
        print(f"packaged {target.name}")


def cmd_release(args: argparse.Namespace) -> None:
    out = out_dir(args.out)
    made = []
    skill_dir = out / "skills"
    skill_dir.mkdir(exist_ok=True)
    made += package_skills(skill_dir)
    with zipfile.ZipFile(out / "sales-copilot-skills.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for z in sorted(skill_dir.glob("*.zip")):
            zf.write(z, z.name)
    made.append(out / "sales-copilot-skills.zip")
    with tempfile.TemporaryDirectory() as tmp:
        empty, demo, rules = Path(tmp, "empty"), Path(tmp, "demo"), Path(tmp, "rules")
        for p in (empty, demo, rules):
            p.mkdir()
        build_empty(empty)
        build_demo(demo)
        copy_rules(rules)
        for src, name, root in ((empty, "sales-copilot-workspace.zip", "AccountDesk"),
                                (demo, "sales-copilot-demo-workspace.zip", "AccountDesk-demo"),
                                (rules, "sales-copilot-rules-update.zip", "AccountDesk")):
            zip_dir(src, out / name, root)
            made.append(out / name)
    for m in made:
        print(f"built {m.relative_to(out)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("release"); p.add_argument("--out", type=Path, default=Path("dist"))
    p.set_defaults(fn=cmd_release)
    p = sub.add_parser("init"); p.add_argument("workspace", type=Path); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("demo"); p.add_argument("workspace", type=Path); p.set_defaults(fn=cmd_demo)
    p = sub.add_parser("new-account"); p.add_argument("workspace", type=Path)
    p.add_argument("slug"); p.add_argument("--name"); p.set_defaults(fn=cmd_new_account)
    p = sub.add_parser("update"); p.add_argument("workspace", type=Path); p.set_defaults(fn=cmd_update)
    p = sub.add_parser("package"); p.add_argument("--out", type=Path, default=Path("dist"))
    p.set_defaults(fn=cmd_package)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
