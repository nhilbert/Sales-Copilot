---
name: rebase
description: After a phase change on an account (a workshop, a decision, a reorganisation, a delivery leap, a tender step), re-disposition every open item in one batch, keep, superseded, park, rewrite or done, list contradictions with the plan, and open or close episodes. Use when the account manager says "things have moved on", "rebase", "a lot changed", "clean up after the workshop", "close the episode", or when /review shows many expired or stale items.
---

# Rebase

Detail from an intense phase turns into noise once the account has moved on. Rebase backs out of the detail in minutes: the account manager states what changed, the skill proposes a disposition for every open item, the account manager confirms in one pass.

## Inputs

A statement of what changed, in the account manager's words, e.g. "The workshop settled the architecture; the pilot is off; the decision moves to the board in Q1." If missing, ask for it — this skill does not guess what changed.

## Steps

1. Read `POLICY.md`, `CONVENTIONS.md`. Run `ingest` first if `inbox/` is not empty.
2. Record the statement: History entry in `account-plan.md`: `- <date> · phase change: <statement> {src: me <date>; vis: private}`.
3. Collect every open item from Current: A- (open, waiting), Q- (open), N- (watch), DL- (not closed), G- (not done/dropped), the Priorities list, P- (open), AVP- (candidate, active), and every open episode.
4. For each item propose one disposition, with a one-line reason that refers to the statement or to a record:
   - `keep` — still valid as it is (renew lease if expired)
   - `rewrite` — still relevant but the text, owner or date must change (give the new text)
   - `superseded` — overtaken by the change (say by what)
   - `park` — not now, may come back (no lease, stays searchable)
   - `done` — achieved or answered (cite evidence)
5. **Contradictions**: list statements in Current (client strategy, goals, stakeholder stance, account value proposition) that conflict with the statement. Each as a proposed rewrite.
6. **Episodes**: for each open episode, propose `close` or `keep open`. For a close, draft the five-line summary (what the phase was for, what came out, what carries forward, what was dropped, open risks).
7. **New episode**: if the statement opens an intense phase, propose opening one (`E-<yyyymm>-<slug>`, purpose in one line).

## Output (for confirmation)

Group by disposition, most consequential first: superseded, park, rewrite, done, keep. One line per item: `ID · title · → disposition · reason`. Then contradictions, then episode proposals.

Ask once: "Apply all, or list the IDs to change?"

## Apply (after confirmation)

- `superseded` → `status: dropped`, History entry `superseded by <statement or ID>`.
- `park` → `status: parked`, remove `review_by`, History entry.
- `rewrite` → old values to History, new values into the record, new lease.
- `done` → status done/answered with evidence in History.
- `keep` → renew `review_by` if expired.
- Episodes: write the summary into `account-plan.md` History, set `status: closed` and `closed:` in the episode file, move it to `archive/episodes/`, remove it from the Episodes list. New episode: create from `templates/episode/episode.md`, list it under Episodes.
- Update `phase:` in `README.md` if the statement changes it. Commit `rebase: <slug> <date>`.

## Never

- Drop items without listing them for confirmation.
- Delete anything. Superseded and parked items stay in the files.
- Apply a partial set silently; if the account manager changes some items, re-list the final set before writing.
