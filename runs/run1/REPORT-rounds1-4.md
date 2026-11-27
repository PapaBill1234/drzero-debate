<!-- drzero run: 20 questions, 60 calls, 2022849 tokens nocr (input + output + cache creation) -->
# REPORT: parity v2 engine, debate results (2026-11-26)

> **Note on this report**
> - The rules say "read only". So I did not create REPORT.md on disk. This text is the content for that file.
> - All evidence comes from the 18 graded answers above. I did not run the checks again, and I did not open IDA. Each file:line is the location that the answer gives.
> - All 18 answers have `verified True`. "Score" is the judge score. "Gain" is the judge's gain class.
> - Build cost uses this scale: **S** = less than 30 lines plus 1 test. **M** = 30–150 lines plus tests. **L** = more than 150 lines, or a change to the pipeline.

---

## 1. Ops (scheduler, landing, remote builds)

| Rank | Proposal | Score / gain | Evidence | Cost | Files |
|---|---|---|---|---|---|
| 1 | Add `ServerAliveInterval=15` and `ServerAliveCountMax=4` to ssh. Add a `child.wait(timeout=2860)` backstop. | 0.86 / high | `ssh -G`: `serveraliveinterval 0`. Kernel keepalive gives 7200 + 9×75 = 7,875 s before a dead host is found. During that time the card slot, the slot lock and the ssh master stay held. | **S** (2 lines + backstop + chaos canary) | parityctl/remote_build.py:175, parityctl/slotq.py:788-794, canary |
| 2 | After `land_push` is done, the land counts. A backup failure only sets `backup_pending`. landq runs the backup once. Recover states where push is done but the result is 'failed'. Use flock and rebase in sync.sh. | 0.88 / high | In real runs, 5 of 24 lands (21 %) got FAILED or parked after the push was done. Each needed a person. A landq land runs sync.sh 2 times. | **M** (6 changes + 3 tests) | parityctl/cardrun.py:1175-1185, 1382-1392; parityctl/landq.py:569-633, 811-813; parityctl/sched.py:589; backup/sync.sh |
| 3 | Make quota.py the one source of limit texts. Build `LIMIT_RE` from `quota.BILLING + quota.LIMIT`. Add a parity test. | 0.88 / medium | sched.py:97-98 does not match 11 texts that quota.classify does match. Without a PAUSE file, a limit then uses up --retries and the card parks (sched.py:548-551). | **S** (about 10 lines + 1 test) | parityctl/sched.py:97-98, parityctl/quota.py, tests/test_operator.py |
| 4 | Add a crash-wait branch with `CRASH_CAP=6`. A host or scheduler crash then does not use a retry. | 0.85 / medium | rc=None becomes rc=2 'process gone' (sched.py:426-429), and retry() then counts it. A simulation parks the card on crash 3. No real cases exist yet: the data has no sched state. | **S** (about 20 lines + 2 tests) | parityctl/sched.py:100, 432, 444, 485, 496, 805; tests/test_sched.py:375 |

## 2. Tokens (cost meters and cost estimates)

| Rank | Proposal | Score / gain | Evidence | Cost | Files |
|---|---|---|---|---|---|
| 1 | Correct the repair gate values: `P_OUT_OF_CARD` 0.1→0.6 (when a PDB record exists), `review_shape_cc` 0.4→0.6, `review_shape_imm` 0.5→0.15. Add a TLS imm form to `ltcg_layout`. | 0.70 / medium | The gate would block the 2 repairs that gave all 29 credited MATCHes. Measured shape_cc: 15/22, n=21. Most other classes have n<5 ❓. | **S** | parityctl/repair.py:104-133, exclude_policy.json |
| 2 | Split an author session when its context is larger than 100k tokens (`CTX_SPLIT`). Run gap cards through author.py, not through Agent subagents. Remove "read gap-XX-result.json" from prompts. | 0.82 / high | 40.16M beq over 16 transcripts. cache_read is 62.7 % of it. The context grows by about 2.3k tokens per call, up to about 168k. Expected saving is 25–30 % of author beq. Only the split part (about 14 %) is modelled from data. | **L** | parityctl/author.py:416-482 (next to :458), driver |
| 3 | Fix StreamMeter: read `message_delta` output counts. A `result` line must not trip the cap. | 0.86 / medium | The live meter reads 30–39 % too low (2 sessions; output 984 against 30,766). This blocks claude_runner from production. The tokens-per-MATCH figure does not change. | **M** (the message_delta pass-through is ❓) | parityctl/author.py:125-126, 357-396, 458-461 |
| 4 | Compute `review_item` from the ledger median (8,046 tokens). Count carried and precheck items as 0. | 0.85 / medium | 322 model reviews: mean 7,287 tokens, median 8,046. The constant 6,000 is too low by 21–34 %. carry() never ran: 0 of 355 reviews have carried_from. | **S** | parityctl/repair.py:98, 699 |

## 3. Quality (credit, proof, planner calibration)

