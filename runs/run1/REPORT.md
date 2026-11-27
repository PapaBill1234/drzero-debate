<!-- drzero run: 39 questions, 120 calls, 4936268 tokens nocr (input + output + cache creation) -->
# REPORT — parity v2 engine: graded proposals

## 0. Scope and method

- Input: 34 graded questions from 5 subjects (tokens, hard, ops, quality, tools), levels L2–L9. All are `verified True`.
- I re-measured nothing. No shell or file tool was available, and IDA is not allowed. Each number comes from the graded answer and keeps the file:line that the answer gives.
- Status ("open", "landed ❓") comes from commit messages in the git snapshot (`cd12f1d9`, `b3bd6219`) and from fix commits that ops L6 names (`b910aaec`, `758a9321`). I did not check the code.
- Rank = gain × evidence strength. Score ≥ 0.85 and a measured gain come first. Gains that rest on estimates have ❓.

### 0.1 A caveat that changes many numbers

tokens L7 found two facts:
- 28 of the 29 credited MATCH come from no card.
- The cause: the `Docs/Parity` baseline is 645, but a fresh REF build of d5b3dc3 gives 673.

So these numbers are wrong until someone re-pins the baseline:
- the ledger "1,472k beq per credited MATCH",
- the repair value gate (tokens L5),
- the ref_real fits (quality L5, L8).

Re-pin the baseline first.

---

## 1. Tokens

| # | Proposal | Source | Gain (evidence) | Cost | File | Status |
|---|---|---|---|---|---|---|
| T1 | Order the card scope by reachability. Move bodies that the model predicts as unreachable to a "Deferred: needs root R". Schedule one unlock card for each root first. Fix the calibrate parser crash. | tokens L7 (0.80) | 82 % of metered author beq (31.8M of 38.8M) went to group (c) bodies. Without them, beq per credited MATCH goes from 1,472k to 378–526k. With credit in the unlock cards, about 190k ❓. Model precision 0.97, recall 0.95. | Medium: render_card, plan, an unlock-card rule | plan_cards.py:852, :1310 | open ❓ |
| T2 | Re-pin the proof baseline to a fresh build of the base rev (673, not 645). | tokens L7 | Without it, the ledger does not see the real gain. 28 of 29 credits are baseline drift. | Small | Docs/Parity/baseline (bns-lift) | open ❓ |
| T3 | Shard `--no-packet` cards to at most 10 distinct PDB names and a start prompt of about 30k tokens or less. Let proof-text cards write the handoff early. | tokens L6 (0.80), quality L7 (0.85) | lg-01 lost 417,607 units with no edit. About 1.6M cost units saved over 4 cards. cg-01 (10 names) finished at a 61k peak. | Small: mkcard.py; or `card_shards()` in author_packet.py:274 | v2batch/tools/mkcard.py, author.py:900, :978 | open ❓ |
| T4 | Use one unit, beq, from the ledger to the cap: feedback reads meter beq, MEASURED_FACTOR 16.5, CARD_CAP = author card_cap 3M. | tokens L5 (0.85) | Today's ranking does not change. The reported cost per REF is 41k but the metered cost is 863k (21×). 5 of 8 metered cards went past 3M. The planner can split gap-18 and gap-25 before the author parks them. | Small; ship both parts in one change | feedback.py:155, plan_cards.py:89-92 | open ❓ |
| T5 | Split the context (CTX_SPLIT), run cards through author.py, and drop the "read result JSON" text from prompts. | tokens L4 (0.82) | About 25–30 % of author beq. A tool-output cap alone saves only 0.8–2.8 %. | — | author.py:123 | split exists (author.py:123); the rest ❓ |
| T6 | StreamMeter: read `message_delta`. Do not let a `result` line trip the cap. | tokens L3 (0.86) | The live meter reads 30–39 % low. The cap reads 1.43–1.65× low. | Small | author.py:125, :357-396, :458 | open ❓ |
| T7 | Get review_item from the ledger median and count carried items as 0. | tokens L2 (0.85) | The measured mean is 7,287 and the median 8,046, against 6,000. Up to 51.5 % of review tokens are re-reviews ❓. | Small | repair.py:98, :699 | open ❓ |
| T8 | Repair gate: P_OUT_OF_CARD 0.6, shape_cc 0.6, shape_imm 0.15. | tokens L5 (0.70) | The gate today blocks the 2 repairs that gave all 29 credits. n < 5 in most classes ❓. | Small | repair.py:104-133 | open; wait for T2 |

