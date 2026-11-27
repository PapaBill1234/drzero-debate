# Dr. Zero: master list of proposals

Date: 2026-11-26. Source: `/data/parity-v2/drzero/all-proposals.txt` (about 115k tokens, 86 entries).
Read only. No engine file changed. Nothing committed.

## How to read this list

- Each row is one change. Rows merge entries that propose the same change. All source IDs stay on the row.
- Gain is the best judge grade of the merged sources. The judge marked almost every entry "verified". That is a weak filter. Read the Why column and the notes under each table.
- Effort is my estimate. S = under 1 day of work. M = 1 to 3 days. L = more.
- Code check (marker at the end of the Files cell):
  - `open` = the named code is not in the engine yet.
  - `part` = a part exists already. The text names what is left.
  - `stale ❓` = the proposal names constants or lines that differ from the engine now.
- I checked with grep in `design/parity-v2/parityctl` only. I did not run any test. Line numbers move.
- Many speed numbers are for the v2b wave (2026-11-26). The goal is 3,600 s per wave and 84k nocr tokens per MATCH.
- Figures marked ❓ are guesses of the proposal or of the judge.

## Summary

| Item | Count |
| --- | --- |
| Raw entries read | 86 (run1 39, run2 47) |
| Entries merged into rows | 70 |
| Entries dropped (done, weak or wrong) | 16 |
| Merged items | 41 (D01 to D41) |
| Type correctness | 3 |
| Type parity | 3 |
| Type safety | 9 |
| Type speed | 14 |
| Type cost | 12 |
| Gain high / medium / low | 22 / 18 / 1 |
| Items with code `open` | 26 |
| Items with code `part` | 12 |
| Items not traced (marked ❓) | 3 (D02, D27, D36) |

Honest view of the list:

- Only 3 rows change MATCH credit directly (D01, D02, D03). They matter most because a wrong credit breaks every other number.
- The speed rows overlap. D19, D20, D21, D22, D28 all cut the same 1-hour wave. Their gains do not add up. Build and measure one at a time.
- Three high-gain rows lean on one wave (v2b) and a few positive cases. These are D14, D15 and D13. Treat them as guesses until the next wave.
- The cost goal (84k nocr per MATCH) is not met by speed rows. v2b was about 181k. Only D32, D13, D14, D15 and D17 touch the big token costs (lead 1.78M, authors 0.94M).

## A. MATCH credit and ledger correctness

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | Credit only (exe, symbol) items that are not credited yet. Keep a `credited_items` table in the receipts. | `integrate.py:119-125,289`, `feedback.py`, `receipts.py` (open) | Wave 1 claimed 118 MATCH but only 33 were real. A repeat land credits the same item twice. | High | M | correctness | run1-32 |
| D02 | In `feedback.py`, set `credited` for a 'review' verdict. Use `credited` as the numerator of `ref_real` and `tokens_per_ref`. Fit `p_new` on credited MATCH. Re-run the review of the 62 stale accept receipts. Stop feedback text from overriding result files. | `feedback.py` (`credited` is in REAL_FIELDS; the review rule is not checked ❓), `plan_cards.py` (open) | The pooled `ref_real` is 0.645. It would be about 0.31. The planner now trusts a number that is too high. The review digest changed, so `check_review` counts 0 valid accepts. | High | M | correctness | run1-17, run1-08 |
| D03 | Make the credit chain checkable. `ledger_land` passes `proof_path`, `main_match_before/after`, excluded counts, wave and `match_symbols`. Store `commits=[{sha, actor, card}]` of each land. Add `ledger.verify_match_chain`. | `integrate.py:246-255`, `ledger.py:405` (`record_credit`) (open) | `landed.sha` and `credit.card` do not name the commits that made the MATCH. Lead and author work cannot be told apart. 0 s gain, but every cost claim then has proof. | High | M | correctness | run2-28, run2-46 |

Notes:

- D01 is the best correctness row. Check the idempotency rule against the existing `uid` rule in `ledger_land` first.
- D02 and D12 (below) both change the planner. Do D02 first.

