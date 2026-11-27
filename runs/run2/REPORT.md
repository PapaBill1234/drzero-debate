<!-- drzero run: 47 questions, 143 calls, 6552411 tokens nocr (input + output + cache creation) -->
# REPORT — parity v2 debate, run 2 (2026-11-26)

## 0. Scope and base numbers

This report merges the graded answers of the run. It does not repeat run 1 lessons. All gains are on the v2b wave of 2026-11-26. Gains do not add. Section 3 gives the combined estimate.

| Base number | Value | Source |
|---|---|---|
| v2b land chain | 6,567–6,670 s (13:27:08Z → 15:38:39Z) | measure L5, fleet L9 |
| Build + tests on the critical path | 4,558 s | fleet L9 |
| Goal | builds + tests ≤ 3,600 s | owner |
| True wave cost, all actors | 2,797,956 nocr / 15 MATCH = **186.5k per MATCH** | measure L10 |
| Author-only figure (lead not counted) | 68.2k per MATCH | measure L7. Do not use it as the wave cost. |
| Cost goal | < 84k nocr per MATCH | manual wave, 4.89M / 58 (cost L8) |
| Fleet use | peak 4 concurrent builds out of 18 slots | fleet L9 |

Main findings:
1. The wave is limited by its critical path, not by fleet size. Do not buy capacity for this goal (fleet L9).
2. Three stalls dominate the path: the `gc` tail, the uncached pdb_layout tail, and fresh base builds of docs-only mains.
3. cardrun never calls slotq. For this reason all 28 card full_builds ran locally while 10 remote slots stood idle (fleet L6, walltime L7).
4. The lead uses 63 % of nocr. 7 of 8 author cards bought 0 MATCH (measure L10, cost L4/L6).
5. Several safety holes are real. One of them already gave credit: gap-int-2 landed 29 MATCH from a gate with no layout check (safety L7).

---

## 1. Per subject

Order: verified gain first, then evidence strength. "Path s" = seconds removed from the land chain.

### 1.1 Walltime

