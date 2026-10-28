---
title: 'READMEs for the addon and the workbook script'
type: 'chore'
ticket: ''
created: '2026-10-28'
status: 'built'
baseline_revision: 'cb02231'
route: 'oneshot'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Both READMEs are stale. The root one still describes the 1.1.0 attendance/loot ratio, SavedVariables and `sample_json`. The script one lists English menu items that no longer exist and says nothing about clasp setup.

**Approach:**
- Rewrite `README.md` (repo root) for the 2.0.0 companion: install, snapshot import, both columns, treatment popup and `/preloot`, chat line, Gargul export settings, Gargul version tolerance, session-only behaviour, offline tests and the test payload.
- Rewrite `tools/google_apps_script/README.md` as the setup and usage guide: the clasp setup (the deferred 4.1 item), the French menu, the tabs, the raid flow, WCL credentials and the browser tests.
- English prose, with menu and tab labels exactly as they appear in French.
- These are the README parts of 5.7 and 4.10, done early at the owner's request (2026-10-28).

</frozen-after-approval>

## Implementation Notes

- Oneshot: documentation only, no code.

## Review Triage Log

Quick review: 8 findings, all confirmed against the source and fixed.

- **medium, patch.** "Opening a page in a browser works too" was wrong for the pages that read fixtures; now 4-3, 4-4, 4-6 and 4-7 need `--allow-file-access-from-files`.
- **medium, patch.** Nouveau palier: live Objets tabs are emptied, and the archive is warning-protected, not read-only.
- **medium, patch.** `/reload` also drops the snapshot: re-import (Démarrer exports the same raid ID), and earlier awards no longer count in the columns.
- **low, patch.** An empty treatment is not refused; it is picked in the Terminer preview. Only the empty `raidId` needs typing.
- **low, patch.** The `clasp create` advice was wrong; replaced with File > Make a copy plus new IDs in `.clasp.json`.
- **low, patch.** Supprimer lists every Raids row, and choosing the open raid cancels it.
- **low, patch.** Mettre à jour les parses WCL needs Serveur WCL and the credentials, and is refused during a raid.
- **low, patch.** The Close button is shown as **Fermer** on the French client.

## Verification

**Manual checks (if no CLI):**
- Every menu label, tab name, slash command, file name and command in the READMEs matches the source (`menu.js`, `schema.js`, the TOC, `Picker.lua`, `Core.lua`, `tests/`).