## B. Safety and proof binding

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D04 | Bind every step output to the tools that made it. Add producer digests (gate scripts, shims, strict tools, `capstone`, `pefile`, `llvm-pdbutil`) to the keys of gate, full_build and strict. Add `base_build` to the strict key. Write a `producer` stamp next to each output. `proof.py` binds the stamps. `integrate` refuses a mismatch. Use an import-closure digest for the checker files. | `proof.py:63-83` (CHECKERS), `cardrun.py:807-815,1381-1400`, `integrate.py:128-186`, `gate_*.sh` (part: CHECKERS now has `funcdiff_cached.py`, `objcache.py`, `buildcache.py`, `buildonce.py`, the linked and gate scripts; `checkerset.py` is missing; `tool_digest` still hashes only 4 parts) | A real drift happened (digests `d0f0a78e` and `da7e7c9d`). With the same rev, a re-check can reuse a gate or strict output from old tools and stamp the new digest on it. | High | M | safety | run1-37, run2-06, run2-12, run2-34 |
| D05 | Bind the gate environment. `gate_fast.sh` writes `gate.env`. Proof R8 and `remote.json` bind it. `integrate` refuses a missing digest. Make `gate.sh:15` fail when `gate_extra.sh` is not executable. `pdb_layout.py` writes `pdb_layout.json`, exits 2 on a missing PDB, and maps `lift_common` (a real 4th hole). The proof binds the summary. | `gate_fast.sh`, `remote_build.py`, `proof.py` (R8), `integrate.py`, bns-lift `tools/gate.sh`, `tools/pdb_layout.py` (open) | A remote job has no per-job check today. A missing `gate_extra.sh` skips the layout check without a sign. | High | M | safety | run2-23, run2-29 |
| D06 | Add deterministic review rules P4 (callee name or signature, with the fold exemption), P5 (zero argument at a call), P6 (store count), P8 (load segment), P9 (return width). `integrate` recomputes the precheck and does not trust the receipt. Add a 2-draw accept rule and whitespace-normalised bundle digests. Add frozen fixtures (11 defect items must reject, 30 clean bundles must pass). | `review.py:19-24,259` (only P1 to P3 exist), `integrate.py:106`, new `tests/test_review_canary.py` (open) | P3 ignores the value 0. A dropped zero argument passes by design. In a replay, the rules catch 8 of 12 rejected items with a bundle on disk. They flag 19 accept draws. Saves about 90 draws (320k nocr, about 3.3k per MATCH). The 99 old draws log only the final call, so the token figures are lower bounds. | Medium | M | safety | run2-42, run2-17 |
| D07 | Add proof rule R9 `safety_guard`. It runs `edit_guards` (G1, G3) on the body diff of each new MATCH. A hit gives `no_auto`, so the item needs a review. Split the checker digest. `build_digest` keys full_build. `rule_digest` (`proof.py`, `guard.py`, `edit_guards.py`) keys only proof. Bind review receipts to symbol, candidate and bundle. | `proof.py:63-65,180`, `edit_guards.py`, `cardrun.py:405,1382-1389`, `integrate.py` (open; `edit_guards` runs only in `pilot.py`) | A lift that drops a server safety check can still get MATCH credit in the card path. A rule change costs about 5,450 s and 59k tokens today. It would cost about 48 s. The judge found the "2/3 auto credit" premise wrong. The real share is 18 of 51 (35 %). Hand replay on 317 bodies is not verified ❓. | Medium | M | safety | run2-47 |
| D08 | Add a model-reviewer canary with seeded defects (84 mutants, about 219k nocr, about 640 s serial). Run it only when the model, the instructions or the bundle format change. Integrate refuses the change when recall falls below a floor. | new `tests/` canary, `review.py` (open) | No mutation test of the reviewer exists. The review is the only check for about 1/3 of the credit. Recall of the model is not measured yet. Any later cut to the review (smaller model, trimmed bundle) needs this number first. | Medium | L | safety | run2-42 |

Notes:

- D04 and D05 are two halves of one trust problem. Land them together.
- D07 conflicts with D23 in one point. See D23.
- Do not ship skip-review-by-score. The judge in run2-42 and run2-47 both rejected it.