| # | Proposal | Path gain | Evidence | Build cost | Files |
|---|---|---|---|---|---|
| W1 | Move `buildcache.py gc` out of the gate. Run it in the background with `flock -n`, `ionice -c3`, a 6 h stamp and its own `gc.log`. Write `gate.rc` and `rc=` first. | 617–922 s (17–26 %) | L3, L4, fleet L9. gc removed 0 entries in all runs. The cause of the stall is disputed (see Q1). | about 8 lines | `parityctl/gate_fast.sh:72-78` |
| W2 | Cache pdb_layout per TU. The key is the cc key + the dump argv + the script sha. The value is the parsed records. Start gate_extra in parallel with vsobj_restore and parity_sh. Set `rc = max`. | 578 s safe (16 %). Up to 855 s at 4 slots (24 %). | L5, pipeline L9, safety L7. Tail p50 80 s, p90 125 s, 2,461 s over 30 builds. Dumps are byte-identical. | about 80 lines plus the S5 fail-closed rule | `buildcache.py`, bns-lift `tools/pdb_layout.py:127-135`, `tools/gate.sh:15`, `gate_fast.sh:65-67` |
| W3 | Seeded bases. At land, copy the lander strict JSON into `bases/<head>-<digest>/strict`. Do this only when the delta touches only Docs/**, README, CLAUDE or AGENTS and the digests are equal. Hook B walks up to 20 first parents. | 230 s confirmed, up to 634 s ❓ (6–18 %) | L8, pipeline L3. 25/25 strict files are byte-equal. 6/6 fresh bases were 100 % cache hits. | 1 function and 3 hooks, plus shadow mode in the first wave | `cardrun.py` (s_strict, land after land_push, s_base_build) |
| W4 | Treat a docs-only main move as build-neutral. Re-run only compare, proof and review carry. Do not use `--reset`. | about 640 s (18 %). Overlaps with W3 and P2. | L6 | small | `cardrun.py` s_plan :840, dry_checks :1356; `author.py` MAIN_MOVED branch |
| W5 | Run vsobj restore in parallel with wine_setup and gate_sh. Run vsobj record after `gate.rc` under a tail lock. Write the index in try/finally. | 107–120 s (3 %) | pipeline L7, fleet L9 (309 s in the replay) | about 30 lines | `gate_fast.sh:65-76`, `buildcache.py:668-677` |
| W6 | Overlap gate_sh and parity_sh (a cmake shim, or a prep step plus 2 branches) | 43–46 s median per gate (1–5 %) | pipeline L4, walltime L6. Do not do this together with W2: the gains do not add, and the disk is saturated. | medium | `gate_fast.sh` |

### 1.2 Fleet

| # | Proposal | Path gain | Evidence | Build cost | Files |
|---|---|---|---|---|---|
| F1 | Send cardrun full_build and base_build through `slotq.py build` at run time (not in COMMANDS, so the digests stay the same). Keep land-chain rebuilds local, with a cap of 1 land build + 1 check build. | 598 s (17 %), range 500–1,400 s ❓ | fleet L6, walltime L7. 0 'slotrun:' lines in 31 logs. `build_direct` has no caller. 10/10 remote slots were free at each build start. | about 15 lines | `cardrun.py:669` run_cmd; `hosts.json` |
| F2 | Turn on objsync: `"objsync": "both"` (or "push"), `objsync_days` 3, plus a namespace seed at wave start | 125 s per remote build (163–192 s → 20–51 s); about 2 min per wave | fleet L3, L5. A copy takes 3.3 s for 122 MB. | config + `objsync.py seed` | `hosts.json`, `remote_build.py:416`, `slotq.py:761` |
| F3 | Per-phase deadlines (push 150 s, run 450 s, pull 60 s), a remote `setsid timeout 420`, a reaper, `flock -n` before push, and a stuck-slot skip | Protects 2,273 s when a host hangs (4,173 s → 1,900 s in the simulation) | fleet L8. The fix adds 0 tokens. | about 100 lines plus a test | `remote_build.py`, `slotq.py` |
| F4 | Classify rc correctly: use EXIT_INPUT (2), not 3, when gate.rc is missing. Use the cool-down only for ssh 255 and rsync faults. | Stops one bad job from blocking 10 slots for 600 s | fleet L3. All 4 rc-3 rows came from one setup bug. | small | `remote_build.py:421,465` |
| F5 | Set build3 to 5 slots and keep cl_jobs at 4. Write the sizing rule into hosts.json. | 0 s (latency and safety only) | fleet L4 | config | `hosts.json` |

Do not do: cl_jobs 2 (gain 0); a shorter cool-down (0 real transport faults); plan "first job local" (it loses 0.5–1.5 min).

### 1.3 Pipeline

| # | Proposal | Gain | Evidence | Build cost | Files |
|---|---|---|---|---|---|
| P1 | Early review. Run precheck and the model review right after full_build, in parallel with base, strict and proof. Use a provisional digest D0. Carry the receipt to the final digest. | 435 s path (12 %) | pipeline L8. Replay target: merge-03b stops at 15:26:03. | 1 new step | `cardrun.py:35` step order; `review.py:882` |
| P2 | Merge train. When A is ready, build B on A.tip. Bind build_tree and spec_parent in the proof. | 1,314 slot-s. 0 s path in v2b. Worst case 6 × 264 slot-s per failed A. | pipeline L8, walltime L6 | large | `landq.py:833`, `cardrun.py`, `proof.py` |
| P3 | Park `no_gain` cards before cardrun (compare gain 0, lost 0; not merge, wmain or tools-lane cards) | 2,939 step-s; 300–670 s wall ❓ | pipeline L5. lg-01a was rebuilt 5 times. | small | `author.py:144`, before s_proof |
| P4 | On-target exe first, with early failure in parity.sh and strict | 1–4 min ❓ | pipeline L5 | medium, bns-lift change | `gate_fast.sh:67`, `tools/parity.sh` |

Do not do: reuse of author gate builds (rev never matched, 0/8); an in-session preview MATCH tool (a preview MATCH is right only about 21 % of the time on v2b, pipeline L6).

### 1.4 Cost (tokens per MATCH)

| # | Proposal | Token gain | Evidence | Build cost | Files |
|---|---|---|---|---|---|
| C1 | Card selection. Keep `constant`, `missing_call` and structural rows (wmain, EH funclet, unpaired). Drop proof A/B rows. Put at most 6 rows on one card. Add a `tries` dimension and the stop rule E = c_attempt/p > 168k. | −749k nocr (186.5k → 137k per MATCH). About 1,380 s author wall. | cost L6, L8, L4-cards, measure L10. 7/8 author cards gave 0 MATCH. | medium | `v2batch/tools/mkcard.py:46`, `parityctl/triage.py`, `feedback.py`, `plan_cards.py` |
| C2 | Lead driver. Run the waves through `sched.py run`. The lead never waits > 270 s (`warmwait.py`). Add `opstatus.py --wave` (≤ 1.5k tokens). | −617k measured, −255k more ❓. Wave 181k → 123k per MATCH. | cost L7. 35 % of lead nocr is cache rewrites after waits; 11 % is compaction. | medium | `sched.py:804`, `opstatus.py`, lead brief and hook |
| C3 | Item-state table in the split handoff (≤ 800 tokens, no model call) | 67–150k units on pod-01 x01 | cost L5 (pod-01) | about 60 lines | `author.py:1211-1236` handoff_text |
| C4 | Run all authors through author.py with the deny list (no in-session waits, no hr reads, `BASH_OUTPUT_CHARS` 8000) | 11–14k per MATCH | cost L3 (ad-hoc sessions) | small | `author.py:145` DENIED |
| C5 | Replay transport for engine test cards; give their reviews group=test | about 1.7M per engine campaign, 0 per wave | cost L4 | small | `review.py:802`, `ledger.py:524` |

Combined: C1 + C2 give about 82k per MATCH ❓ (measure L10). This is the only path under 84k found so far. It holds only for fresh pools (see Q3).

Not verified: the "cost L5 score 0.40" packet answer failed its check. Do not use its 73.2k figure. One fact from it holds: all 8 v2b runs used `--no-packet`.

Do not do: fixes A/B/C on parked cards (they save 0 units, cost L4-park); a per-function call cap (it cuts 4 of 6 MATCH, measure L9); a 60k digest split (+20.6 % nocr).

### 1.5 Measure

| # | Proposal | Gain | Evidence | Build cost | Files |
|---|---|---|---|---|---|
| M1 | Build events carry t0, host, slot, cl_jobs, overlap, parent_step, wave, phases and cache counts. Read them from gate.phases and `clone/build-vs2010/cache-events.jsonl` (both exist). Record failed steps too. | 0 s. Makes W1–W5 and F1 provable. | measure L4, L5, L8 | about 30–60 lines | `cardrun.py:640-644`, `ledger.py:401` |
| M2 | Meter the lead at each land (`meter.measure_files`). Store the commit list and actor per land. Add match_symbols to credit. | 0 s. Gives nocr per MATCH per actor. | measure L10 | about 40 lines | `integrate.py:255`, `meter.py:342`, `ledger.py:405` |
| M3 | Credit chain check: proof_path, main_match_before/after, excluded, wave. Add `verify_match_chain`. | Blocks query errors of −31 %, +34 % and ×2.9 | measure L7. Chain 3520 → 3535 = +15, verified. | about 40 lines | `integrate.py:253`, `ledger.py:405`, `proof.py:194` |
| M4 | Fix the meter: a `stream_event` branch for output; a `closed` credit with ref_match 0; a required `wave` | Fixes a +40k error in split sessions | measure L4 | about 50 lines | `meter.py:253`, `ledger.py:384,408` |
| M5 | Review timing and the draw type (model, precheck, carry) | 0 s. Review is ≤ 139 s of the path. | measure L6 | about 40 lines | `cardrun.py:640`, `ledger.py:627` |
| M6 | `wave_start` and `wave_end` events; HANDOFF stamps from `date -u` | 1,216 s of pre-ledger time becomes visible | measure L5, L10. The HANDOFF clock labels are false. | small | new `parityctl wave` command |

### 1.6 Safety

Each speed fix in 1.1–1.2 has a safety guard here. Ship the guard together with the fix or before it.

| # | Proposal | Guards | Evidence | Cost per wave | Files |
|---|---|---|---|---|---|
| S1 | pdb_layout fail-closed. Write a `pdb_layout.json` summary, fail on a non-executable gate_extra, and bind `names_bind` in proof. Integrate refuses a proof without it. | W2 | safety L7. 17/66 cardrun gates had no layout check. gap-int-2 got 29 MATCH credit. | about 0.22 s per gate | `tools/gate.sh:15`, `pdb_layout.py`, `proof.py`, `integrate.py` |
| S2 | Host env digest in `gate.env`. Bind it in R8 and compare it in integrate. Audit K = 1 proof per host per wave. | F1, F2 | safety L6. Probe 0.48–1.66 s. | about 0.6 s per job, 420 slot-s audit | `gate_fast.sh`, `remote_build.py`, `proof.py`, `integrate.py:check_proof` |
| S3 | Producer digests on build and strict output. Check them in build_ok, strict reuse and proof_current. | W3, W4, P1 | safety L8 | 0 s on v2b, ≤ 230 s on a script change | `cardrun.py:725,773,1057,1381-1400`, `proof.py` |
| S4 | Extend tool_digest: checker_digest, remote_build, shims, funcdiff tools, capstone, pefile, pdbutil. Refuse an unstamped `--strict-base`. | W3 | safety L4. A stale base can hide a regression. | 0–214 s per change | `cardrun.py:637-641` |
| S5 | Deterministic review rules P4–P9, recomputed in integrate. Add a canary fixture test. | review cuts | safety L9. The model rejects only 38 % of known defects. | −3.3k nocr per MATCH | `review.py:259`, `integrate.py:106`, `tests/test_review_canary.py` |
| S6 | R9 safety_guard (G1+G3) in proof. Split the digest into build_digest and rule_digest. | all auto credit | safety L9. 10/10 hits were false positives; add the arity filter. | ≤ 1 s per card | `proof.py`, `edit_guards.py` |
| S7 | Wrapper sha + sys.version in the fd and pickle keys; a canary of 2 fd hits per wave | fd cache | safety L3-fd | about 24 s per wave canary | `buildcache.py:780-794`, `funcdiff_cached.py:40`, `buildonce.py:117` |
| S8 | 2-draw accept before carry; collapse whitespace in S before the digest | review carry | safety L5 | +1.46k per MATCH | `review.py`, `ledger.py:493`, `receipts.py:363` |

---

## 2. The 10 best actions

| Rank | Action | Subject | Gain (1 h goal) | Tokens per MATCH | Pre-req | Main file |
|---|---|---|---|---|---|---|
| 1 | Move gc out of the gate (W1) | walltime | 617–922 s path (17–26 %) | 0 | none | `gate_fast.sh:76` |
| 2 | Card selection + tries stop rule (C1) | cost | about 1,380 s author wall | −49k (186.5k → 137k) | M2 to prove it | `mkcard.py`, `triage.py` |
| 3 | Lead driver + opstatus (C2) | cost | about 600 s ❓ | −41k to −58k | none | `sched.py`, `opstatus.py` |
| 4 | pdb_layout cache + parallel + fail-closed (W2 + S1) | walltime, safety | 578 s safe (16 %) | 0 | S1 in the same change | `pdb_layout.py`, `buildcache.py`, `gate_fast.sh` |
| 5 | cardrun full_build/base_build through slotq (F1 + F2 + S2) | fleet | 598 s (17 %) | 0 | S2 env digest, F4 | `cardrun.py:669`, `hosts.json` |
| 6 | Seeded bases + digest fix (W3 + S4 + S3) | walltime | 230–634 s (6–18 %) | 0 | S4, shadow wave | `cardrun.py` |
| 7 | Early review in cardrun (P1) | pipeline | 435 s (12 %) | about 0 | S3 | `cardrun.py`, `review.py` |
| 8 | Ledger instrumentation (M1 + M2 + M3) | measure | 0 s, makes ranks 1–7 provable | 0 | none | `cardrun.py`, `integrate.py`, `ledger.py` |
| 9 | Remote deadlines + reaper (F3) | fleet | protects 2,273 s per host hang | 0 | F1 | `remote_build.py`, `slotq.py` |
| 10 | Deterministic review rules + canary (S5) | safety | < 1 % | −3.3k | none | `review.py`, `integrate.py` |

Combined estimate (not additive): the fleet L9 replay with W1 + W5 + prebase gives 4,558 s → 2,861 s of builds and tests on the path. That is inside the goal. W2 and F1 add more margin ❓. For cost, ranks 2 and 3 give about 82k per MATCH ❓, but only on fresh pools.

Order of work: 8 → 1 → 4 → 6 → 5 → 9 → 7; 2, 3 and 10 run in parallel (no build code is shared).

---

## 3. Open questions

| # | Question | Why it matters | Cheapest test |
|---|---|---|---|
| Q1 | What caused the 14:02–14:18 stall? cg-01 and pod-01 both ended at 14:18:04. walltime L4 says a cold gc walk on HDD sdb. fleet L6, L9 and measure L8 say the cause is unknown (a cold walk today takes 0.28 s; the journal was steady). | W1 fixes the symptom. If the cause is a SIGSTOP or an I/O stall, it can hit other steps. | Time `gc()` with `max_bytes=10**15` after `drop_caches`, under a load like the wave's |
| Q2 | Is the remote output byte-equal to the local output for card revs, not only for self-test revs? | F1 safety | Audit K = 1 from S2 |
| Q3 | Is 84k a fair bar? cost L8: the retried pool needs about 500k per MATCH (manual process). | It decides whether the cost goal can be met at all | Track yield per `tries` class in the next wave |
| Q4 | The review token median: 1,807 nocr (ledger, safety L9) or 16,894 (brief)? | Review cost cuts | One query with the M4 meter fix |
| Q5 | Edit tool tail up to 19.4 s with no hooks | ≤ 158 s (4.4 %) | M1 `author_time` events |
| Q6 | Who took `build2.slot1.lock` at 13:10 without slotq? | A hidden remote user | Log the caller in `try_lock` |
| Q7 | Disk: sdb at 100 % util and 38–59 % iowait during the wave | It limits W5, W6 and the local slots | Move clones and the store to SSD or the new server; measure again |
| Q8 | Does an early review (P1) change the verdict, given that 1.6 % of pairs flip on the same key? | P1 safety | Replay v2b with D0 receipts |
| Q9 | Can G1/G3 judge first lifts from a stub? Only 1 of 15 credits was checkable. | S6 coverage | A fixture with a stub-to-lift card |
| Q10 | Does the dedicated server shorten this wave at all? fleet L9 says no while the path is serial. | Hardware plan | Re-run the replay after ranks 1–7 |
