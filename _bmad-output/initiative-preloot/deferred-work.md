- source_plan: `C:/Repos/preloot-agent/_bmad-output/initiative-preloot/epic-sheets-workbook/story-tracer-clasp-bound-script-in-a-new-workbook-plan.md`
  summary: Rewrite tools/google_apps_script/README.md as the CLASP setup guide (install clasp, enable the Apps Script API, login, create-script, push, authorise, run browser tests), replacing the outdated main()/Drive/manual-paste content.
  evidence: Split from story 4.1 at the user's request because the plan was about 1,880 tokens; the test harness stays in 4.1 because its Verify requires the browser test page to pass.

- source_plan: `C:/Repos/preloot-agent/_bmad-output/initiative-preloot/plan-4-2-workbook-polish.md`
  summary: Before story 4.3, update the architecture spine, spec and PRD with five workbook-polish decisions now implemented in the Apps Script workbook contract.
  evidence: Decisions to record: (1) Raids fields now include report-codes and BiS-window behaviour by reset date; (2) Config stores the open raid id; (3) PatternItems is removed; (4) tank priority is removed from roster and interchange assumptions; (5) Impact Score gain now comes from Objets-tab simulated gain by roller spec (reverses AD-2 no-item-gain-lookup and updates Interchange v1/addon assumptions).

- source_plan: `C:/Repos/preloot-agent/_bmad-output/initiative-preloot/epic-sheets-workbook/story-raid-lifecycle-and-pre-raid-snapshot-export-plan.md`
  summary: Confirm the companion addon decodes the 4.6 Base64 snapshot (UTF-8 JSON, Interchange v2), including accented spec labels such as Prêtre Sacré.
  evidence: Unverified (high if false): no Base64 decode call was found in the repo's Lua. To settle, paste a live export into the addon in game, or have epic 5's importer test decode fixtures/snapshot-sample.json once Base64-encoded.

- source_plan: owner discussion 2026-10-22 (after story 4.7; nothing implemented)
  summary: Linked mains — a player with two (or more) Roster mains (not Rerolls) shares attendance across them, while each character keeps its own Awards block, BiS/Impact loot counts, parse, spec, BiS ratio and Impact score.
  evidence: |
    Status: discussion only, awaiting owner answers; then correct course and add an epic-4 story (after 4.8, or before it if needed before the tier change).
    Proposed model: new Roster column "Joueur"; rows sharing a value share attendance (symmetric, allows 2+, blank = solo). Rerolls unchanged: an alt credits its main's whole group.
    Touch points: End raid WCL credit merges pulls across the group for the >25% threshold and writes 1 in every group member's Présence column; score formulas, loot import, snapshot, archive and Delete raid unchanged; setup warns on a Joueur value used once; a character cannot be both Roster and Rerolls (already enforced).
    Fairness risk: the absent linked main keeps gaining presence without loot, so its BiS ratio climbs; one person's attendance builds two characters' priority. Options: (1) accept, full credit to both; (2) partial credit (e.g. 0.5) for the absent partner; (3) shared BiS loot count (contradicts separate BiS ratio).
    Open questions: group size exactly 2 or more; link applies to future raids only or merges history (suggested: future only); merge pulls when a player swaps character mid-raid (suggested: yes); hand edits to Présence stay independent per character (suggested: yes); fairness option 1/2/3.