## C. Triage and planner (parity effect)

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D09 | Add `band_items()` to triage for DIFF items with score below 85 (STUB-CALLEE, EMPTY, PATH-LITERAL, SHARED-SRC, EH, FOLDED). Add a park list for them. | `triage.py` (open) | The figure "about 230 builds saved" is a guess ❓. The idea is to stop spending author rounds on classes that never turn into MATCH. | High | M | parity | run1-39 |
| D10 | Add triage hint families. `inline_dir` classes grouped by callee. `branch_inversion` hints that depend on the direction (`detail.tail`). `classify_order()` for `instruction_order` (PSEUDO-CALL, INLINE-GAP, TAIL-ARTIFACT). Group by function across exes. | `triage.py` (open; `path_literal`, `icf_alias`, `data_name`, `ltcg_inline` exist already) | Grouping gives one fix for many items. "About 10 builds saved" is a guess ❓. The EASE weights do not change. | High | M | parity | run1-28, run1-21, run1-31 |
| D11 | Planner reachability. `exe_state` builds `lifted` from the merged base only. Split `gains()` into free p_new and blocked p_new. Order the scope by reachability in `render_card`. Fix the calibrate crash. Land gap-15 and gap-04 first. | `plan_cards.py:734,1232,1315` (part: `exe_state` and the reachability model exist; the split and the crash fix are not checked ❓) | A card that lifts only unreachable bodies gives NOREF gain and no REF gain. The "+40 NOREF" gain is a guess ❓. The group a/b/c shares are not verified. | High | M | parity | run1-23, run1-34 |
| D12 | Fix the cost-model constants. Use one unit (beq) in the planner. Print the fitted `p_new` per kind. Re-fit the repair CLASSES p values (`P_OUT_OF_CARD` 0.1 to 0.6, `shape_cc` 0.6, `shape_imm` 0.15). Run `carry()` on every review (up to 0.90M of 1.75M review tokens). | `plan_cards.py:89-91,1018`, `feedback.read_ledger`, `repair.py:98-141,699`, `cardrun.carry` (stale ❓: `MEASURED_FACTOR` is 1.35 and `CARD_CAP` is 320,000 now, not 16.5 and 3,000,000; `review_item_cost` exists) | The order of open cards does not change. This row fixes units only. The `P_OUT_OF_CARD` value rests on about 1 item. The judge says the causal claims are overstated. | Medium | S | cost | run1-25, run1-04, run1-16, run1-01 |

