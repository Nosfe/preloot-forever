# Acceptance Criteria

Testable conditions for each capability. Terms are from [glossary.md](glossary.md). Where a stage owns the behavior, it is named in brackets from [architecture-preloot.md](../architecture-preloot/architecture-preloot.md).

## CAP-1 — Select Target Phase [cli]
- Target P2 → Previous P1; P3 → P2; P4 → P3; P5 → P4.
- Target P1 → the Baseline Sets come from the pre-raid BiS Lists.
- Both Phases are written to the run settings and never change during the run.

## CAP-2 — Load BiS Lists [ingest_bis]
- Lists are loaded for every DPS and Healer Spec, for both the Target Phase and the Previous Phase.
- No Tank Spec list is loaded.
- A Spec with no list for either Phase gets an Issue and is skipped. The run continues.
- The fetch timestamp is recorded and shown in the report.

## CAP-3 — Resolve items [resolve_items]
- Every BiS List item maps to a wowsims item ID, slot and drop source (boss and zone), or gets an Issue with its Spec and slot.
- The report shows the name-to-ID match rate for each Spec. Only 170 of 448 wowtbc.gg items carry an ID, so name matching does most of the work.
- A match is accepted only if the item's wowsims phase is at or before the Target Phase.
- Heroic and normal versions resolve to different IDs. When the BiS List context doesn't say which is meant, the item is reported as unresolved.
- `db.json` comes from the same wowsims release as the bundled `wowsimcli.exe`.

## CAP-4 — Detect Contested Items [detect_contested]
- An item on the Target Phase BiS Lists of two or more Specs of the same Role is contested.
- Two Specs of the same class count as contesting (e.g. Fury and Arms Warrior), even though both sim as wowsims `dps_warrior`.
- An item on only one Spec's BiS List is excluded from the Priority Table.
- Items not on any Target Phase BiS List are never considered.
- An item on both DPS and Healer BiS Lists is ranked separately in each Role and flagged.

## CAP-5 — Upgrade simulation [plan_sims, simulate, rank]
- Upgrade Value = (sim with item − Baseline Set sim) / Baseline Set sim. Raw Gain is recorded next to every Upgrade Value.
- DPS Specs use DPS; Healer Specs use HPS.
- The baseline and the candidate sims use the same random seed and the same number of iterations.
- The encounter is a single-target Patchwerk fight lasting 2–3 minutes; the wowsims default encounter is acceptable.
- Gems and enchants use the wowsims defaults for both the Baseline Set and the Contested Item.
- For paired slots (rings, trinkets, one-hand weapons), each slot is handled on its own. The Contested Item is simmed in every slot it fits. The other slot takes every option: the Baseline Set item and each Target Phase BiS List option for that slot. Every combination is simmed.
- The best combination sets the ranking Upgrade Value. Every combination's result is kept in the run output.
- The iterations, seed, encounter and wowsims version are recorded and shown in the report.
- There is no cap on the number of sims.

## CAP-6 — Ranking and Tie-Break [fetch_parses, rank]
- Specs are ordered by Upgrade Value, highest first.
- Upgrade Values within the sim error margin are tied. Tied Specs are ordered by the higher Raw Gain.
- If the Raw Gain is also within the error margin, the higher Warcraft Logs top-percentile parse ranks first. Parses come from the TBC Anniversary Previous Phase (P3 for a P4 Target Phase).
- If Warcraft Logs data is unavailable, the tie is shown as unresolved and the run is not blocked.
- The Priority Table shows which rule settled each tie.

## CAP-7 — Priority Table and CSV [rank, render]
- There is one row per Contested Item: item, slot, drop source, and the competing Specs ranked with their Upgrade Value and Raw Gain.
- Rows are grouped by Role (DPS, Healer).
- CSV: one row per (Contested Item, Spec). Columns: item ID, item name, slot, drop source, Role, Spec, rank, Upgrade Value, Raw Gain, tie-break rule applied.
- The CSV and the HTML use the same order.

## CAP-8 — HTML report [render]
- It is a single HTML file with all CSS and JS built in, no external scripts or fonts, and it opens offline.
- Tabs: Priority Table, Contested Items, BiS Lists.
- Each Spec is shown in its class color, and each Upgrade Value is color-coded by size.
- Each item name links to its Wowhead TBC item page. The link is a hyperlink only; no Wowhead data is fetched.
- Each row shows the drop source (boss and zone).
- Healer rows carry the label "alpha sim".
- A separate section lists Issues and match rates.
- It shows provenance: the fetch timestamps, the wowsims version and the sim settings.
- It credits its sources: wowsims (MIT, with a link to the project), wowtbc.gg BiS Lists and Warcraft Logs.
- Text taken from sources is HTML-escaped.

## CAP-9 — Resume [simulate, cli]
- Restarting with identical settings resumes the latest run. Changed settings start a new run.
- Completed sims are never run again. A truncated last result is discarded and that sim runs again.
- A stage whose output already exists is skipped. A partial write never leaves a file that looks complete.

## CAP-10 — Portable executable [packaging]
- A PyInstaller one-folder bundle, built on Windows and zipped, with `wowsimcli.exe` included.
- It runs on Windows 11 x64 with no Python installed.
- It never writes into its own folder. All state lives in the `--workspace` folder.
- Warcraft Logs credentials are read from `<workspace>/secrets/` or environment variables, and never appear in artifacts or logs.
