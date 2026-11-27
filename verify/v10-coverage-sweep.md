# v10-coverage-sweep: ideas that the master list missed

Date: 2026-11-26. Read only. No repo file changed. Engine parityctl HEAD 28a87a4b, bns-lift main 3c8e78c.
Method: 4 agents read all 86 raw entries (question, answer, evidence, proposal, judge notes) and both REPORT.md files. They found about 560 ideas. About 330 map to D01-D41 or to a dropped entry. About 230 have no home or only a partial home. 4 more agents checked the code and data for the 77 ideas with value medium or higher. The rest are in section C.
Size of this file: about 6k tokens.

## A. Verdict table (ideas with no home in D01-D41)

| Item | Verdict | Defect today (file:line) | Evidence quality | Risk | Scope if BUILD | Effort | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M01 Stale-tool reuse at file level (run2-34b) | BUILD (inside D04) | cardrun.py:725-731 build_ok, :766-775 strict_all, :1057-1069 proof_current; proof.py:151-155 strict_stale checks cfg only | measured (code) | high today: checker change + --reset reuses old outputs (work dirs stay, :1821) | check the D04 producer stamp at the 3 reuse sites; test: checker change forces rebuild | M | D04 (agent A) |
| M02 fd_key and pickle key miss wrapper + sys.version (run1-37d, run2-06) | BUILD-SMALL | buildcache.py:778-791; funcdiff_cached.py:40-42 | measured (1,148 fd hits vs 266 misses) | stale fd hit moves baseline count and lost_check; auto credit safe (strict.py:50 imports funcdiff) | add fsha(wrapper), sys.version, sha(__file__); about 8 lines + 30-line test | S | coordinate D04 |
| M03 Proof R8 ignores gate.rc; no sha pin of original exe/PDB; pin_digest ignores file mode (run2-29h) | BUILD-SMALL (inside D05) | proof.py R8; proof.py:88-100; targets/server.json | measured (mode 644->755 change was invisible) | low | R8 needs gate.rc==0; sha256 pins; hash mode; about 25 lines | S | D05, D04 |
| M04 Declared config not in checker digest (run1-37e) | BUILD-SMALL (inside D04) | proof.py:81-86; target.py:66-67,343 patch EXES/CONFIG from unhashed targets/server.json | measured | a dropped binary drops lost_match silently | hash canonical JSON of gates/compare/binaries; about 15 lines + test | S | D04 |
| M05 Unstamped --strict-base accepted (run2-12c/d, run2-02d) | BUILD-SMALL (inside D04) | cardrun.py:1014-1016; done file :1029 has no digest | measured (0 of 47 states use it) | low now; live once D22 seeds | write tool_digest into done; StepFail on mismatch; D22 seeds only on equal digest | S | D04, then D22 |
| M06 EH tables not compared (run1-39e) | BUILD-SMALL | funcdiff/strict have no .pdata/.xdata check | measured: 51 MATCH functions in 5 exes differ in EH handler or maxState (e.g. ThreadManager::entry lost __try) | auto credit blocked (strict full=False); review and ref_match can count them | `eh` field in strict.py rows; mismatch -> review item; do not change funcdiff status | S-M | D09 EH reader; 1 digest bump |
| M07 Packet off for all v2b runs; prompt claims a packet (run2-21a) | BUILD-SMALL | author-prompt.md:32; author.py:1766,1817 | measured (8/8 opts.packet False) | conflicts with D18 deny list (no pseudocode path) | conditional prompt line; refuse --no-packet for >3 rows unless forced; about 15 lines | S | M08 first; before D18 |
| M08 Token estimate 2.5 B/token, real 1.65 (run1-26b) | BUILD-SMALL | author_packet.py:58-60; packet.py | measured (8 prompts, 34 % low) | 60k inline packet is about 91k real; can trip the 100k split at once | len*3//5; about 4 lines; fixture test ±10 % | S | before M07, D13 |
| M09 Per-id base->now feedback each round (run1-36b, run2-26f) | BUILD-SMALL | author.py:1533-1549 lists lost names only | measured (scd-01b lost Execute/ExecuteW in round 2) | none (feedback only) | compare_gate (:824) adds id_status table; about 40 lines; scd-01b fixture | S | none |
| M10 Meter loses output tokens on split/cap sessions (run2-41d, run1-09c/d) | BUILD-SMALL (extends D41) | meter.py has no message_delta branch; author.meter_raw :436 | measured (seq 420: 246 vs 18,504; beq 199,989 low on 2 rows) | cost numbers only | read stream_event/message_delta, max per message id; about 25 lines; seq-420 test | S | before D38/D39 numbers |
| M11 Compaction calls not metered (run1-12e, run2-40b) | BUILD-SMALL (inside D38) | meter.py: no compaction branch | measured (5 lead compactions) | none | estimated row per compact_boundary; about 15 lines | S | D38 |
| M12 Stale triage input for mkcard (run1-21h, 31d, 36a, 39b) | BUILD-SMALL (extends D09/D14) | mkcard.py:57 reads v2batch triage at 6824f3d; 7 of 152 items MATCH now | measured ("18 of 116" not reproduced) | low | refuse when triage head != card base; drop items MATCH in base; about 20 lines | S | D09, D14 (agent B) |
| M13 ease() uses raw confidence, not calibrated precision (run1-02c/d) | BUILD-SMALL | triage.py:519-528 (gate exists :1100) | measured (tail_merge 0/18 exact) | ranking only | min(conf, precision) for calibrated causes; about 8 lines | S | none |
| M14 sched backup_pending never retried (run1-33c) | BUILD-SMALL (extends D33) | sched.py:519-525 sets it; nothing reads it | measured (code) | none for MATCH; live in cardrun land mode and the D32 driver | D33 retry also reads sched flags; about 15 lines + test | S | D33 (agent A), D32 |
| M15 sync.sh off-main exit 0, no git timeout, exit 1 means 2 things (run1-33b/f/g) | BUILD-SMALL (extends D33) | backup/sync.sh:82-85, :96-104, :74/76/89 | measured (code) | D33 escalation on exit 1 would misfire | exit 6 off main; timeout 300 on git (exit 5); own index.lock code; about 8 lines | S | D33 |
| M16 Ledger misses failed steps, buildonce fails, queue wait; report counts author.* as build s (run2-04b/c/d, 18c) | BUILD-SMALL (extends D37) | cardrun.py:640; buildonce.py:298-300; ledger.py:742-743 (73 events, 8,422 s); slotq.py:337-343 | measured (10 fails, 6,019 s) | none | 4 hunks, about 35 lines + 3 tests | S | D37 |
| M17 Missing ledger credit rows gap-07..26; gap-int-2 at=0 (run1-32e, run2-28e) | BUILD-SMALL | ledger.py:879-903 BACKFILL_LEDGERS lacks slot4 ledgers; :940-962 | measured (union 243 vs 276 claimed) | double count if run before D01 | add ledgers; fix at=0 on read; about 20 lines + test | S | after D01 |
| M18 candidate_match counts EXCLUDED rows (run2-28f) | BUILD-SMALL (fold into D03) | proof.py:193-194 | measured (1151 vs 1024) | display only; digest bump | use is_match with excl; about 6 lines | S | D03, D04 |
| M19 rerank does not fail without `credited` (run1-17d) | BUILD-SMALL (inside D02) | feedback.py:174-182 | measured (code) | low | raise/flag in calibrate and rerank; about 10 lines | S | D02 |
| M20 Unmetered credit flag (run2-10e/f, 28i, 24f) | BUILD-SMALL | ledger.py:405-411 | measured (11 of 15 v2b MATCH from cards with 0 author events) | low | `unmetered` flag, per_match marked partial; about 15 lines | S | D41, D38, D39 |
| M21 DIFF->DIFF score drops not reported (run1-36c, run2-35e) | BUILD-SMALL (report only) | no check exists | measured (31 drops >5 points; POD 94.4->79.8/77.2) | a blocking guard stops valid header edits | non-blocking diff_regress list in land result/opstatus; not in proof.py; about 30 lines | S | D09 input |
| M22 cmake --build has no -j: 10 ninja jobs per slot (run2-08b) | BUILD-SMALL | bns-lift tools/gate.sh:13; gate_fast.sh:57 --clearenv | plausible | 1 checker-digest bump | `--setenv CMAKE_BUILD_PARALLEL_LEVEL "$cl_jobs"`; 1 line | S | batch with D19-D21 |
| M23 Slot lock has no owner record (run2-38e) | BUILD-SMALL | remote_build.py:234-242 truncates, no owner | measured (13:10:04, no trace) | none | write {pid, argv, at} after LOCK_EX; about 8 lines | S | none |
| M24 rc 3 "transport" is a setup error (run2-32j, 01e) | BUILD-SMALL (inside D29) | remote_build.py:427 | measured (4 rows, g17, fixed e878667f) | none | exit 5 "setup", mark host down with log tail; about 10 lines | S | D29; better than D29's EXIT_INPUT 2 |
| M25 Tests write the real base_cache (run2-12e) | BUILD-SMALL | tests/test_sched.py:76-85 -> cardrun.py:199,204 | measured (2,478 of 2,508 dirs, 94 MB) | none | tmp base_cache; guard test; clean old dirs | S | none |
| M26 Unbacked pinned inputs; linked-* leak; pilot gate in worktrees (run1-07d/f/g) | BUILD-SMALL (extends D36) | .gitignore:7,10,11; sync.sh:45 excludes parityctl/ | measured (31 dirs 110M; reference log only in 2 eng-wt copies) | input loss | copy pins + log to backup/inputs with sha256; keep newest N linked-*; about 30 lines | S | D36 |
| M27 Lift fix: LD path define for RefCntObject.h (run1-18d, 39d) | BUILD-SMALL (lift card) | SessionBuffer.cpp:197-205; RefCntObject.cpp:16; PacketUtil.cpp:18 | measured (4 LD items >=85); "+12" guess | gate checks 5 exes | one per-exe define (StlMemory.h:17 pattern) | S | none |
| M28 SetInvalidInfo +3 MATCH on unlanded branch (run1-11c) | BUILD-SMALL (lead card) | engine rule DONE (proof.py:141-196); b684588 only on triage-fix branch | measured (DIFF 96.3 in CG/SCD/POD on main) | re-check on main | land b684588 after a fresh check | S | none |
| M29 HANDOFF clock labels false (run2-18e, 46h) | BUILD-SMALL | HANDOFF.md:62 (18:10 vs 15:05:42Z) | measured | none | AGENT-RULES line + date -u helper; about 10 lines | S | D32 |
| M30 lone_constant flag on non-constant items (run1-06d) | BUILD-SMALL (low) | triage.py:355 | measured (14 items) | report counts only | 3 lines | S | next triage edit |
| M31 filter_card ID_ROW matches 0 rows (run1-26c) | BUILD-SMALL (extends D13) | author_packet.py:286 | measured (0 of 10 cards) | low | also filter cardexe.SCOPE_ROW; about 15 lines | S | D13 |
| M32 D12 factor + cap must land together (run1-25d) | BUILD-SMALL (inside D12) | plan_cards.py:89-92, :365-368 | measured | factor alone drops chain cards | one commit | S | D02 |
| M33 slotq run-time prefix, not COMMANDS (run2-22a) | constraint for D28 | cardrun.py:807-811 tool_digest hashes commands | measured | editing COMMANDS rebuilds every base | run-time prefix in run_cmd :669; about 6 lines | S | D28 |
| M34 Background gc must close fds and detach (run2-13b) | constraint for D19 | remote_build.py:420-421 fd 9 slot flock; queue_build.py:910 PIPE | measured | bare `&` holds the remote slot | setsid -f, </dev/null, 9>&-, own flock + timeout | S | D19 |
| M35 Buildonce hit must re-run compare (run2-25c) | LATER (hard condition of D27) | none today (key includes Docs) | measured | real once D27 drops Docs | — | — | D27 |
| M36 Cross-host byte check (run1-37h, 38f, 22d) | LATER (gate for D28) | partly done: hostname pinned gate_fast.sh:51, compare :1016 | measured | none today (card builds local) | — | S | D28 |
| M37 Toolchain probe path+size only (run2-23e, 25d) | LATER / inside D05 if its scope has the run2-23 memo | remote_build.py:1102; buildcache.py:83-103 | plausible | low | — | S | D05 |
| M38 G1/G3 false positives and coverage (run2-47d/f) | LATER (fold into D07) | edit_guards.py only from pilot.py:389-392 | plausible | none before D07 | — | — | D07 |
| M39 gc never deletes .tmp- dirs (run2-33d) | LATER (fold into D19) | buildcache.py:892-899 | measured (0 such dirs now) | none | 6 lines | S | D19 |
| M40 Move clones/store off sdb (run2-08d, 13c) | LATER | sdb busy 36x sda; both QEMU disks; /data 92 % full | measured busy; HDD not proven | load onto root fs | — | — | D37 A/B build first |
| M41 Late REF MATCH credit to unlock cards (run1-34c) | LATER | no rule | plausible | double count | — | — | D11, D01, T2 re-pin |
| M42 Credit written before accept commit (run2-28h) | LATER | integrate.py:289 before :296 | measured (0 states hit) | low | — | — | D03 verify chain |
| M43 slotq child.wait no limit; SIGTERM counted as killed (run1-22d, 19d) | LATER | slotq.py:1173,1230; :864-865 | measured | low | — | — | D28, D30 |
| M44 Dirty-tree checker digest (run1-37g) | LATER (add to D04) | proof.py:80-86 | measured (0 ledger hits) | low | — | — | D04 |
| M45 ctx_split 160k in runcard.sh (run2-21e) | LATER (input to D17) | runcard.sh; 5 of 8 cards | measured | 8k margin to compaction | — | — | D17 |
| M46 Triage hint details: callee noise, SPLIT_CAUSES, STUB, classes (run1-21/28/31) | LATER (fold into D10) | triage.py:250 (61 noisy entries), :80 | measured (noise) | hint text only | — | — | D10 |
| M47 Repair numbers: cmd_feedback draft rewrite (run1-04b) | LATER | plan_cards.py:1262-1264 | measured | planner off the v2b path | — | — | D12 |
| M48 Stop-list park source (run2-15c) | LATER (extends D09) | lessons.md stop lists not a park source | measured | none | — | — | D09 |
| M49 landed_on_main no credit; recover failed-after-push (run1-14c/d) | DONE | landq.py:703-709; sched.py:511-517 | measured | — | — | — | rest is M17 |
| M50 Review digest = whole review.py (run1-08c) | DONE | review.py:135-148 (REVIEW_VERSION), adopt_legacy | measured | — | — | — | — |
| M51 Accept after review reject (run2-28g) | DONE | integrate.py:87-116 | measured | — | — | — | — |
| M52 Operator busy-park on recover (run1-29b-e; REPORT O8) | DONE (canary kill-lander LATER) | operator_run.py:853-879; landq.py:639,678 | measured | — | — | — | — |
| M53 Double backup per land (run1-24d, 14b) | DONE | landq.py:793-794, :945-951 | measured | — | — | — | — |
| M54 Git env, landq timeouts, base flock (run1-22b/c/e) | DONE | landq.py:360-377; cardrun.py:1022 | measured | — | — | — | — |
| M55 Crash rc<0 and crash_waits resets (run1-10b/c) | DONE | sched.py:101,423,443-447 | measured | — | — | — | — |
| M56 Cut-file JSON readers (run1-20c) | DONE | buildonce.py:274; queue_build.py:906 | measured | — | — | — | — |
| M57 CMake comment rule; include_removed; early R1; R7 in precheck (run1-13b-e) | DONE | cardrun.py:915-939, :405-485, :941 | measured | — | — | — | — |
| M58 POD exe routing of packet/REF build (run2-27j, run1-27e) | DONE | R3 21bb1180, 8a5e2f65 | measured | — | — | — | — |
| M59 no_gain_text reach (run2-27i); review_item from ledger, carry cost 0 (run1-01a/b/d) | DONE | author.py:1586-1594; repair.py:641,662 | measured | — | — | — | — |
| M60 Auto re-check "moved after proof base" (run2-15e); no_gain rebuild loop (run2-19b) | DONE | author.py:162,:1339; :1493-1508 | measured | — | — | — | — |
| M61 2-draw carry rule (run2-17c) | REJECT | ledger.py:505-521; receipts.py:365-385 already refuse carry on conflict | measured (3 flips, all old digests) | adds 1 draw per accept | — | — | — |
| M62 Revoke gap-int-2 / gap-15 accepts (run2-29j, 42e) | REJECT revoke; LATER re-audit | layout hole closed f2920f3; 0 errors over 6,002 members | measured | revoking real MATCH | — | — | D06 replay |
| M63 ICF/short-body refusal in funcdiff (run1-39f) | REJECT | — | guess | kills real getters and empty bodies | — | — | D09 class label |
| M64 resym .h byte-44399 "correctness bug" (run2-45h) | REJECT (claim) | type order only; resymc not deterministic | measured (3 dumps) | none | sha key stays optional in D21 | — | D21 |
| M65 Hardlink restore rm -f (run2-33e) | REJECT now; condition for D20 | restore uses copyfile buildcache.py:389,644,748 | measured | real only with hardlink restore | — | — | D20 |
| M66 Drop K from review bundle (run2-42c); ltcg_layout regex (run1-16c) | REJECT | review.py:507-521; 0 of 6 P3_imm match | plausible / measured | more false rejects; parks real imm defects | — | — | review canary |
| M67 Empty-key backfill events (run1-15b); pdb_layout pool cap (run2-20e); per-exe BloodLib share (run2-30e); git gc clones (run2-11f); XDG / rc 2 bugs (run2-26e, 07f); stale .down alarm (run2-11d); Meter last-12 (run2-27c) | REJECT | premise wrong, done, or no effect (see agent notes) | measured | — | — | — | — |
| M68 Lost SendResponseChargeRequestStopFail (run1-32d) | REJECT as engine bug; lift item | never MATCH on main (DIFF 84.1 since 588f468) | measured | none | — | — | D09 band |
| T2 Baseline re-pin 645 vs 673 (run1-34b, REPORT T2) | note only | — | — | — | — | — | agent B; M41 and M17 (wave 1) depend on it |