## D. Card authoring and token cost

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D13 | Split cards by function. `card_shards()` gives at most 8 functions per shard (for `--no-packet` cards). Cap a card at 10 PDB names. Split cards over about 3,600 words. Write the handoff early. | `author_packet.py`, bns-lift side `v2batch/tools/mkcard.py`, `author.py:1479` (open; `author.py` already has `CTX_SPLIT` and shards) | A big card reaches a context split with 0 change (lg-01: 417,607 units). The gain of about 1.0 to 1.5M units is a guess ❓. The word threshold has only 2 positive cases. | High | M | cost | run1-26, run1-27, run2-15 |
| D14 | Filter the card rows. Keep only causes and bands that had MATCH yield (`constant`, `missing_call`, structural misses). Drop rows with proof level A or B unless the draft row has a new idea. Put at most 6 rows on a card. Park `no_gain` items. | `v2batch/tools/mkcard.py:46`, `triage.py` (part: `no_gain` park and a proof-level check exist in `author.py`) | The rule is fit to 6 positive rows, and only 2 are author MATCH. So 77-84k nocr per MATCH is overfit. Lead commits bought 11 of the 15 MATCH. Their 1.77M cost is not in that number. The judge found the finding "F3 leaves 0 items" useful. | Medium | M | cost | run1-36, run2-35 |
| D15 | Add a `tries` field per item (earlier cards or handoffs that named it while it stayed DIFF). Fit yield by (cause, band, tries). Add an expected-cost stop rule `E = c_attempt / p`. Drop the item when E exceeds 168k. Send cross-exe name groups to one lead pattern card. Report tokens per attempt and yield per tries class. | `triage.py`, `feedback.py`, `plan_cards.py gains()`, `v2batch/tools/mkcard.py`, `docs/WAVES-VS-V2.md` (open) | The 84k bar came from a pool of 207 untried items. The v2b pool has 152 items, and 147 stay open. A fair bar differs. This is the main honest-metric row. It saves about 2.2M author tokens ❓. It loses at most about 6.8 expected MATCH ❓. | High | M | cost | run2-44 |
| D16 | Enforce a per-item tool-call budget in `author.py`. The Meter counts `tool_use` blocks that name each item. At 8 calls the session ends at the next turn end with status `item_budget`. The next session marks the item "Not done". | `author.py:584` (`limit_check`), `tokscope.py` (open) | Rule 8 is prompt text only. On v2b this cuts 20k to 385k units, depending on how calls are counted ❓. Both author MATCH came at item call 4 or earlier. | Medium | M | cost | run2-35 |
| D17 | Run all cards through `author.py` with the 100k context split. Drop the "read result JSON" lines from the card text. Write a per-item state table into `handoff_text`. | `author.py:1211-1236` (`handoff_text`), `CTX_SPLIT` (part: the split exists) | The gain is about 25-30 % of beq. The reset cost is unverified ❓. The table saves 67-150k units on pod-01 and 30-83 s per split. | High | M | cost | run1-12, run2-27 |
| D18 | Deny waits (`sleep`, `build.sh`, `gate*.sh --full`) and the Hex-Rays cache in the author tool list. Set `BASH_OUTPUT_CHARS` to 8000. | `author.py:171-179` (`DENIED`, `BASH_OUTPUT_CHARS`) (part: the limit is 16,000 now; the deny entries are not checked ❓) | About 11-14k tokens per MATCH. The "61 min critical path" claim in the entry is weak. | Medium | S | cost | run2-03 |

