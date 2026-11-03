---
title: 'Raider portal (read-only web app)'
type: 'feature'
created: '2026-11-03'
status: 'built'
route: 'full'
---

## Intent

Give raiders a readable page without showing the workbook. Owner choices (2026-11-03): all of Classement Impact, Roster numbers, tier loots, raid-by-raid presence and tier items; access for anyone with the link (no Google account); a "Mon personnage" view; no raid-group filter.

## Design

- `src/webapp.js`: `doGet` serves `portal.html`; `getRaiderPortalData` returns one JSON (cached 60 s in the script cache) built from Roster (`buildSnapshotRaiders_`), Objets (`buildSnapshotItems_` + `addImpactScores_`, same formula as the snapshot), Awards (any award of an item marks it owned, like the Classement Impact tab; tier loots from Config's start, blank date = raid date) and Présence (tier raids). Never Config settings or WCL data.
- `src/portal.html`: French single page, tabs Mon personnage / Classement Impact / Roster (sortable) / Loots (raider filter) / Présence / Objets (spec filter). DOM built with `textContent` only. Class colours as the Présence headers, gold/silver/bronze for the top 3.
- `appsscript.json` `webapp`: `USER_DEPLOYING`, `ANYONE_ANONYMOUS`. `.claspignore` now uploads `portal.html`.
- Deployment `AKfycbxO3nq95bWjdMoIPlr59qulz0l859O1ZNCMaR3JPYZgmxJljYxdIs7DqTeiG9ypdXeqmQ` (version 1); update with `clasp deploy -i <id>`.

## Verification

- `tests/portal.html` PASS (data fields, no Config leak, owned rule, tier filters, manifest, no HTML injection); story-4-1 PASS.
- Local render with sample data checked (Mon personnage view).
- Owner: open the link, pick a name, check each tab against the workbook.
