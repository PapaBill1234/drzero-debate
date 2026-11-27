# Batch v9-dropped: verify the 16 dropped entries

Engine main: `design/parity-v2` at HEAD 1fb8b581 (2026-11-26 19:06 UTC). All line numbers are from this copy. Read only. I ran no canary, test, build or model call.

## Result table

| Item | Verdict | Defect today (file:line) | Evidence quality | Risk | Scope if BUILD | Effort | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| run1-02 | BUILD-SMALL (master says Done: partly true) | `triage.py:519-528` ease() uses raw confidence, not precision. `triage.py:1100-1115` gate_hint keeps every uncalibrated hint (33 of top 50 in the newest run). No margin in `calibration()` `:1080-1098`. | measured (calibration json 11-26 14:54; r2 triage run 14:55) | none for MATCH/proof (ranking only) | ease × precision for calibrated causes; gate 'unverified' for a cause with ≥ 5 cases and 0 exact; about 15 lines; extend `test_calibration_and_gate` (`test_triage.py:450`). Margin: LATER. | S | after D09 (agent B edits triage.py) |
| run1-03 | DONE | none. `quota.py:50-67`, `sched.py:99`; tests `test_operator.py:728-744` | measured | none | - | - | - |
| run1-05 | LATER | 5 modules still exist, 404 lines; only callers are inside the set | measured (lines); tokens ≈ 4.4k guess | none | - | - | - |
| run1-06 | DONE | code done; the wave list `v2batch/triage/triage-latest.json` (13:37) is from older code: lone constants at ranks 28-31 | measured | none | re-run triage (ops, no code) | - | H1/D09 re-run |
| run1-10 | DONE | none. `sched.py:101,423,443-450`; resets `:455,500,529,657,839`; tests `test_sched.py:438-478` | measured | none | - | - | - |
| run1-11 | DONE (steps 1-3); step 4 LATER | no `per_exe_ltcg` park reason (grep: 0 hits) | measured | none | - | - | - |
| run1-13 | DONE | none. `cardrun.py:134,453,915-965`; tests `test_cardrun.py:619-691` | measured | none | - | - | - |
| run1-15 | DONE | none. `ledger.py:1005-1070`; tests `test_ledger.py:490,529` | measured | none | - | - | - |
| run1-18 | DONE | none. `triage.py:123-154,549-574`, `insn_diff.py:230-283`; tests present | measured code; builds saved ❓ | none | - | - | - |
| run1-22 | DONE | none. `cardrun.py:185-193,284-320,390-398`, `landq.py:177,366-406`, `queue_build.py:165`, `operator_run.py:161`; tests `test_cardrun.py:901-945`, `test_landq.py:536-548` | measured | none | - | - | - |
| run1-24 | DONE | none. `canary.py:83,723-733,1075-1105`; test `test_canary.py:64-78` | measured | none | - | - | - |
| run1-29 | DONE in units; BUILD-SMALL e2e | canary has no kill-lander mode: kill2 (`canary.py:777`) kills only the operator, so `landq recover` never runs end to end | measured | none (sandbox) | `canary.py`: mode `lander`, invariant `recover_not_parked`; about 50 lines; extend `test_all_chaos_modes` | S | after D30 (cut-host also edits canary.py) |
| run2-09 | REJECT (step 2 LATER) | no replay transport; the waste is on old test cards only | measured | none | - | - | - |
| run2-19 | DONE (other design); small gap LATER | `author.py:1520-1550` calls gain_check for every card; no merge/wmain/tools-lane exclusion | measured code; wall gain guess | low today | - | - | D14 (agent B) |
| run2-21 | BUILD-SMALL (drop right for the main claim) | `author-prompt.md:32` always says "The packet at the end of this prompt"; `author.py:366` puts no packet when off or on a packet fault | measured | none | move line 32 into the `$packet` block; about 5 lines; 1 test in `test_author.py` | S | after D13 (agent B) |
| run2-26 | REJECT (tool); LATER (EXE var + offline replay) | `preview_build.sh:25,84-85,97,102,113-115` LobbyDaemon only; `author.py:166-169` no build tool | measured (fix6 timing); gain guess | preview false_diff 43 % misleads | - | - | - |

## Reasons per item

