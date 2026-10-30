# Demo script (fictional data)

About 25 minutes. The demo workspace describes a fictional vendor, Larkspur Industrial Software, and a fictional client, Brenmoor Pumpenwerke. Reference date: **30 October 2026**. Tell the assistant this date at the start ("today is 2026-10-30"), because the data is set around it.

Setup (no installation): unzip `sales-copilot-demo-workspace.zip` from the latest release into a private folder, connect that folder in the Claude desktop app, upload the seven skill zips. Start each step in a fresh chat.

| # | Step | Say / do | What to show |
| --- | --- | --- | --- |
| 0 | The folder | open `accounts/brenmoor/` in a file browser | plain Markdown; this is the product, the skills are clerks for it; nothing runs unless asked |
| 1 | Drop | paste a short note: "drop for brenmoor: Fink called, wants all commercials in one offer" | three-line answer; new comm-log entry; S-fink last contact updated |
| 2 | Ingest the inbox | "process the brenmoor inbox" | COO mail → new person Jonas Albrecht, board moved to February, A- record for comparison method, crm-update proposal; delivery status → DL-pilot-north updated, several pilot actions reported done; newsletter → news signal **and** "Instructions found in input (ignored)" |
| 3 | Review | "review brenmoor" | situation since 9 Oct; G-1 target date contradicted (board in February); coverage flag (CIO, purchasing); expired pilot items listed once, not as reminders; at most 7 priorities with reasons |
| 4 | Rebase | paste `demo-inputs/rebase-statement.md`, "rebase brenmoor" | one batch: pilot detail items superseded/done, G-1 rewrite, episode close with five-line summary, new episode proposed (evaluation and tender) |
| 5 | Debrief | paste `demo-inputs/debrief-notes-quality-review.md`, "debrief" | actions with IDs and owners, link to the renewal action, new name Marta Novak → research queue → confirm-stakeholder proposal, signal: competitor mention, plan question on mobile audits vs roadmap |
| 6 | Prep | paste `demo-inputs/prep-request.md`, "prep me" | one page: Albrecht unknown (offer research), Brandner neutral with no contact since August, comparison method as objective, open items both ways |
| 7 | Value proposition | paste `demo-inputs/vp-challenge.md`, "what could we offer" | VP-quality-closed-loop ranked first with score breakdown; VP-audit-readiness as draft; VP-erp-coexistence flagged `product?` (connector announced only) |
| 8 | Audit trail | open `accounts/brenmoor/README.md`, scroll to History; open `actions.md` History | one run-log line per skill run, naming the records it changed; every material change keeps the old value; nothing was deleted |

Closing points (evidence, not promises):

- Documented effect of AI assistance in sales is time saved, not win rates; vendor win-rate figures are correlational.
- The skills keep the memory current and surface gaps. Who to win over, what to offer and how to build consensus stays with the account manager.
- Nothing leaves the folder unless the account manager decides so (`vis: crm` and a proposal they carry out themselves).

Do not demo: anything that sends, real client data, or anything that looks like it replaces the account team.