| Rank | Proposal | Score / gain | Evidence | Cost | Files |
|---|---|---|---|---|---|
| 1 | Use credited MATCHes as the numerator. Set `credited` for verdict 'review' too, and add the accepts that have a current review_digest. ref_real and tokens_per_ref then use `credited`. Result-file values take priority over the feedback text. | 0.86 / high | Pooled ref_real is 0.645 on the raw delta, 0.311 on credited only, and 0.427 with accepts. feedback.py:179 reads credited only on verdict 'pass'. planner-feedback.md has wrong values for gap-24/25/26. | **M** | parityctl/feedback.py:66-69, 179-180, 527-534 |
| 2 | **Correctness issue:** all 62 stored accept receipts have review_digest bbd31df. The current review.py is dc270c96. So check_review credits 0 of them. Review them again, or keep review.py frozen during a wave. | (from 0.85 and 0.86) | integrate.check_review:85-100; quality L3 and L5 answers. | **S** to start (one re-review run, at about 8k tokens per item, so about 0.5M tokens for 62 items ❓) | review ledger, review.py |
| 3 | Fit p_new on credited MATCHes (auto credit + accepts) / ids_total. Do not add a credit rule to proof.py. | 0.85 / medium | 179 unique review items. mnem is false on 92 % of them, so no mechanical rule is safe. Credit per raw MATCH: gap24 0.43, gap23 0.56. | **S** | parityctl/feedback.py:526 |
| 4 | Add a `precheck` step (pinned, cmake, guard R7, removed /INCLUDE warning). Check lost_match right after full_build. | 0.88 / medium | 3 of the 9 proof failures are static-only, and precheck catches them in less than 1 s. 04b wasted about 26 min. gap17 lost 3 MATCHes because a commit removed `/INCLUDE` pragmas. | **M** | parityctl/cardrun.py:116, 1074-1080; guard.py |
| 5 | Print the fitted p_new, basis and n for each kind. Rewrite the REF and token rows of open drafts. | 0.85 / medium | The printed 0.80 differs from all fitted values (0.59 / 0.84 / 0.69). Job cards print REF 4.8–7.4 too high. | **S** | parityctl/plan_cards.py:869-871, 1018, 1251-1254 |

## 4. Hard (triage hints)

| Rank | Proposal | Score / gain | Evidence | Cost | Files |
|---|---|---|---|---|---|
| 1 | Add `EASE['lone_constant']=0.1`. Put the LTCG warning first in the hint. | 0.85 / high | constant has 14 of the top 50 items, 12 of them lone. The verdicts are 0 RIGHT, 4 WRONG and 1 NOT FIXABLE. All 12 come from 4 functions with bad verdicts. | **S** (about 5 lines) | parityctl/triage.py:54, 378, 404 |
| 2 | Split data_ref by ref family: use net refs, drop net-zero refs, and add the causes path_literal, icf_alias, data_name and ltcg_inline. Fix ICF naming in insn_diff. Do not case-fold paths. | 0.85 / high | 55 items in 6 families. In the top 50, 3 builds are saved for certain and up to 6 of 8 ❓. 10 `_Instance` builds are saved below the top 50 (triage-feedback.md:21). | **M** | parityctl/triage.py:307-311, 385-386; insn_diff.py:234-236 |
| 3 | Mine labelled cases from DIFF→MATCH pairs in the 114 stored runs. Gate hints on calibrated precision (≥10 cases, ≥0.7). | 0.88 / medium | 255 of 313 hints have confidence < 0.5. Confidence measures coverage, not correctness (triage.py:323). 5 causes have 0 cases. | **M** (about 150 lines + manual labels) | parityctl/triage.py:346, 404, 630 (new `mine-cases`) |
| 4 | Add a `cross_exe_split` flag and hint. When a build gives +N exes and −1 exe, keep the gain and park the lower exe. | 0.85 / low | Only 9 of 43 tail_merge items are split. They are already at rank 151 or lower. Most of the gain is the SetInvalidInfo case: +3 MATCHes, 1 park. | **M** | parityctl/triage.py:537-565, ease(), hint() |

## 5. Tools (code hygiene and IO)

| Rank | Proposal | Score / gain | Evidence | Cost | Files |
|---|---|---|---|---|---|
| 1 | Replace `proof_index` with a lazy `resolve_proofs`. Warn on a missing digest. | 0.90 / medium | The rglob takes 195.2 s. A glob of at most 3 levels takes 0.49 s. The hit ratio is 12/83 (14.5 %). 1 digest is never found (probe-compose), and 5 events have empty keys. | **S–M** + test `test_backfill_hashes_only_needed_proofs` | parityctl/ledger.py:986-1029, tests/test_ledger.py:407 |
| 2 | Add one helper, `atomicio.atomic_write_json`. Switch the concurrent writers first. | 0.80 / medium | 98 plain writes, 4 helpers. 1 real race: repair.py:1132 `running.json` is written after Popen. The data scan found 0 broken files. | **M** | new parityctl/atomicio.py; repair.py:1132, slotq.py:832, queue_build.py:884-896, buildonce.py:272-296, … |
| 3 | Move run data out of parityctl/. Change the write defaults to `T.state()`. Add the guard test `test_no_code_folder_data.py`. | 0.75 / medium | 136M of run data are in the code folder. pilot.py:61-64 reads gitignored inputs, so the pilot gate fails in worktrees. reference.sqlite is 150 commits behind HEAD. | **L** | buildonce.py:314, linked_build_*.sh, remote_build.py:542, triage.py:603/684/691, pilot.py:61-64, work_queue.py:74/78, web.py:16-17, .gitignore |
| 4 | Archive 5 dead modules (403 lines, about 4.5k tokens ❓). Correct TARGETS.md:104. | 0.80 / low | No caller found in bin/, tools, systemd, cron or *.sh. The scan of the large run folders did not finish ❓. | **S** | parityctl/{measure_build,step5_*,slice_diff}.py, docs/TARGETS.md:104, PLAN.md:11 |

