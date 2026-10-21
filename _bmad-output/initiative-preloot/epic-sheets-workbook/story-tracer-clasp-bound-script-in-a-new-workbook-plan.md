---
title: 'Tracer: CLASP-bound script in a new workbook'
type: 'feature'
ticket: '1'
created: '2026-10-21'
status: 'built'
baseline_revision: '38fefdeea7d44b6814692c3bab36800307d90386' # C:/Repos/Gargul_Preloot (code repo)
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 1
context:
  - '{project-root}/_bmad-output/initiative-preloot/architecture-raid-loot-distribution/architecture-raid-loot-distribution.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The new loot workbook does not exist, and Gargul_Preloot's Apps Script is pasted by hand into the old workbook, with an `onOpen` that calls a missing `main()` and code that expects the old workbook's sheets.

**Approach:** Create a new workbook whose bound script is pushed with CLASP from `tools/google_apps_script/src/`. It opens a "Loot priority" menu with one stub per later action file, and proves the path end to end with a diagnostic action that writes one row through a shared locked, atomic `batchUpdate` helper. The old scripts move to a folder that is never pushed until stories 4.4 and 4.7 rewrite them.

**Decisions:** Workbook title `preloot-forever`. Script time zone `Europe/Paris`. The README rewrite is deferred to a follow-up (deferred-work.md).

## Boundaries & Constraints

**Always:** All new script code lives in `tools/google_apps_script/src/`, the only folder CLASP pushes, on the V8 runtime with the Sheets advanced service v4. Every workbook write in later stories goes through the shared helper: document lock, then one `Sheets.Spreadsheets.batchUpdate` call. Each menu stub lives in the file its later story owns. Tests are browser HTML pages with fake Apps Script globals, one page per story.

**Never:** No Warcraft Logs, data-model, formula, snapshot, ledger or tier logic (stories 4.2-4.8). No credentials or `.clasprc.json` in the repo. No change to the old workbook, `Core.lua`, `Gargul_Preloot.toc`, the local WCL tools, or the README. Old `attendance.js` and `ratio.js` are moved unchanged.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Menu | Owner opens the workbook | "Loot priority" menu lists the four planned actions and Diagnostics | No error expected |
| Diagnostic write | Owner runs Diagnostics > Test write | One timestamped row is appended to the `Diagnostics` sheet, created if missing | No error expected |
| Forced failure | Owner runs Diagnostics > Test failed write | No row is added; an alert shows the batch error | Sheets rejects the whole batch |
| Busy lock | Another owner action holds the document lock | No write; alert says another action is running | Lock released in `finally` |
| Stub action | Owner picks a not-yet-built action | Alert names the story that delivers it | No write |

</frozen-after-approval>

## Code Map

- `tools/google_apps_script/attendance.js` -- old WCL code; `onOpen` at L13-23 calls a missing `main`; depends on `ratio.js`. Moves to `legacy/`; story 4.4 rewrites it.
- `tools/google_apps_script/ratio.js` -- old loot code with case-insensitive matching and RCLC import. Moves to `legacy/`; story 4.7 rewrites it.
- `tools/google_apps_script/test_runner.html`, `presence_test_runner.html` -- old test pages (the first loads a missing file and calls `main()`). Move to `legacy/` beside the files they test.
- `attendance.js` L44-47 -- `LockService.getDocumentLock()`, `tryLock`, `releaseLock` in `finally`: the lock pattern to reuse.
- Old test pages -- `equal(actual, expected, label)` inside an IIFE, result in `<pre id="result">` as `PASS: N assertions` or `FAIL: stack`: the pattern to reuse.
- CLASP 3.4.1 (Node 24.13.0 present; clasp not installed or logged in) -- `clasp create-script --type sheets --title <t> --rootDir src` creates a new Sheet with a bound script and writes `.clasp.json`. Without `.claspignore`, `*.html` is pushed. The Apps Script API must be on at script.google.com/home/usersettings.

## Tasks & Acceptance