## 2. Hard (triage)

| # | Proposal | Source | Gain | Cost | File | Status |
|---|---|---|---|---|---|---|
| H1 | Run triage again on the current main (rev 6824f3d or later). Add a structural band below 85 and a park list that the scheduler and plan_cards obey. Feed unmatchable-draft.md into the park list. | hard L9 (0.85) | 18 of the 116 are already MATCH. 70 have no body fix. 46 go to agents instead of 116. About 230 builds per round ❓. | Medium: band_items plus a 30-line EH reader | triage.py:59, :724; plan_cards; author.py | open ❓ |
| H2 | instruction_order: filter non-callee tokens, add order_class, group_key and a STALE mark. | hard L8 (0.80) | 0 of 33 items is a clean swap. About 12 fewer builds in the top 50, and 7 more outside it. | Medium | triage.py:178-182, :412 | open ❓ |
| H3 | Call family: add detail.inline_dir and one hint and ease for each class. Group items by callee. | hard L7 (0.80) | 28 of 40 hints point the wrong way. About 10 builds saved. 5 noinline clusters. | Medium | triage.py:208, :376-381, :67 | open ❓ |
| H4 | data_ref: compute net refs. Split into path_literal, icf_alias, data_name and ltcg_inline. Fix the resolver ICF naming. | hard L5 (0.85) | 3 certain builds saved in the top 50 (up to 6 of 8), plus 10 _Instance builds below it. | Medium | triage.py:307-311, insn_diff.py:234 | open ❓ |
| H5 | Mine labelled cases from DIFF→MATCH run pairs. Gate a hint on calibrated precision. | hard L2 (0.88) | 255 of 313 hints are unmeasured. About 75 wasted rebuilds per pass ❓. | About 150 lines | triage.py:346, :404, :630 | open ❓ |
| H6 | branch_inversion: one hint for each tail direction. No ease factor. | hard L6 (0.86) | 3 top-50 items get a direction-specific hint. 2 or more builds were wasted on them. | Small | triage.py:381 | open ❓ |
| H7 | Cross-exe LTCG split flag and a "keep gain, park the lower exe" rule. | hard L4 (0.85) | 9 of 43 tail_merge items. +3 MATCH from feedback line 18. Rank effect is small. | Small | triage.py:537-565 | open ❓ |
| H8 | lone_constant demotion. | hard L3 (0.85) | 12 lone items leave the top 50. | — | triage.py:404 | landed ❓ (hard L8: "already in the code", 27b1b93b) |

## 3. Ops

| # | Proposal | Source | Gain | Cost | File | Status |
|---|---|---|---|---|---|---|
| O1 | Scoped pause: `scope` model or all, and `check(need=)`. Only author, review with pending items and the repair author kind need `model`. | ops L9 (0.86) | 10 READY cards with 0 review items land in about 40 min instead of up to 8 days (80 card-days). 88 % of check step-seconds do not call a model. | Medium: 9 gates | quota.py:211-263, sched.py:323/674, cardrun.py:526/1648, landq.py:461/513, buildonce.py:282 | open ❓ |
| O2 | backup_retry in operator_run, outside the landq lock, with a timeout and escalation. sync.sh must exit non-zero when a push fails. | ops L8 (0.86) | Today a failed push exits 0, so nobody sees it. The sched path never retries. One backup can hold the land queue for 900 s or more. | Medium | operator_run.py, landq.py:489-503/923, backup/sync.sh:95-102 | open ❓ |
| O3 | ssh `ServerAliveInterval=15`, `CountMax=4`, plus a wait timeout in slotq. | ops L5 (0.86) | A dead host is found in about 60 s, not about 7,875 s (130×). Up to 10 slots are freed. | About 3 lines | remote_build.py:175, slotq.py:788 | ssh part open (ops L6); canary hang mode landed ❓ (cd12f1d9) |
| O4 | One list of limit texts (LIMIT_RE built from quota). | ops L2 (0.88) | 11 texts no longer use up --retries. | — | sched.py:97 | landed ❓ (b910aaec) |
| O5 | Crash waits do not count as retries (CRASH_CAP 6). | ops L3 (0.85) | 3 crashes no longer park a good card. | — | sched.py:432 | landed ❓ (b910aaec) |
| O6 | A failed land_backup after the push keeps the land. | ops L4 (0.88) | 5 of 24 lands (21 %) were false FAILED. | — | cardrun.py:1175 | landed ❓ (758a9321) |
| O7 | Canary chaos modes limit, crash, backup and hang. | ops L6 (0.87) | End-to-end cover for L2–L5. | — | canary.py | landed ❓ (cd12f1d9) |
| O8 | landq recover: pause and busy do not use the recover budget. | ops L7 (0.86) | A good card no longer parks after about 10 min with "dead lander". | — | operator_run.py:844-887 | landed ❓ (cd12f1d9) |

