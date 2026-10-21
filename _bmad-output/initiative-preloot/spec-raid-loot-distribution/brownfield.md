# Brownfield: Gargul_Preloot

Owner's repo `github.com/zambelaba/Gargul_Preloot` (local clone `C:/Repos/Gargul_Preloot`, `main` = tag `1.1.0`, in use today) is evolved for WoW Forever. Gargul v8.0.1 is assumed to fully support Forever.

## Current state

| Part | Files | Does today |
| --- | --- | --- |
| Addon | `Core.lua`, `Gargul_Preloot.toc` | Depends on Gargul. Adds a ratio column to the master-looter roll table, a "Preloot (Base64)" importer button, and increments loot count on epic non-OS awards. Saves data in `GargulPrelootDB`. Appends the new ratio to Gargul's award chat announcement, in French. |
| Apps Script | `tools/google_apps_script/attendance.js` | WCL v2 report fetch, attendance >25% of completed boss pulls, Rerolls alt-to-main mapping, `presence_details` sheet, document lock. |
| Apps Script | `tools/google_apps_script/ratio.js` | Writes Base64 roster JSON for the addon; parses RCLC and Gargul exports into `loot_details` and loot counts. |
| Local tooling | `generate_raid_json.ps1`, `run_local.cmd`, `.env.example`, `raid_ids.csv` | Offline WCL attendance JSON generator with self-test. |
| Tests | `presence_test_runner.html`, `test_runner.html` | Browser runners for presence and attendance logic. |

## Keep

- Gargul-dependent addon structure, importer button and master-looter table hooks.
- WCL fetch, the >25% boss-pull threshold, Rerolls attendance crediting, the document lock.
- The ratio line appended to Gargul's award chat announcement, unchanged (French).
- Gargul-format award import idea, replaced by the Custom export template from the architecture spine.

## Change

- Replace the single attendance/loot ratio with BiS Ratio and Impact Score (allocation-rules.md) in both the addon and the Sheet.
- Move the TOC to WoW Forever (`## Interface-Camelot: 16001`).
- Append the addon's columns after Gargul's ten native roll-table columns; Gargul reads roll type from column 4, sort keys from 6–7, and the gear toggle from 10.
- Add the owner's BIS/IMPACT/NONE choice per award and fill `@GPRAID`/`@GPTREATMENT` in the Gargul Custom export by checksum.
- Set `_importButtonAdded` so the importer button is created once; call Gargul's `Base64.decode` instead of the nonexistent `Base64:Decode`.
- Credentials move from Script Properties to the owner's User Properties; workbook writes become atomic batches.

## Remove

- `GargulPrelootDB` SavedVariables persistence.
- Random 1–10 ratio shown for unknown players, and the test data/hash helpers.
- Case-insensitive and `-Thunderstrike` name normalization.
- Loot coefficients (0.33, prio items = 0) and hard-coded date cutoffs (2026-05-18, 2026-09-01).
- RCLootCouncil import and English `Pattern`/`Design` name-prefix detection.
- Google Drive JSON file output.

## Repair

- `test_runner.html` loads the missing `warcraft_logs_raid_json.js` and calls the removed `main()`.
- `tools/google_apps_script/README.md` describes the removed `main()` and Drive output.