## B. Judge notes: master list kept the wrong part

| Row | What the master list keeps | What the judge or data says |
| --- | --- | --- |
| D12 | "stale ❓: MEASURED_FACTOR is 1.35 and CARD_CAP is 320,000 now, not 16.5 and 3,000,000" | Misread. run1-25 gives 1.35/320k as today and proposes 16.5/3M (author card_cap 3M, author.py:153). Verified. The unchecked CARD_MIN 1.4M is missing. |
| D12 | "up to 0.90M of 1.75M review tokens" (no ❓) | Judge: 123 final-call-only events, not 99; subset unclear (895k of 1.54M). |
| D12 | "Re-fit P_OUT_OF_CARD 0.1 to 0.6" | Judge: rests on about 1 item; a later accept can come from an engine change, not the repair. |
| D02 | "It would be about 0.31" (row and Top 10, no ❓) | Judge did not recompute 0.311 or 0.427. Also depends on T2 re-pin. |
| D06 | "2-draw accept rule" with no caveat | Judge (run2-17): a split counted as reject can lose real MATCH. Carry already refuses conflicts (M61). |
| D17 | "25-30 % of beq", Gain High | Judge run1-12: only the 14 % split part is plausible; run2-27: counterfactuals ❓, gain low. |
| D18 | "About 11-14k tokens per MATCH" | Judge run2-03: miss bins wrong; char split and cap simulation not verified. Also conflicts with M07 (packet off). |
| D19 | Gain High; Top 10 "922 s and 618 s stalls" | Judge run2-13/36: steady gain about 2 s; stall may be bwrap teardown or wineserver. |
| D20 | Gain High | Judge run2-33: gain low; 107 s and cold-read figures not verified. |
| D21 | "about 855 s per wave"; "0 of 136 gates ever failed there" | Judge run2-45: option (c) competes with ninja for 8 cores. run2-29: 70 gates ran no layout check, so "0 failed" does not prove the check ran. |
| D22 | parallel base_build fallback | Judge run2-02: CPU contention not checked. Missing guard: seed only on equal tool_digest (M05). |
| D26 | "Run funcdiff per exe in parallel" | run2-39 says prefetch (buildcache.py:807-842) may already do it ❓. Judge run2-14: --first drops the off-target regression signal. |
| D27 | "Gain is not given in seconds"; Docs-free key | run2-25 gives 320-924 s ❓. Judge: Docs-free key is safe only if the compare re-runs (M35). |
| D28 | "v2b peaked at 4 of 18 slots" | Judge run2-39 rerun: peak 7. run2-39 also: critical-path-first priority gains 0 s. |
| D30 | `child.wait(timeout=2860)` | Judge run1-19: T must come from p99 build time; ServerAlive works only in the mux master. run2-38: do not replace cool-down with a probe. |
| D16 | per-item tool-call budget of 8 | run2-41 judge rejects a per-function cap: N=8 cuts 4 of 6 MATCH; MATCH functions use a median of 16 calls. |
| D10 | "EASE weights do not change" | run1-28 and run1-31 propose ease per class. Decide before D10. |
| D04 | "digests `d0f0a78e` and `da7e7c9d`" | Judge run1-37: these are commit SHAs, not digests. |
| run2-21 | whole entry dropped for its denominator | Judge verified the packet finding as useful (M07). |
| run1-29 | dropped as done (quota.check only) | Operator busy-park part was open in the entry; now verified DONE (M52). |

