---
title: 'Warcraft Logs attendance import'
type: 'feature'
ticket: '4'
created: '2026-10-22'
status: done
baseline_revision: '2d9cdf4d030771bf16b3e50218473bed4496daec' # C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** After a raid, the owner fills Présence by hand, and nothing ends the started raid. Nothing reads the Warcraft Logs report to credit attendance or to fill in the raid's Date and Instance.

**Approach:** Two owner menu actions.
- **Set WCL credentials** opens a dialog (client ID plus a masked secret) and stores them in the owner's User Properties.
- **End raid** opens one window for the started raid (Config Raid ouvert) with a **WCL link** field (required, exactly one report) and a **Gargul export** box. One click does everything below in one batch:
  1. fetches the pasted report;
  2. credits `1` in the raid's Présence row for each roster raider present in more than 25% of the distinct completed boss pulls;
  3. adds that Présence row and fills the raid's Date and Instance;
  4. writes the report code in Rapports WCL with an Importé le timestamp;
  5. ends the raid: clears Raid ouvert and removes the `Raid ouvert` protections (`buildRaidProtectionDeleteRequests_`).

**Decisions (owner, 2026-10-22):**
- **One window, built in two steps:**
  - 4.4 builds the End raid window, the WCL part and the raid end.
  - The Gargul box only accepts empty text, meaning a raid with no awards. Any text is refused with "import du loot Gargul : story 4.7".
  - 4.7 later plugs the loot import into the same window and batch.
- **No separate import:** exactly one WCL link is required at End raid (owner decision), and there is no separate WCL import action. A second report is out of scope; the owner fixes Présence by hand.
- **End raid with no started raid:** an alert says to start the raid first, and nothing is written.
- **Pulls:**
  - Boss fights (`encounterID > 0`, not `inProgress`, kills and wipes) of the report are counted.
  - When the report has no boss fight, every completed fight counts.
- **Instance and Date:**
  - Instance = the WCL zone name as given.
  - Date = the report start, as a date in the script time zone.
  - Both are written only where the cell is empty, in both the Raids row and the Présence row.
- **Credit:**
  - A name resolves through `resolveAttendanceKey_`: an exact roster key, or a Rerolls alt mapped to its main.
  - A raider is credited when the main or any of its alts is in a strictly greater share than 25% of pulls.
  - A `B` is never overwritten, and nothing writes `0`.
  - Unmatched names are listed in the result, not written.
- **Cleanup:**
  - Delete `legacy/attendance.js`, `legacy/test_runner.html`, `legacy/presence_test_runner.html`, `generate_raid_json.ps1`, `run_local.cmd`, `.env.example` and `raid_ids.csv`.
  - Remove their mentions from `README.md`.
- **Menu labels:**
  - Start raid (export snapshot)
  - Cancel started raid
  - End raid
  - Set WCL credentials
  - Set up / refresh workbook and Archive tier and activate next stay as they are.
  - `End raid` calls `endRaid()` in `attendance.js`. The `importRaidLedger` stub is removed from `ledger.js`, which 4.7 fills with the loot import used by `endRaid()`.
- **Earlier owner choices that still apply:** the report link is pasted in the window (not in a cell); the WCL zone name is kept as is; the legacy files are deleted.

## Boundaries & Constraints

**Always:**
- Hold the document lock and use one `applyBatch_` per End raid. Validate and fetch before writing; any failure writes nothing and keeps the raid started.
- Secrets only in `PropertiesService.getUserProperties()`; never in cells, logs or alerts.
- The WCL token comes from the client-credentials flow, via `UrlFetchApp` with `muteHttpExceptions`.
- Exact names, with no case folding.
- French accents are kept; comments are one short line.