## E. Build wall time inside the gate

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D19 | Move `buildcache.py gc` off the build path. Run it in the background with a stamp (6 h), `flock -n` and `ionice`. Or run it once per operator tick with a 60 s limit. | `gate_fast.sh:76`, `buildcache.py:892` (open; gc still runs after `gate.rc`) | The gc walk stalled 922 s (cg-01) and 618 s (pod-01). The two stalls end together, so the cause may be host-wide I/O. The log shows "removed 0". Steady state is about 2 s. The gain is real only on a cold walk. | High | S | speed | run2-11, run2-13, run2-39 |
| D20 | In `gate_fast.sh`, start `vsobj restore` in the background at the start. Write `gate.rc` before `vsobj record`. Run record and gc in a detached tail under `flock`. Make `index_append` run in `try/finally`. | `gate_fast.sh:65-76`, `buildcache.py:610-677`, `cardrun.py:750` (open) | Restore costs 982 s and record 483 s over 62 runs. About 761 s of restore hides behind `gate_sh`. A `setsid` tail escapes the group kill of `run_cmd`, so it needs its own limit. More I/O on sdb may slow `gate_sh` (not measured). | High | M | speed | run2-33, run2-39 |
| D21 | Cache the `pdb_layout` tail. Add a `layout` kind to `buildcache.py`, keyed by cc key, dump argv and the tool hash. Key the resym `.h` by PDB sha and resymc sha. Start `gate_extra.sh` in the background (`GATE_EXTRA=defer`). Set `rc` to the worst rc. | `buildcache.py:394-430`, `gate_fast.sh:65-67`, bns-lift `tools/gate.sh:15`, `tools/pdb_layout.py:60,127-135` (open) | The tail after ninja is 80 s (p50), 70 % of `gate_sh`. 0 of 136 gates ever failed there. Claims: 76 s median per build, about 855 s per wave. The second determinism check covers only 3 TUs. Changing `gate_fast.sh` forces one base rebuild. | High | M | speed | run2-20, run2-45, run2-29 |
| D22 | Seed the base strict data. After `land_push`, copy the lander's strict output into `bases/<head>-<digest>/strict` when the delta touches only `Docs/**` and README files. Do the same for older docs-only ancestors. As a fallback, run `base_build` early (prebase hook) or in parallel with `full_build`. | `cardrun.py:1008-1032,1165`, new `Card.seed_base` (open) | 6 of 6 fresh base builds in v2b did no new work (25 of 25 strict files equal). Saves 840 s per wave of card-path time. Only 230 s is confirmed on the land chain. Shadow mode for the first wave is part of the proposal. | High | M | speed | run2-43, run2-02, run2-39, run2-05 |
| D23 | Treat accept commits (`Docs/Parity/baseline/*.json`, `progress.tsv`, `README.md`) as build-neutral in `s_plan` and `dry_checks`. Re-plan in place (plan, strict, proof, review carry) when only safe paths move. Do not rebuild. | `cardrun.py:138,841`, `author.py:1339-1347`, `landq.py check()` (open) | About 640 s per wave (18 %) in the entry. The judge in run2-43 says `parity.sh` reads the baseline for the gate. So the plan-rebuild rule must stay for it. Settle this conflict before work starts. About 190 s of the gain is a guess ❓. | Medium | M | speed | run2-31, run2-37 |
| D24 | Add a merge train. When card A is ready, rebase the queued cards onto `A.tip` and build them speculatively on a remote slot. Bind the build to the real main in the proof. | `landq.py:833`, `cardrun.py:846-857,1356`, `proof.py` (open) | It saves 1,314 slot-seconds in v2b. It saves 0 s on the v2b chain, because the rebases were not on the critical path. The worst case for one failed A is 6 x 264 slot-seconds. Large effort, small proven gain. | Medium | L | speed | run2-37 |
| D25 | Add an `early_review` step after `full_build`. First run `review.py precheck-items` (0 tokens). Then run the model review in parallel with `base_build`, strict and proof, under a provisional digest. | `cardrun.py:35,156`, `review.py:834-838,882` (open) | The gain is 435 s on the chain (12 % of the goal). The entry corrects its own premise. Base build is mostly reused, so a reject is 16 to 244 s after `full_build`. A reject also saves the later review tokens. | Medium | M | speed | run2-37 |
| D26 | Overlap phases of one gate. Start `parity.sh` when the clang build ends (a `cmake` shim). Overlap the clang and VS2010 jobs. Run funcdiff per exe in parallel. Add `--first <exes>` for the on-target exe. | `gate_fast.sh:62-72`, `gate_shims/`, bns-lift `tools/parity.sh:71-73` (open; `--first` needs a bns-lift change) | At most 179 s per wave for the shim. About 43 s per run for the job overlap. The disk (sdb at 100 % util) is the bigger limit. Some gain overlaps D21. | Low | M | speed | run2-30, run2-08, run2-14, run2-39 |
| D27 | Make `fresh_build` call `buildonce gate`. Key it on the tree without `Docs/`. Add a remote store path. Bind the toolchain digest. | `cardrun.py` (`fresh_build`), `buildonce.py` (open ❓: not traced) | One result for equal trees. Gain is not given in seconds. | Medium | M | speed | run2-25 |