## 4. Quality

| # | Proposal | Source | Gain | Cost | File | Status |
|---|---|---|---|---|---|---|
| Q1 | Split p_new into stub-free and stub-blocked. Land the stub owners first (gap-15, then gap-04). | quality L6 (0.80) | P1 precision 1.000 and recall 0.479. p_blocked is 0/92 and p_free 0.774. About +40 NOREF MATCH on the finished set ❓. No rounds on 92 bodies with p = 0. | Medium | plan_cards.py:251-261, :331, :765 | open ❓ |
| Q2 | mkcard filter: drop park, unverified and level A/B items. Sort by ease. Refuse a card with fewer than 3 items. | quality L9 (0.80) | 29 of 59 items gave 0 MATCH. About 1.4M cost units ❓. | Small | v2batch/tools/mkcard.py:42-48 | open ❓; the no_gain round landed ❓ (b3bd6219) |
| Q3 | Deduplicate credit per (exe, symbol) in a credited_items table. real_ref then uses the deduplicated credit. | quality L8 (0.80) | Wave 1 claims 118 against 33 real. Wave 2 has 33–46 double counts. ref_real 0.698 → 0.613. | Medium | integrate.py:119-125, :289; feedback.py:163-165 | open ❓ |
| Q4 | feedback: set credited for verdict `review`, and use credited as the ref_real numerator. Stop feedback.md from overriding result files. | quality L5 (0.86) | Pooled ref_real 0.645 → about 0.31 (about 0.43 after re-review). Fixes the gap-24/25/26 errors. | Small | feedback.py:66-69, :179, :527-534 | open ❓ |
| Q5 | Re-review the 62 accepts that have the stale review digest (bbd31df). | quality L3 (0.86), L5 | Today check_review counts 0 of 62 accepts. | Review tokens: 62 × about 7.3k ≈ 450k ❓ | review.py, receipts | open ❓ |
| Q6 | A `precheck` step (R2, R3, R7, include_removed) and an early lost_match check after full_build. | quality L4 (0.88) | 3 of 9 stored failures fail in under 1 s with 0 builds. About 26 min was wasted on 04b. | Medium | cardrun.py:116, :1074-1080 | open ❓ |
| Q7 | Print the fitted p_new and basis in the method text and the drafts. | quality L2 (0.85) | Job cards no longer show a false shortfall of 4.8–7.4 REF. | Small | plan_cards.py:869, :1018, :1251 | open ❓ |

## 5. Tools

| # | Proposal | Source | Gain | Cost | File | Status |
|---|---|---|---|---|---|---|
| L1 | Compute checker_digest from the import closure plus the script closure (checkerset.py, LEGACY list), and add the closure test. | tools L8 (0.85) | 13 or more unhashed files and 3 config groups. A real drift ran from 20:07 to 01:47 (gate_fast.sh was not hashed). 0 false credits so far. | Medium | proof.py:63-86, buildcache.py:787, cardrun.py:636 | open ❓ |
| L2 | run_cmd wall-clock limits with a process-group kill. | tools L5 (0.88) | 2 hung backups held a slot for 8,178 s. 6,378 s saved. | — | cardrun.py:454 | landed ❓ (cd12f1d9) |
| L3 | Lazy proof lookup (resolve_proofs). | tools L3 (0.90) | 195.2 s → under 1 s. Finds the 13th digest. | Small | ledger.py:986-1029 | open ❓ |
| L4 | dbx.connect with roles, WAL and user_version. Fix sync.sh **before** WAL. | tools L7 (0.86) | A writer stalls ≤ 0.058 s instead of 3.07–3.45 s. 0 lock errors seen so far, so this is hardening. | Medium | new dbx.py, receipts.py:112, backup/sync.sh | open ❓ |
| L5 | atomic_write_json. Start with repair.py:1132. | tools L4 (0.80) | Closes 1 double-run race. 0 torn writes seen. | Medium | new atomicio.py | open ❓ |
| L6 | gitx.run (not a checker). Fix the guard stderr loss at its callers now. | tools L6 (0.88) | Error text is the same everywhere. 0 harm seen. | Medium | cardrun.py:1415/1553, landq.py:547 | open ❓ |
| L7 | Move data out of parityctl/ and add a guard test. | tools L3 (0.75) | About 128M (about 0.8M tokens) leaves the code folder. pilot.py gate works in worktrees. | Medium | buildonce.py:314, triage.py:684/691, pilot.py:61 | open ❓ |
| L8 | Archive 5 dead modules. | tools L2 (0.80) | 403 lines (about 4.5k tokens ❓). | Very small | parityctl/ | open ❓ |

