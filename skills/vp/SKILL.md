---
name: vp
description: Match a client challenge against the value-proposition library and current product material, rank candidates with proof and gaps, flag misalignment, and draft new library entries where nothing fits. Also checks the library for entries no longer backed by product material. Use when the account manager says "what could we offer for", "value proposition for", "check the VP library", or pastes a client challenge.
---

# Value propositions

The account manager curates the library in `_shared/value-propositions/`. This skill finds, ranks, checks and drafts. It never marks an entry `validated` and never decides what is offered to a client.

## Modes

- **match** (default): a challenge, optionally for an account.
- **check**: audit the library against product material.

## Match

1. Read `POLICY.md`, `CONVENTIONS.md`.
2. Read every library entry's front matter and Challenge, Offer, Proof, Fit conditions sections; every file in `_shared/products/` (capabilities and their status); if an account is given: `value-proposition.md`, `account-plan.md` Goals, `stakeholders.md` (roles), `roadmap.md`.
3. Restate the challenge in one sentence, in the client's terms. If it is really two challenges, split it.
4. Score each library entry (show the numbers):
   - challenge fit 0–3 (pattern match against `challenge_patterns` and Challenge text)
   - product backing 0–2 (2 = all products `current` with the capability generally available; 1 = announced/roadmap; 0 = not found in product material)
   - proof 0–2 (2 = proof in a comparable segment; 1 = any proof; 0 = none)
   - buyer fit 0–1 (entry's `buyer_roles` present among the account's stakeholders)
   - minus 1 for each fit condition the account visibly fails
5. Rank. Show the top five with score ≥ 3. For each: why it fits, the proof, what is missing, and flags:
   - `product?` — the entry relies on a capability not found as generally available
   - `stale` — `updated` older than 180 days
   - `unproven` — status `validated` but no proof listed
6. If no entry reaches 3, or the account manager asks: draft a new entry from `templates/shared/value-proposition-entry.md` as `_shared/value-propositions/VP-<slug>.md` with `status: draft`, every unknown written `unknown`, products only from product files. Say clearly that it is a draft.
7. Search parked AVP- records and `used_at` lists for earlier use at other accounts; mention them ("used at <slug>: <outcome if recorded>").
8. If an account is given, offer to add the chosen candidates as AVP- records with `status: candidate` — write only on confirmation.
9. If you wrote anything: self-check (CONVENTIONS §14); add a History line to each draft entry; if an account is given, append the run log line to its `README.md` History.

## Check

For every library entry: products still present and `current`? capabilities still generally available? proof present for `validated`? `updated` within 180 days? Output a table: entry · status · issues · suggested action. Write nothing; the account manager decides.

## Output

Match: the restated challenge, the ranked table (entry · score breakdown · flags), then for the top three a short paragraph each, then drafts created (if any).

## Never

- Invent numbers, references or capabilities. Missing proof is reported as missing.
- Copy client-specific details into library entries. Library entries are generic; client specifics stay in the account's `value-proposition.md`.
- Mark anything `validated`.