**Execution:**
- [ ] `tools/google_apps_script/legacy/` -- `git mv` the four old files here unchanged -- keeps the old `onOpen` and missing-sheet code out of the push.
- [ ] `tools/google_apps_script/src/appsscript.json` -- V8, Sheets advanced service v4, `Europe/Paris` -- runtime and API.
- [ ] `tools/google_apps_script/src/batch.js` -- `withDocumentLock_(fn)` and `applyBatch_(buildRequests)`, where `buildRequests` is a function called inside the lock that reads the sheet and returns the requests (an empty list writes nothing) -- the one write path; checks and writes are serialized together. `withDocumentLock_` is not re-entrant: an action takes the lock once.
- [ ] `tools/google_apps_script/src/menu.js` -- `onOpen` menu; Diagnostics actions pass their request builder to `applyBatch_` -- the tracer.
- [ ] `tools/google_apps_script/src/attendance.js`, `snapshot.js`, `ledger.js`, `tier.js` -- one stub handler each that alerts its story (4.4, 4.6, 4.7, 4.8) -- later stories replace only their own file.
- [ ] `tools/google_apps_script/.claspignore` -- allow only `appsscript.json` and `*.js` -- tests and fixtures never reach the project.
- [ ] `tools/google_apps_script/tests/harness.js`, `tests/story-4-1.html` -- fakes for `SpreadsheetApp`, `LockService` (exposing whether the lock is held), `Sheets`, UI alerts. The fake `batchUpdate` copies one sheet store keyed by id and rebuilds the name index from it, committing only when every request succeeds. Tests use `equal(actual, expected, label)` and cover the I/O matrix: a second Test write appends a second row; the forced failure on an existing `Diagnostics` sheet leaves the row count unchanged; the lock is free after both; each stub leaves the rows unchanged -- the per-story test pattern.
- [ ] `tools/google_apps_script/fixtures/.gitkeep` -- shared fixtures folder for stories 4.3, 4.6, 4.7.
- [ ] `.gitignore` -- add `.clasprc.json` -- credentials never committed.
- [ ] hitl -- owner: `npm install -g @google/clasp`, enable the Apps Script API, `clasp login`, then from `tools/google_apps_script`: `clasp create-script --type sheets --title preloot-forever --rootDir src`, then `git checkout -- src` to restore any committed file it rewrote (the manifest must keep Sheets v4 and `Europe/Paris`), `clasp show-file-status` to confirm only `appsscript.json` and `src/*.js` are listed, `clasp push`, open the workbook, authorise, run the Diagnostics actions; commit `.clasp.json`.

**Acceptance Criteria:**
- Given `clasp push`, when the remote project is listed, then it holds only `appsscript.json` and the `src/*.js` files.
- Given the workbook `preloot-forever`, when the owner opens it, then the I/O matrix behaviors hold.
- Given `tests/story-4-1.html` opened in a browser, then it shows `PASS`.

## Design Notes

```js
function applyBatch_(buildRequests) {
  return withDocumentLock_(function () {
    var requests = buildRequests();
    if (!requests.length) return null;
    return Sheets.Spreadsheets.batchUpdate({ requests: requests }, SpreadsheetApp.getActive().getId());
  });
}
```

The forced-failure action sends a valid `appendCells` plus a request for a missing sheet id, proving Sheets applies all requests or none (spine Deferred: failure atomicity).

## Verification

**Commands:**
- `clasp push` from `tools/google_apps_script` -- expected: only `appsscript.json` and `src/*.js` pushed.
- Open `tools/google_apps_script/tests/story-4-1.html` in a browser -- expected: `PASS`.

**Manual checks (if no CLI):**
- In `preloot-forever`: the menu appears; Test write adds one row; Test failed write adds none and shows an error; a stub names its story.

## Plan Change Log