**run1-02.** `triage.py mine-cases` (`:1018`), `calibration()` (`:1080`) and `gate_hint()` (`:1100`) exist with tests (`test_triage.py:426-560`). The mined set is 173 cases, 57 labelled. Only 2 causes are calibrated: branch_inversion 13/16 exact ('show') and tail_merge 0/18 ('unverified'). Three parts of the proposal are missing. (1) ease() does not use the precision. (2) The proposal showed a one-line fix only for a calibrated, precise cause. The code does the reverse: an uncalibrated cause keeps its hint. instruction_order has 0 of 9 exact (6 family) and still gives 9 fix orders in the top 50. constant has 0 of 3. (3) No margin cut. Parts 1 and 2 are cheap and use measured data. The margin needs more labelled cases, so it is LATER. Goal "≥ 10 cases for data_ref, constant, missing_call, hiword" is not met: the data has 2, 1, 22 (label, not cause) and 1.

**run1-03.** `quota.limit_pattern()` and `is_limit_text()` exist. `sched.LIMIT_RE` is built from them. Tests cover every BILLING/LIMIT text, the real CLI strings, the "killed, provider paused" negative and a bare-number negative. Full cover.

**run1-05.** The 5 modules are still in `parityctl/` (404 lines). A grep finds no caller outside the set. The `TARGETS.md:104` edit is a misread, as the judge said. Zero run-time effect. Do it in any cleanup commit.

**run1-06.** `EASE['lone_constant'] = 0.1`, the LTCG-first hint and 2 tests exist. In the r2 run (code with the change), the first lone constant is at rank 80, as claimed. But the triage list of the v2 wave (`/data/parity-v2/v2batch/triage/triage-latest.json`, 13:37) and the checked-in `parityctl/triage-latest.json` (11-25 20:44) come from older code. They have lone constants at ranks 28-31, no hint gate and no path_literal cause. The code is done. The output that agents read is stale. The EASE refit ("next step") goes into run1-02.

**run1-10.** CRASH_CAP 6, the crash branch, `rc < 0` as a crash, and every reset place (also `sync_inputs` `:657`, which the judge asked for) exist. 4 tests cover 3 crashes, the cap, other states and the reset.

**run1-11.** The flag, `SPLIT_FACTOR 0.3`, the per-exe hint and the 2 tests exist (49 flagged items in the r2 run). Step 4 (park reason `per_exe_ltcg`) is not in the code. Proof R1/R4 act only on baseline MATCH (`proof.py:7,12`), so a build that drops one exe from DIFF to a lower DIFF already passes. The hint tells the author to keep the gain. A park reason adds only a label. LATER.

**run1-13.** `precheck` (R1 pinned, R2 CMake with the "remove the trailing comment" text, R7 guard), the `include_removed` warning and the early `lost_check` exist, with 4 tests. CMAKE_OK is unchanged, as the proposal said.

**run1-15.** `resolve_proofs` reads state.json paths first, then shallow globs, then ledger folders, then the full rglob only for missing digests. The warning and both tests (decoys, state path) exist.

**run1-18.** Net refs, `ref_family()` (path_literal, icf_alias, data_name), `mark_ltcg_inline()` and the ICF resolver with '?' names exist with tests. ltcg_inline uses a mirror-ref rule, not the feedback rows. This is more general than the proposal. In the r2 run, 7 path_literal items are in the top 50 and group into one fix per path pair. "3 builds saved" stays ❓.

**run1-22.** Per-command limits, group kill, BaseException cleanup, git limits and `GIT_TERMINAL_PROMPT=0` exist in cardrun, landq, queue_build and operator_run. The `GIT_SSH_COMMAND` part is not needed: both remotes use https. The limits are larger than proposed (full_build 5,400 s, backup 1,800 s). This is safe for good runs. The rsync root cause is closed: `backup/sync.sh:41-47` excludes `backup/` and `eng-wt/`, and `:50-56` stops at 600 MB. So the ❓ in D33 can close.

**run1-24.** All 4 modes and all 5 invariants exist. `test_all_chaos_modes` runs them in the unit suite.

**run1-29.** `landq.recover` checks the quota, keeps `e['limit']`, and the operator gives back the budget on exit 79 and parks a busy slot after 7,200 s as "slot N busy". 2 operator tests and 2 landq tests cover it. The canary chaos mode `kill-lander` is missing. Today kill2 kills the operator while landq lives, so the recover path never runs end to end. Scope: kill -9 the landq group after the intent opens, write PAUSE once, hold the slot, assert LANDED, no park, no "dead lander".

