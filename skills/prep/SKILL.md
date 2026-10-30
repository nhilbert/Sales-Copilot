---
name: prep
description: Prepare the account manager for an upcoming meeting with one page, the people, where we stand, what they will raise, what we want, open items both ways, questions to ask. Read-only. Use when they say "prep me for", "meeting with X tomorrow", "what do I need to know before", or paste a calendar invitation.
---

# Prep

One page before a meeting. Read-only: this skill changes no files unless the account manager asks to save the page.

## Inputs

- Account, meeting date, attendees (names or roles), purpose. Take what the request or a pasted invitation gives. If attendees or purpose are missing, ask once; if still missing, prepare for the account in general and say so.

## Steps

1. Read `POLICY.md` and `CONVENTIONS.md`.
2. If `inbox/` is not empty, ask whether to ingest first (it changes files). Do not ingest silently.
3. **People**: match attendees to S- records. For each: role, buying role, influence, stance, personal win, last contact, and their last three History entries. Unknown attendee → say so; offer research (public role only, POLICY 6–7) and run it only if accepted.
4. **Since last contact** with these people: comm-log entries, decisions, delivery changes, news (N-) about their company or unit.
5. **Open items both ways**: open A- records where they are owner or stakeholder (what they owe us) and where `owner: me` concerns them (what we owe them). Flag overdue ones.
6. **What we want**: goals (G-) and active AVP- records that concern these people's roles or units. Propose a meeting objective in one sentence if the account manager has not stated one.
7. **What they will likely raise**: open delivery issues (DL- amber/red), unanswered questions they asked, objections recorded as `signal:` entries.
8. **Parked but possibly relevant**: search parked and dropped records and `archive/episodes/` for these stakeholders and topics; list at most three, marked "parked".
9. Respect the reminder budget for open items; show the rest as a count.

## Output (one page)

```text
Meeting: <name> · <date> · <attendees>
Objective (proposed): <one sentence>

People
- <Name> (<role>) — stance · influence · last contact <date> · cares about … · personal win …

Where we stand            — 3–5 lines, with record IDs
What they will raise      — bullets
What we want out of it    — bullets, tied to G-/AVP- IDs
Open items                — we owe · they owe (IDs, due)
Questions to ask          — 3–5
Watch-outs                — risks, sensitivities, contradictions
Parked, maybe relevant    — at most 3
```

Every statement carries the record ID or source it came from.

## Never

- Write files without an explicit request. If asked to save: `accounts/<slug>/reviews/prep-<date>-<meeting-slug>.md`.
- Draft messages to the attendees.