## C. Ideas not checked in code (low value or detail of a D row)

These are mapped to the D row whose builder must read the source entry. Verdict for all: LATER ❓ (not verified).

| D row | Source ideas to read during the build |
| --- | --- |
| D03 | run2-28c (report only landed credits with proof_path), 28d, 46d (HANDOFF.md:52 attribution wrong: ef90562 made pod-01 +4) |
| D05 | run2-29g/i (gate_fast fails on missing summary; 5 tests), 23f/g (per-wave audit rebuild, fake-HOME test) |
| D06 | run1-01e (6 flips on equal key), run2-42d (P7 branch rule), 42g (P6 rsi trap) |
| D07 | run2-47e (bundle holds R9 finding), 47g (replay cache), 47h (WaitQueueList fixture), 47i |
| D08 | run2-42f (32 source mutants) |
| D10 | run1-21b/c/e/f/g, 28b/d/f/g/h, 31b/e, run1-11b/d |
| D13 | run1-26e/f (shards share files), 27b (one name per shard), 27d |
| D15 | run2-15b (order by root-cause yield), 44d (backlog file), 44h, 44i |
| D17 | run2-27b/d-h (table details), 27h (split commit 144 s) |
| D19/D20/D21 | run2-11a size counter, 36d selftest cache, 45b/c/d/e/g/i, 29f, 20c (A/B verdict lines), run2-33f |
| D22 | run2-43e/g (step detail, base_seeded event) |
| D23 | run2-31c: parity.sh reads the baseline after the compile, so a compare re-run settles the D23 conflict ❓ |
| D24/D25 | run1-32c (merge-train proof before credit), run2-37b/e/g |
| D26 | run2-30b/c/f/g, 08c, 14b |
| D28/D29 | run2-16b/e/f (objsync copies only vsobj ❓), 05b, 22e, 11e/h, 07b/c/e |
| D30 | run2-32b (timeout 2,860 -> 720 s), 32c, 32i, 32k |
| D31 | run1-38c |
| D33 | run1-33d/e/h, 14f |
| D34 | run1-20d/e, 35b/c/d |
| D35 | run1-30b/c/e/f |
| D37 | run2-04h (cached author build: wineboot + restore 140 of 147 s ❓, medium), 04i/j/k (land_backup 2,654 s and 5,524 s not recorded), 05d, 24b/d/e, 36e |
| D39/D41 | run2-03h (158 vs 172 MATCH), run1-09e |
| none | run1-03b/c (limit-text parity test; mostly done), 06c (refit EASE from labels), 07e/h/i, 08e, 17f (unlock term check), 20f and REPORT run1 Q9 (solver scratch files in /tmp: clean up), 24b canary invariants, 36d (ENGINE-ISSUES #9 doc fix), run2-03g (cache misses at 48-120 s gaps), 34d/e/f, 39e/h/i, 41c, 46g (pre-written cards, D32) |

## D. Reasons (short)

- M01: the biggest trust hole found. D04 changes step keys, but fresh_build finds gate.rc and reuses old outputs. D04 must check stamps at the reuse sites.
- M02: fd hits are 81 % of fd calls. A wrapper edit would reuse stale verdicts for the baseline and lost_check. Auto credit stays safe.
- M03-M05: three small holes in D05/D04 scope. The 644->755 mode change was invisible to pin_digest.
- M06: measured, not guessed. 51 MATCH functions differ in EH data. Auto credit is blocked, but review credit can count them. Show EH in strict and the review bundle.
- M07/M08: the packet was off in every v2b run and the prompt said the opposite. Fix the token estimate first, or a big inline packet trips the split.
- M09: one table per round costs no build and stops round-to-round thrash (scd-01b).
- M10/M11: beq is low on split rows. Fix before D38/D39 publish per-MATCH numbers.
- M12/M13: card input is stale; ease ignores the calibration that exists.
- M14/M15: D33 names only the landq path and only "exit non-zero". Two more silent paths exist.
- M16-M20: ledger gaps. Counting only. M17 must follow D01 or it double counts.
- M21: report only. A blocking guard would stop valid header edits.
- M22-M25: one-line or small fixes with measured cause.
- M26: a pinned input exists only in 2 worktree copies. Back it up.
- M27/M28: lift actions, not engine work. M28 is +3 MATCH on an unlanded branch.
- M33/M34/M35/M36: constraints that the D19, D27 and D28 builders must follow.
- M49-M60: done on main. Remove the "landed ❓" marks in run1 REPORT (O8, O5, O6).
- M61-M68: premise wrong, risk too high, or no effect.