**run2-09.** Measured on the ledger now: 348 model reviews. Duplicate triples: test cards 234 events / 1,705,678 tokens, gap cards 52 / 391,146, v2 cards 15 / 14,728. No test-card review ran after 11-25 20:41. A replay transport saves 0 on waves. The drop was right. The carry miss-reason counter (step 2) is cheap observability: LATER.

**run2-19.** `no_gain` is a result and a park reason. A zero-gain round gets a feedback round. When rounds run out, the card parks before the proof. A passed proof with match_gain 0 also parks. 4 tests exist. This is a different design from the proposal (the proposal parked at once). The card does not enter the sched queue, so the "main moved" repeat stops. Gap: no exclusion for merge, wmain or tools-lane cards. These cards do not run through author.py today, so the risk is low. Tell agent B (D14) that the author side exists.

**run2-21.** The "goal met" claim is false (wrong denominator), so the drop was right for the headline. The packet is now on by routing: ENGINE-ISSUES row 1 was fixed in d0cd29af, and runcard.sh runs with the packet. But all 8 stored author states have `packet: False`, so there is 0 measured session with the packet. One real defect stays: the prompt claims a packet when there is none (packet off, or a packet fault). Fix it. The Grep `head_limit` hook needs a settings hook that author.py does not have. Measure packet-on sessions first: LATER.

**run2-26.** The entry itself says do not build the tool. `preview.py` in `parityctl/` is the old fix6 getter pilot, not a tool. The preview disagrees with the full build (false_diff 43 %). The gain is about 100 s (2.8 %), a guess. The EXE variable and the offline replay are LATER.

## run1 REPORT open questions

**Q1 (status of landed ops fixes).** All are on main. Each one is an ancestor of HEAD, and code and tests exist.

| Lesson | Commit (UTC) | Code | Test |
| --- | --- | --- | --- |
| ops L2 limit texts | b910aaec 12:57 | `quota.py:50-67`, `sched.py:99` | `test_operator.py:728-744` |
| ops L3 crash waits | b910aaec 12:57 | `sched.py:101,423,443-450` | `test_sched.py:438-478` |
| ops L4 backup after push | 758a9321 13:14 | `cardrun.py:1490-1538` | `test_cardrun.py:935`, `test_landq.py:548` |
| ops L6 canary chaos | cd12f1d9 15:28 | `canary.py:83,1075-1105` | `test_canary.py:64-78` |
| ops L7 recover budget | cd12f1d9 15:28 | `landq.py:627-679`, `operator_run.py:98-99,856-877` | `test_operator.py:326-351`, `test_landq.py:482-499` |
| tools L5 run_cmd limits | cd12f1d9 15:28 | `cardrun.py:185-320` | `test_cardrun.py:901-945` |
| no_gain round | b3bd6219 15:36 | `author.py:1493-1509,1586-1594` | `test_author.py:1047-1116` |

**Q2 (ssh keepalive).** Yes. `remote_build.py:171` SSH_KEEPALIVE (ServerAliveInterval=15, ServerAliveCountMax=4), used in `ssh_argv` at `:184` with BatchMode. `objsync.py:198-199` has it too. Backstop: `slotq.py:573` REMOTE_TIMEOUT 2860 and the kill at `:845-860`. Commit a8a84b22 (13:31). Test `test_remote_build.py:260` and the canary invariant `ssh_keepalive`. Per-phase deadlines stay in D30.

**Q10 (canary after the fixes).** One all-mode result exists: `/tmp/tmp.lKTYcU6WnB/canary-result.json`, 15:28 UTC, chaos `pause,kill,limit,crash,backup,hang`, verdict pass, 24 of 24 invariants ok. It is synthetic (stub builds, fake model). It is probably `test_all_chaos_modes` at the r4-ops merge. It is after b910aaec, 758a9321 and a8a84b22, but before b3bd6219 (author no_gain). It is in /tmp. The newest kept run in `/data/parity-v2/canary` is run-fix2b at 02:14. Its meta has no engine rev. Action: run `canary --chaos all` once on main and keep the result under `/data/parity-v2/canary`. Add the engine rev to the canary meta (about 2 lines).

## Extra finding

The triage code for run1-02/06/11/18 is done, but the lists that agents read are stale (see run1-06). Only `eng-wt/r2-triage-out/r2/triage-latest.json` (14:55) uses the new code. Re-run `triage.py run` on main with the calibration for the v2 wave. This fits H1/D09.