## F. Remote fleet, slots, quota and hangs

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D28 | Send `full_build` and `base_build` through `slotq.py build`. The new argv is `slotq.py build bash gate_fast.sh {clone} {home}`. Try each free remote host once. Fall back to local on exit 75 or a transport error. Keep the land-chain rebuild local (`SLOTRUN_REMOTE=off`). Cap local concurrency (1 land build + 1 check build). Use critical-path-first priority. | `cardrun.py:150`, `slotq.py:39-49,1148` (`build_direct`), `build.json` (open) | After 10:00 the remote hosts ran only 2 jobs. v2b peaked at 4 of 18 slots. Gain 500-1,400 s per wave ❓. The remote push cost and cold caches reduce it. Build3 6 to 5 slots (run2-07) gives 0 gain. | High | M | speed | run2-38, run2-11, run2-22, run2-07, run2-05, run2-01 |
| D29 | Warm the remote namespace. `objsync.py seed --ns`. Force a push per namespace. Prefer warm hosts in `slotq.free_hosts`. Set `objsync: both` and `objsync_days: 3` in `hosts.json`. Use EXIT_INPUT (2) for a missing `gate.rc`. Find out why remote dispatch stopped. | `objsync.py`, `slotq.py:750-762`, `remote_build.py:421,465`, `/data/parity-v2/hosts.json` (part: `objsync_days` is read in `remote_build.py`; `hosts.json` has no `objsync` key) | The namespace is about 656 MB, so the "about 5 s" seed time is probably low. The 130-260 s per wave is a rough guess ❓. | Medium | M | speed | run2-16, run2-01 |
| D30 | Set deadlines per remote phase (push 150 s, run 450 s, pull 60 s) with `EXIT_DEADLINE` 124. Run the remote job under `setsid timeout -k 15 420`. Add `remote_build.py reap --host H` and `flock -n lock true or exit 75`. Add stuck-slot marks and down rules. Add a `child.wait(timeout=2860)` backstop in `slotq remote_once`. Add canary `--chaos cut-host`. | `remote_build.py`, `slotq.py:573`, `canary.py` (open: no `EXIT_DEADLINE`, no `setsid`; part: `SSH_KEEPALIVE` 15 s x 4 exists) | A hang at minute 20 costs 374 s, not 2,647 s. The wave would end in 1,900 s instead of 4,173 s in the entry's model. The judge confirmed `REMOTE_TIMEOUT` 2860 and the missing reap. | High | M | speed | run2-32, run1-19 |
| D31 | Add a `scope` field (model or all) to the quota pause record. Add `quota.check(need=...)`. On a model limit, stop only the steps that call a model. | `quota.py`, `sched.py`, `cardrun.py` (open) | Builds and lands continue during a model limit. The cost is a land delay. | Medium | M | speed | run1-38 |

## G. Operator, lead session and backup

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D32 | Add a lead driver. Run author, check and land under `sched.py run` (no model). Add `opstatus.py --wave DIR` (one row per card, 1.5k tokens). Enforce `warmwait.py --max 270` with a hook. Start a fresh lead from `HANDOFF.md` plus the wave table after 54 min. Send lead-fixable items to the lead, not to author cards. | `sched.py:804`, `opstatus.py`, `warmwait.py` (open: no `--wave`; `warmwait.py` exists but 0 Bash calls used it) | The lead cost 1.78M of 2.72M nocr. Cold cache rewrites after waits cost 623k (measured). The 4 compaction rewrites cost 199k. Fix A saves about 617k. Fix B about 255k ❓. The "75k per MATCH" end state assumes pod-01-like authors. That is a plan, not a measurement. | High | M | cost | run2-40 |
| D33 | Fix `sync.sh`. It exits 0 when both pushes fail (the last `git push ... && echo` fails inside `set -e` with no exit). Exit non-zero then. Run backup retry outside the landq lock with a timeout. Escalate by ntfy. Exclude `*/backup/state/` from rsync ❓. | `backup/sync.sh:96-105`, `landq.py:554` (`retry_backups`), `operator_run.py` (part: `backup_pending`, `retry_backups` and the `flock` exist; the exit code bug is still there) | A silent backup failure looks like success. Reproduced in the entry. Small change. | High | S | safety | run1-33, run1-14 |
| D34 | Use `atomicio.atomic_write_json` in the other write sites (98 sites in 34 modules). Add `dbx.py` (WAL, `busy_timeout`, `BEGIN IMMEDIATE`, `user_version`). Make `sync.sh` snapshot the sqlite files. Narrow the catches in `score.py:101` and `events.py:235`. | `atomicio.py`, `repair.py`, new `dbx.py`, `score.py`, `events.py` (part: `atomicio.py` exists and 3 modules use it; `dbx.py` is missing) | Robustness only. Speed gain is small. The `repair.py` race needs 2 callers ❓. | Medium | M | safety | run1-20, run1-35 |
| D35 | Add `gitx.py`, one shared git helper. Fix the lost guard stderr. | `cardrun.py:1415,1553`, `landq.py:547` (open; part: `GIT_TIMEOUTS` exist in `cardrun.py`) | Hardening only. The data shows 0 harm so far. | Medium | S | safety | run1-30 |
| D36 | Move run data out of the code folder to `T.state()`. Add `tests/test_no_code_folder_data.py` and `.gitignore` lines. | `parityctl/` (not checked ❓) | Keeps the repo clean. The count in the entry is slightly off (27 files, not 29). | Medium | S | safety | run1-07 |