---

## 6. The 10 best actions over all subjects (open items only)

| Rank | Action | Subject | Why first | Main file |
|---|---|---|---|---|
| 1 | Re-pin the proof baseline to a fresh base build (673). | T2 | Every credit-based number and fit depends on it. Very small cost. | Docs/Parity/baseline |
| 2 | Order the scope by reachability, plus unlock cards. | T1 | Largest measured beq gain: 1,472k → 378–526k per MATCH. | plan_cards.py:852 |
| 3 | Split p_new into stub-free and stub-blocked, and land the stub owners first. | Q1 | Precision 1.0. No rounds on 92 bodies with p = 0. Fits with #2. | plan_cards.py:251-261 |
| 4 | Re-run triage on main, add the structural band and a park list the scheduler obeys. | H1 | Removes 70 of 116 functions with no body fix. About 230 builds per round ❓. | triage.py, plan_cards |
| 5 | mkcard filter (no park, unverified or level A/B items). | Q2 | 49 % of the batch items gave 0 MATCH. About 1.4M units ❓. | v2batch/tools/mkcard.py:42 |
| 6 | Shard `--no-packet` cards to at most 10 names. | T3 | About 1.6M cost units. Stops parks with no edit. | mkcard.py / author_packet.py:274 |
| 7 | Deduplicate credit and use credited as the ref_real numerator. Re-review the 62 stale accepts. | Q3 + Q4 + Q5 | The planner calibration is wrong by about 2× today. | integrate.py:119, feedback.py:179/527 |
| 8 | Scoped pause (model or all). | O1 | 80 card-days of land delay per weekly limit. | quota.py, sched.py, cardrun.py, landq.py |
| 9 | backup_retry outside the landq lock, and sync.sh push failure exits non-zero. | O2 | A silent backup loss today. The land queue can block for 900 s or more. | operator_run.py, backup/sync.sh |
| 10 | Closure-based checker digest plus the closure test. | L1 | A digest drift really happened. Cost stays flat (0 of 9 changes were comment-only). | new checkerset.py, proof.py:63 |

Next after these: T4 (beq unit and cap), H2 and H3 (triage hints, about 22 builds), O3 ssh keepalive (3 lines, 130× faster detection), Q6 precheck.

## 7. Open questions

1. **Status check.** Confirm in code that ops L2/L3/L4/L6/L7, tools L5 and the no_gain round landed. The source is commit messages only ❓.
2. **O3 status.** Is `ServerAliveInterval` now in `SshTransport.ssh_argv`? ops L6 says it was open. `cd12f1d9` added only the canary hang mode ❓.
3. **review_item value.** tokens L2 says the median is 8,046. tokens L5 says the mean is 7,300. 99 reviews count only the final call, so the true value is higher ❓. Choose one rule.
4. **match_value units.** Should match_value stay at 50k, or change to beq (about 491k–1,430k)? Wait for the baseline re-pin (#1).
5. **Order of T1 and Q1.** Both change gains() and the scope. Do them in one change, or do Q1 first?
6. **WAL safety.** sync.sh rsyncs the 109 tracked backup ledgers. Is a snapshot with backup() enough, or must ledgers stay in DELETE mode?
7. **INLINE-GAP Character group (hard L8).** Is it PGO partial inlining? No experiment has run yet ❓.
8. **Unbounded greps.** Run the full greps for the 5 dead modules (tools L2) and for "database is locked" with no time limit before you delete anything.
9. **Scratch files from earlier rounds.** tools L8 left `/tmp/x` (108 lines). tools L4 says it wrote 2 scratch files. Remove them.
10. **Canary run after the fixes.** No canary run is kept after `b910aaec` and `758a9321`. Run `canary --chaos limit,crash,backup,hang` once to confirm.
