# Design rationale

Why the desk is built the way it is. The rules themselves are in CONVENTIONS.md and POLICY.md.

## The problem

Key-account work in long, stakeholder-heavy sales cycles is information-heavy: mails, meeting notes, delivery status, news, product material. Account plans exist but go stale; the published practitioner research points to execution and coverage, not missing information, as the usual failure (plans not followed through, deals depending on a single contact, internal coordination). An assistant helps most where the work is detection and collation — keeping the memory current, noticing gaps and expiry, preparing material — and least where it is judgment: whom to win over, what to offer, how to build consensus.

## Why files, not a database or a vendor memory

- The account manager can read and correct everything in any editor.
- Any model or harness can work on the same folder; switching costs a configuration file, not a migration.
- The audit trail needs no tool: every skill run writes a run-log line naming the records it changed, and every material change keeps the old value in History. A synced folder (e.g. OneDrive) adds file versions; git can be used but is not required.
- Experienced sellers keep a personal working memory next to the company CRM. Making it explicit, structured and private is more honest than pretending it does not exist, and the proposal mechanism gives the CRM a cleaner path than the status quo.

## Why head and history

Long relationships accumulate detail. If the assistant reads the full log as state, everything it ever noted stays "true". Separating a short Current section from an append-only History, and building reminders only from Current, keeps detail available without letting it pose as the present. Published evaluations of agent memory systems report that showing superseded versions at answer time lowers accuracy; showing the current state plus short change notes performs better.

## Why leases and a reminder budget

Intense phases (a tender, a pilot, an escalation) produce many small items. When the account moves on, those items turn into noise. Leases make forgetting the default: an item that is not reconfirmed stops being surfaced and is listed once for disposition. Episodes put the boundary of a phase into the file structure, and `/rebase` turns "a lot changed" into one confirmable batch. The reminder budget caps noise even when hygiene slips.

## Why no outbound channel

An assistant that reads untrusted content (mail, documents, web pages), has access to private data and can communicate externally can be steered by injected text to leak that data. Removing the outbound leg — no send tools, no CRM writes, web research restricted to public identifiers — removes the class of attack instead of filtering it. Instructions found in input are reported, not followed.

## Known limits

- The skills rely on the model following procedures; the linter catches format errors, not wrong judgments.
- Portability covers skills and memory, not permissions: each harness needs its own enforcement configuration.
- Without mailbox or CRM connectors, completeness depends on what the account manager drops in.