---

## 6. The 10 best actions over all subjects

The order uses gain first, then judge score, then low build cost.

| # | Action | Subject | Why first | Cost | Main file |
|---|---|---|---|---|---|
| 1 | Add ssh `ServerAliveInterval=15` / `CountMax=4`, plus a wait timeout in slotq | ops | A dead host is found in about 60 s, not 7,875 s. Up to 10 slots are freed. Only 2 lines. | S | remote_build.py:175, slotq.py:788 |
| 2 | Credit stays valid: review the 62 accepts again with the current review.py, or freeze review.py during each wave | quality | Today the accepts give 0 credit, so review tokens buy nothing. | S | review ledger / integrate.py:85-100 |
| 3 | Make the land count when the push is done; run the backup once and without harm | ops | 21 % of real lands needed a person. Dependants were blocked. | M | cardrun.py:1175-1185, landq.py:811 |
| 4 | Add `lone_constant` with ease 0.1 | hard | Removes 12 dead items from the top 50, so up to 12 builds are saved. | S | triage.py:54, 404 |
| 5 | Use credited MATCHes in feedback (ref_real, tokens_per_ref, p_new) | quality | Pooled ref_real 0.645 → about 0.31–0.43. The ranking stops overrating handler cards. | M | feedback.py:179, 526-534 |
| 6 | Correct the repair gate p values | tokens | The gate would block the repairs that gave 29/29 credited MATCHes. | S | repair.py:104-133 |
| 7 | Build `LIMIT_RE` from quota.py | ops | Stops limit texts from parking good cards (audit gap 16). | S | sched.py:97-98 |
| 8 | Split the data_ref families | hard | 3 to 6 top-50 builds saved, plus 10 below the top 50. | M | triage.py:307-311 |
| 9 | Add the precheck step and an early lost_match check | quality | 3 of 9 proof failures stop in < 1 s with 0 builds. | M | cardrun.py:116, 1074 |
| 10 | Add the crash-wait branch (`CRASH_CAP=6`) | ops | A crash does not use a retry. This closes the last park-a-good-card path. | S | sched.py:432 |

Next after the top 10: the context split (tokens L4; largest saving, 25–30 % author beq, but cost L), StreamMeter (must be done before claude_runner goes to production), the lazy proof lookup (195 s → < 1 s), and atomicio.

---

## 7. Open questions

| # | Question | Source |
|---|---|---|
| 1 | Which value is correct for `review_item`: the median 8,046 (tokens L2) or the mean 7,300 (tokens L5)? 99 reviews record only the last call, so both values can be too low ❓. Recommendation: compute it from the ledger and use 8,000 as the fallback. | tokens L2, L5 |
| 2 | Cost units do not agree. `match_value` is 50k tokens, but the ledger gives 491k–1,430k beq per credited MATCH. Should the gate move to beq for value and cost together? | tokens L5 |
| 3 | Does the Claude CLI pass `message_delta` through in `stream_event`? A dry run must check this before StreamMeter change 1. | tokens L3 |
| 4 | Why did carry() never run (0 of 355 reviews)? The claimed saving of up to 0.90M tokens (51.5 %) ❓ depends on this answer. | tokens L2 |
| 5 | gap-24 is not in the ledger, so nobody can check the 44k/7 source of the old estimate. | tokens L2 |
| 6 | The repair p values for shape_imm, signature, constant, other and semantic have n < 5 ❓. Collect more data before a second refit. | tokens L5 |
| 7 | Several greps of the large run folders did not finish: dead modules, cardrun events, JSONDecodeError in cardrun/remote/canary logs. Run them in a separate session with no time limit. | tools L2, L4; quality L4 |
| 8 | The context-split saving (14 %) and the start-context trim (about 11k tokens ❓) are estimates. Remeter one card to check them. | tokens L4 |
| 9 | Does the cross-exe ease multiplier hurt data_ref items? Check before shipping. | hard L4 |
| 10 | The tools L4 answer reports a rule break: it wrote 2 scratch files. Check where these files are, and delete them if they are inside a tracked tree. | tools L4 |
| 11 | How many DIFF→MATCH pairs do the 114 runs really hold? The value of the case-mining plan depends on this number. | hard L2 |
| 12 | gap-20 counts its credit against a 674 baseline, while its raw delta is at 687. Sibling cards count 20 of 250 MATCHes 2 times (8 %). Which baseline should the credit use? | quality L5 |