- 2026-10-21, loop 1 (bad_plan). Trigger: quick review found `applyBatch_(requests)` locked only the write while the sheet lookup and sheet-id choice ran outside the lock, and a nested lock is impossible, so later stories could not serialize check-and-write (spine Deferred). Also: the harness cloned its id and name maps separately, so appends to an existing sheet were invisible and the atomicity test passed vacuously; tests skipped lock release and stub no-write; the planned `equal` pattern was not reused; `create-script` could overwrite the committed manifest. Amended: `applyBatch_(buildRequests)` builds inside the lock; harness copies one store; tests listed explicitly; setup restores `src` and checks `clasp show-file-status` before push. Known-bad state avoided: racy check-then-write copied into stories 4.4-4.8, and a test page that cannot fail on a partial write. KEEP: `git mv` of the four legacy files unchanged; `appsscript.json` content (V8, Sheets v4, `Europe/Paris`, STACKDRIVER); `.claspignore` (`**/**`, `!appsscript.json`, `!**/*.js`); the four one-line stubs with their names and alert texts; menu titles and item labels; Diagnostics sheet creation with an explicit `addSheet` sheetId; the forced failure appending to a missing sheet id; harness `install`/`uninstall`; the page passes in headless Edge (`msedge --headless=new --allow-file-access-from-files --dump-dom`); `.gitignore` adds `.clasprc.json`.

## Review Triage Log

- Pass 1 (quick): high 0, medium 3, low 4, false 1, maybe-false 1.
  - medium, bad_plan -- `src/batch.js` `applyBatch_`, `src/menu.js` builders: sheet lookup and id choice run outside the lock; two actions can both add `Diagnostics`, and the non-re-entrant lock prevents a caller from wrapping both. Plan Design Notes prescribed this shape.
  - medium, bad_plan -- `tests/harness.js` `batchUpdate`: separate deep clones of the id and name maps break object identity; `getSheetRows` reads the stale name map, so appends to an existing sheet are lost.
  - medium, bad_plan -- `tests/story-4-1.html` forced failure: with the harness bug the row count cannot change, so the atomicity assertion passes even on a partial commit.
  - low, bad_plan -- `tests/story-4-1.html`: lock release after a write is never asserted.
  - low, bad_plan -- `tests/story-4-1.html`: stub actions are not checked for no write.
  - low, bad_plan -- `tests/story-4-1.html`: uses `assert(cond)` instead of the Code Map's `equal(actual, expected, label)`, losing actual/expected on failure.
  - low, bad_plan -- `tests/harness.js`: `catch (error) { throw error; }` is dead code.
  - maybe-false (medium if true), bad_plan -- setup: `clasp create-script --rootDir src` may write the default manifest over `src/appsscript.json`; settle by running it and checking `git diff src`.
  - false -- `.clasp.json` absent and setup not run: the hitl task is the owner's and not yet due; not a code defect.
- Pass 2 (quick, after loop 1 re-derivation): high 0, medium 0, low 7, false 0, maybe-false 0. Patched by the parent (implementer not re-engageable); browser page PASS 35 assertions in headless Edge.
  - low, rejected -- `src/menu.js` fixed `DIAGNOSTICS_SHEET_ID`: if the owner renames the Diagnostics tab, re-creation collides on the id; unlikely in everyday use and the fix adds branching.
  - low, patch -- `src/menu.js`: timestamp was `toISOString()` (UTC) despite the `Europe/Paris` script zone; now `Utilities.formatDate` with `Session.getScriptTimeZone()`.
  - low, patch -- `tests/story-4-1.html`: menu items' handler functions and the submenu caption were not asserted; now each handler is checked to exist.
  - low, patch -- `tests/story-4-1.html`: written row contents were not asserted; now the timestamp format and `test-write` marker are checked.
  - low, patch -- `tests/story-4-1.html`: stub alert count unchecked; now `alerts.length === 4`.
  - low, patch -- `src/batch.js`: `buildRequests() || []` silently skipped a builder that forgot to return; now throws unless an array is returned.
  - low, patch -- `src/batch.js`: unreachable `if (!lock)` guard in a bound script; removed.
- Note: the re-derivation renamed the menu labels and stub handlers that loop 1's KEEP list preserved (e.g. "Sync attendance", `runAttendanceSync`); the new names are consistent, tested, and each stub still names its story, so they stay.
