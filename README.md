# Sales Copilot

Skills, conventions and templates for a personal, file-based key-account desk run with an AI assistant (Claude, or any harness that reads [Agent Skills](https://agentskills.io)).

The account memory is a folder of plain Markdown files. The assistant is a clerk for that folder: it files what you drop, prepares you for meetings, brings you up to speed on an account, turns meeting notes into actions, and matches client challenges against your value-proposition library. It never sends anything to anyone and never writes to a CRM.

> **This repository contains no account data, and must never contain any.** Real accounts live in a private workspace outside the repository. The only example data is fictional (`examples/`).

## What it does

| Skill | You say | You get |
| --- | --- | --- |
| `drop` | "drop this into <account>" + a mail, file or note | filed in the account's inbox and processed; three-line answer |
| `ingest` | "process the inbox" (also called by the others) | comm-log, stakeholder, action, delivery and proposal updates; injected instructions reported, not followed |
| `prep` | "prep me for the meeting with …" | one page: people, where we stand, what they will raise, what we want, open items, questions (read-only) |
| `review` | "review <account>", "get me up to speed" | situation, plan vs reality, decisions you must make, expired items, at most N priorities with reasons |
| `debrief` | meeting notes + "debrief" | actions with IDs and dependencies, decisions, new people, value-proposition signals, public-source research |
| `vp` | a client challenge | ranked value propositions from your library, with proof, gaps and product-alignment flags; drafts where nothing fits |
| `rebase` | "a lot changed: …" | every open item re-dispositioned in one batch (keep, rewrite, superseded, park, done); episodes closed |

## Design in five rules

1. **Files are the system.** One folder per account, Markdown with YAML front matter, one git repository. Any editor, any model.
2. **Head and history.** Each file has `## Current` (what is true now) and an append-only `## History`. Reminders come only from Current.
3. **Leases.** Actions, questions, signals and delivery items carry `review_by`. Expired items are not reminders; they are listed once for confirm, park or drop. A reminder budget caps every list.
4. **Propose, don't act.** CRM updates, goal changes, merges and inferred people are proposals the account manager decides on.
5. **Private by default.** Every entry carries `vis: private | team | crm`. Nothing reaches the CRM unless the account manager marks it `crm` and enters it.

Details: [CONVENTIONS.md](CONVENTIONS.md) (file format), [POLICY.md](POLICY.md) (hard rules), [docs/design.md](docs/design.md) (rationale).

## Quick start

Requires Python 3.9+ and git.

```bash
git clone https://github.com/nhilbert/Sales-Copilot.git
cd Sales-Copilot

# a private workspace OUTSIDE this repository
python3 tools/desk.py init ~/AccountDesk
python3 tools/desk.py new-account ~/AccountDesk example-co --name "Example Co"

# or the fictional demo
python3 tools/desk.py demo ~/AccountDesk-demo

# check a workspace
python3 tools/lint.py ~/AccountDesk/accounts
```

The workspace gets copies of the rules, templates, linter and skills (`.claude/skills/`, `.agents/skills/`). `python3 tools/desk.py update <workspace>` refreshes them later without touching accounts.

### Using it with Claude

- **Claude desktop app**: connect the workspace folder. Install the skills from `python3 tools/desk.py package` (one zip per skill in `dist/`) via the app's skill settings. Start each task in a fresh chat; the files carry the state.
- **Claude Code**: run `claude` inside the workspace. `CLAUDE.md`, the skills and `.claude/settings.json` (deny rules for policy files, `rm`, `curl`, `git push`) are picked up automatically.

### Other harnesses

The skills follow the Agent Skills format (`SKILL.md` with `name` and `description`). They are copied to `.agents/skills/` and `.claude/skills/`, which Codex CLI, goose, opencode and OpenHands read; `AGENTS.md` is the shared instruction file. Permission rules are not portable: re-create the rules in POLICY.md's enforcement table for each harness.

## Keeping the public repository clean

- `tools/desk.py` refuses to create a workspace inside this repository.
- `.gitignore` blocks `accounts/`, `inbox/`, `archive/` and mail or export files outside `examples/`.
- `tools/public_guard.py` checks staged files against a private denylist kept outside the repository (`~/.config/sales-copilot/denylist.txt`) and can run as a pre-commit hook. It reports only the term's line number, never the term.

## Status

Early. The skills are written and the example lints clean; they have not yet been tuned on real use. Expect a week of iteration per skill. Model-specific adjustments go into [MODEL-NOTES.md](MODEL-NOTES.md).

## Credits

Ideas borrowed, no code copied:

- [Agent Skills](https://agentskills.io) open standard — skill format and progressive loading.
- Anthropic [knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (sales) — shape of call prep, call summary and account planning skills.
- [orbit](https://github.com/tobiaswuerth/orbit) — a source for every fact; read-only access as a first-class mode.
- [mem0](https://docs.mem0.ai/platform/features/expiration-date) — expiry dates on memories (here: leases). [Graphiti](https://github.com/getzep/graphiti) — invalidate instead of delete. [Letta MemFS](https://docs.letta.com/letta-code/memfs) — git-backed Markdown memory and consolidation passes.
- Simon Willison, ["The lethal trifecta"](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (2025), and [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — why the desk has no outbound channel.
- Sales practice: buying roles after Miller Heiman *Strategic Selling*; qualification ideas from MEDDPICC; account-plan components after SAMA; value word equations after Anderson, Narus and Van Rossum, "Customer Value Propositions in Business Markets", *HBR* 2006. No trademarked templates are reproduced.

## Licence

[MIT](LICENSE).
