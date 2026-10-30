---
name: new-account
description: Create a new account folder in the account workspace from the templates. Use when the account manager says "new account", "set up an account for", "add <company> as an account". Needs only file read and write.
---

# New account

## Steps

1. Read `POLICY.md` and `CONVENTIONS.md` at the workspace root.
2. Ask for the display name if not given. Derive the slug: drop legal-form suffixes (Ltd, GmbH, AG, Inc, SA, …), then lowercase, letters, digits and hyphens only (e.g. "Example Industries Ltd" → `example-industries`). Show the slug; if the folder `accounts/<slug>/` exists, stop and say so.
3. Create `accounts/<slug>/` with the subfolders `inbox/`, `archive/`, `episodes/`, `reviews/` (if empty folders cannot be created, create each with an empty `.gitkeep` file).
4. For every file in `templates/account/`: copy it into `accounts/<slug>/`, replacing `{{account}}` with the slug, `{{name}}` with the display name, `{{date}}` with today's date.
5. Append to `README.md` History: `- <today> · run: new-account · created {src: me <today>; vis: private}`.
6. Self-check (CONVENTIONS §14).

## Output

One line: folder created, and the next useful step ("drop anything you have on this account into its inbox, or tell me the goals").

## Never

- Fill in goals, stakeholders or other content from memory or the web. The account starts empty.