**Never:**
- No Script Properties, no Drive output, no date cutoffs.
- No writes to Awards, Roster or Objets.
- No change to the score formulas.
- No ledger parsing (4.7), and no writes to Awards.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Started raid 5 (Raids row ID only, no Présence row), 1 report: 4 boss pulls; Ana 4/4, Bob 1/4, alt Zed (main Cid) 2/4, Unknown 4/4; empty Gargul box | Présence row `5`, zone, date; Ana and Cid `1`, Bob blank; Raids row gets the code, date, zone and timestamp; Raid ouvert cleared; protections removed; result lists Unknown | — |
| Two links | WCL field holds two report codes | Nothing written | Alert: only one WCL link |
| Présence row exists | Row for raid 5 already exists, with Cid `B` and a typed Date | `B` and Date kept; others credited in that row | — |
| No started raid | Raid ouvert empty | Nothing written | Alert: start the raid first |
| Gargul text | Gargul box not empty | Nothing written; raid stays started | Alert: Gargul loot import comes with 4.7 |
| No link | WCL field empty or with no report code | Nothing written | Alert: WCL link required / not recognised |
| No credentials | User Properties empty | Nothing fetched or written | Alert: Set WCL credentials |
| WCL error | Token or report HTTP error, or unknown code | Nothing written; raid stays started | Alert with WCL status, no secret |
| No raider column | A matched raider has no Présence column | Others credited | Result says to run setup |

</frozen-after-approval>

## Code Map