## H. Measurement

| ID | Change | Files | Why | Gain | Effort | Type | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D37 | Add timing fields to `record_build`: `phases`, `cc_miss`, `vs_new`, `link_miss`, `fd_miss`, `gc_s`, `host`, `slot`, `cl_jobs`, `t0`, `parent_step`, `wave`. Read `gate.phases` and `cache-events.jsonl` after `full_build`. Add phase marks around gc, selftest and `pdb_layout`. Add `parityctl wave start/end`. Add the review step to the build events. | `ledger.py:401`, `cardrun.py:640-644`, `gate_fast.sh` (open) | About 30 lines. It uses data already on disk (the premise "events are lost" is wrong; `gate_fast.sh:71` copies them). It shows the cause of the 60 s to 1,358 s range and of the gc stall. 0 s gain by itself. It proves or kills D19 to D28 with numbers. | High | S | speed | run2-36, run2-04, run2-18, run2-24, run2-10 |
| D38 | Meter the lead. At each land, run `meter.measure_files` on the lead transcript. Write a `kind='lead'` event (card, t0, seconds, nocr, cold cache, compaction). | `integrate.py:255`, `meter.py:342`, `ledger.py` (open) | Lead cost is not in the ledger. True cost of v2b is 186.5k nocr per MATCH (judge). The 17k lead figure in the entry excludes overhead. | High | M | cost | run2-46 |
| D39 | Report MATCH with one counting rule: function-level diff of the baseline JSON plus new keys. Report tokens per attempt and yield per tries class. Use the 84k bar only for fresh pools. | `docs/WAVES-VS-V2.md` | The function diff gives 55 and 7. The records give +58 and +15. The three new keys and 8 new keys explain the gap. A low-effort, high-value doc fix. | High | S | cost | run2-44 |
| D40 | Add `turns.py` (about 150 lines). Parse the session log after `record_author`. Write `author_fn` events per (card, session, fn) and one `author_time` event per session. | new `turns.py`, `author.py:1184-1188` (open) | 35 % of nocr cannot be attributed to a function ❓. It wins about 1 % of the wall goal. Useful as triage evidence (63 % of nocr bought no landed MATCH). The judge says: reject a per-function cap. | Medium | M | cost | run2-41 |
| D41 | Meter leftovers. Add a `record_author` mismatch flag and a terminal 'closed' credit event. Check that a finished session over the token cap is not parked. | `meter.py`, `author.py:449-501,681` (part: `--include-partial-messages` and the `stream_event` branch exist; the over-cap case keeps status ok) | Today's 137,927 nocr per MATCH is premature. Small fixes. | Medium | S | cost | run1-09, run2-10 |

## Top 10

| Rank | ID | Change | Reason |
| --- | --- | --- | --- |
| 1 | D01 | Credit only new (exe, symbol) items | Wave 1 claimed 118 and had 33. Every number rests on credit. Effort M. |
| 2 | D33 | Fix `sync.sh` exit 0 on failed pushes | A real bug. Reproduced. Effort S. |
| 3 | D04 | Producer digests on step outputs and keys | A real digest drift happened. A re-check can credit MATCH from old tools. |
| 4 | D05 | Bind `gate.env` and `pdb_layout.json` in the proof | A real 4th hole (`lift_common`). A remote job has no check today. |
| 5 | D19 | Move `buildcache gc` off the build path | 922 s and 618 s stalls on 2 builds. Effort S. 0 tokens. |
| 6 | D28 | Send `full_build` through `slotq` | Remote hosts idle after 10:00. Peak was 4 of 18 slots. |
| 7 | D22 | Seed base strict data from the lander | 6 of 6 base builds were repeat work. About 840 s per wave. |
| 8 | D30 | Per-phase remote deadlines and reap | A hang costs 2,647 s today. It would cost 374 s. |
| 9 | D32 | Lead driver, wave status, enforced warm waits | The lead is 1.78M of 2.72M tokens. This is the main lever on the 84k goal. |
| 10 | D21 | Cache and defer the `pdb_layout` tail | 70 % of `gate_sh`. 0 of 136 gates failed there. About 855 s per wave. |

Near misses: D02 (planner trusts `ref_real` 0.645, true value about 0.31), D37 (cheap proof tool for all speed rows), D15 (honest metric and stop rule), D13 (card sharding).

Order of work I suggest: D37 first (S, proves the rest), then D01, D33, D19, then D04 with D05.

## Dropped entries

16 entries are not in the table above. One reason each.

| Entry | Reason |
| --- | --- |
| run1-02 | Done in engine. `triage.py mine-cases` and `triage-calibration.json` exist. The saving numbers were guesses ❓. |
| run1-03 | Done in engine. `sched.py` now uses `quota.limit_pattern`. |
| run1-05 | Low value. Archives 5 dead modules. The `TARGETS.md` edit is a misread. |
| run1-06 | Done in engine. `lone_constant` is in `triage.py` and its tests. |
| run1-10 | Done in engine. `CRASH_CAP` is in `sched.py` with tests. |
| run1-11 | Done in engine. `cross_exe_split` is in `triage.py` and its tests. The ranking effect was nil. |
| run1-13 | Done in engine. A `precheck` step is in `CHECK_STEPS` (`cardrun.py:134`). |
| run1-15 | Done in engine. `ledger.resolve_proofs` exists (the `proof_index` name is gone). |
| run1-18 | Mostly done in engine. `path_literal` (ease 0.9), `icf_alias`, `data_name` and `ltcg_inline` are in `triage.py`. The "3 builds saved" figure was partly a guess ❓. |
| run1-22 | Done in engine. `DEFAULT_TIMEOUTS`, `run_limited`, `GIT_TIMEOUTS` and a timeout ledger event exist in `cardrun.py`. The rsync exclude is in D33 as a ❓. |
| run1-24 | Done in engine. The canary has the chaos modes limit, crash, backup and hang. `cut-host` is in D30. |
| run1-29 | Done in engine. `landq.py:13` calls `quota.check()` before a recover and keeps exit 79 as a pause. |
| run2-09 | Weak. 0 gain on v2b waves. The judge found an error in the duplicate claim. |
| run2-19 | Done in engine. `no_gain` is in `PARK_REASONS` and `author.py` docs say the card ends `no_gain` before the proof. The 300-670 s gain was a guess ❓. |
| run2-21 | Weak. The judge set verified False (score 0.4). The 10-MATCH denominator is wrong. |
| run2-26 | Negative result. The entry says not to build the in-session MATCH tool (about 100 s, 2.8 %). |

Partly dropped inside merged rows:

- run2-07: the `build3` 6 to 5 slots change gives 0 gain. Only the routing part is in D28.
- run2-05: the headline 3,300 s is mostly realised by the warm cache. Only the slot count and parallel builds remain (D22, D28).
- run2-24: the entry itself shows review is only about 2 % of a wave. It stays as one field in D37.
- run1-19: `SSH_KEEPALIVE` is done. Only the backstop and the chaos mode remain (D30).
- run1-14: `backup_pending`, `retry_backups` and the `flock` are done. Only the exit code bug remains (D33).

## Stale and unchecked items

| ID | Problem |
| --- | --- |
| D12 | The entry names `MEASURED_FACTOR` 16.5 and `CARD_CAP` 3,000,000. The engine has 1.35 and 320,000. Re-measure before you copy a value. |
| D02, D11, D18, D27, D36 | I did not trace the exact code. Marked ❓. |
| All rows | Line numbers come from the entries. Many are off by a few lines. The design copy may differ from `/data/parity-v2`. |