- `src/attendance.js` -- currently the stub `runAttendanceSync()`. Replace it with:
  - the actions: `endRaid()` opens the End raid window (it shows the started raid's ID); `setWclCredentials()` opens the credentials dialog;
  - the server functions called by `google.script.run`: `saveWclCredentials(clientId, clientSecret)` and `submitEndRaid(linkText, gargulText)`, which returns a message or throws;
  - pure helpers: `extractReportCode_` (exactly one code, else an error), `buildRaidPulls_(report)`, `creditedRaiders_(pulls, rosterIndex)`, `buildEndRaidRequests_`.
  - Legacy reference to copy and adapt, not load: `legacy/attendance.js` `extractReportCode_` (regex `/\/reports\/([A-Za-z0-9]+)/i`, or bare alphanumeric), the token POST to `https://www.warcraftlogs.com/oauth/token` (Basic auth, `grant_type=client_credentials`), and the GraphQL query at `https://www.warcraftlogs.com/api/v2/client` with `report(code, allowUnlisted: true) { code startTime endTime zone { name } masterData(translate: true) { actors(type: "Player") { id name } } fights { id encounterID kill inProgress startTime endTime friendlyPlayers } }`.
- `src/ledger.js` -- remove the `importRaidLedger` stub; the file stays for 4.7.
- `src/snapshot.js` -- reuse `buildRaidProtectionDeleteRequests_`. The Config Raid ouvert clear uses the same pattern as `cancelOpenRaid`.
- `src/roster.js` -- reuse `readRosterIndex_()` / `requireRosterIndex_()` and `resolveAttendanceKey_(index, name)` (exact key or the alt's main, else null).
- `src/snapshot.js` -- reuse `snapshotSheet_`, `requireCurrentLayout_` (Config, Raids, Roster) and `normalizeCellString_`.
- `src/schema.js` -- Raids keys `raidId`, `instance`, `raidDate`, `reportCodes`, `importedAt`; Config `openRaidId`; `PRESENCE_RAID_ID_COLUMN`, `PRESENCE_DATE_COLUMN`, `PRESENCE_FIRST_RAIDER_COLUMN`, `PRESENCE_FIRST_RAID_ROW`; the Présence instance column is index 1.
- `src/menu.js` -- labels per the Intent decisions.
- `tests/harness.js`:
  - add `UrlFetchApp.fetch` with scripted responses (`TracerHarness.setFetchResponses`) and a request log;
  - add `PropertiesService.getUserProperties()` (`getProperty`/`setProperty`);
  - add `Session.getScriptTimeZone`, which exists already;
  - add the `Utilities.formatDate` pattern `yyyy-MM-dd`.
- Dates: write a Sheets serial (days since 1899-12-30) with a `DATE` number format.
- `README.md` -- remove the local-tool and Drive sections only.

## Tasks & Acceptance

**Execution:**
- [ ] `src/attendance.js` -- the actions, server functions and pure helpers above. Each new function gets a one-line comment.
- [ ] `src/ledger.js` -- remove the `importRaidLedger` stub.
- [ ] `src/menu.js` -- rename and add the menu items.
- [ ] `tests/harness.js` -- the UrlFetchApp, PropertiesService and formatDate fakes.
- [ ] `fixtures/wcl-report-sample.json` -- one report response covering the matrix (4 boss pulls, an alt, an unknown player).
- [ ] `tests/story-4-4.html` -- every matrix row, credentials stored in User Properties only, and no secret in alerts.
- [ ] `tests/story-4-1.html` -- update the menu labels and the stub-alert count (the ledger stub is gone).
- [ ] Delete the legacy files listed in the decisions; edit `README.md`.

**Acceptance Criteria:**
- Given credentials, a started raid and a public report, when the owner ends the raid with the link and an empty Gargul box, then the expected raiders get `1` in that raid's Présence row and the raid is ended (Raid ouvert empty, no protections).
- Given the live workbook, when the owner ends a raid with a real report (manual check), then the Présence counts and Roster scores update.

## Implementation Notes

- **Implementer:** delivered `attendance.js` (End raid window, credentials dialog, WCL fetch, pure helpers), the menu labels, the emptied `ledger.js`, harness fakes for UrlFetchApp, User Properties and the `yyyy-MM-dd` formatDate pattern, the fixture, `story-4-4.html`, the legacy file deletions and the README trim. `story-4-1.html` loses the 4.4 and 4.7 stub checks, since those stubs are gone.
- **Parent changes:**
  - Dates written use the plain `DATE` type (the workbook's locale format) instead of a fixed `yyyy-mm-dd` pattern.
  - Added a test for the "link with no report code" matrix row.
- **Test pages:** 4-1 PASS 26, 4-2 PASS 181, 4-3 PASS 103, 4-4 PASS 35, 4-6 PASS 72.

## Plan Change Log

## Review Triage Log

- **Pass 1 (quick):** high 0, medium 3, low 7, false 2, maybe-false 0. The parent patched the code. Pages after patching: 4-1 PASS 26, 4-2 PASS 181, 4-3 PASS 103, 4-4 PASS 67, 4-6 PASS 72.
  - false -- the reviewer read "main or any alt in >25%" as one test per character. AD-7 says "once per resolved roster key" and "credit when the main or any alt took part in > 25% of fights", which is the per-pull combination the code implements. Kept.
  - medium, patch -- two bare codes gave "not recognized", and a URL plus a bare code silently used the first one. `extractReportCode_` now checks each space-separated token: unrecognized text is refused first, then more than one code. This also caught "not a report" words being read as codes. Tests added.
  - medium, patch -- a non-JSON error body (HTML 502) lost the HTTP status. The status is now checked before parsing. Tested.
  - medium, patch -- GraphQL errors (unknown or private code, HTTP 200) dropped the WCL message. The alert now carries the first error message and the code. Tested.
  - low, patch -- test gaps closed:
    - the report HTTP error, GraphQL error, two-bare-codes, URL-plus-code and Gargul cases now assert "nothing written" and "raid stays started";
    - no credentials: no fetch;
    - `submitEndRaid` with no started raid;
    - happy path: Raids instance and date, the exact date serial, the token and report requests, and no secret in the result or alerts.
  - false -- "README rewritten, not trimmed": the old README only described the deleted tools and the Drive flow, so removing those sections left nothing. The short replacement lists the current menu.
  - low, defer to owner -- AC 2 (live check) is a manual step for the owner; step 5 lists it.

## Verification

**Commands:**
- Headless Edge, a fresh `--user-data-dir` per page, for `story-4-1`, `story-4-2`, `story-4-3`, `story-4-4` and `story-4-6` -- expected: `PASS` on each.

**Manual checks:**
- Live workbook:
  - Set WCL credentials.
  - Start a raid, then End raid with a real report and an empty Gargul box. Check the Présence row, the Raids row, the Roster scores, an empty Raid ouvert and no protections.
  - Import the same report again: no change.
