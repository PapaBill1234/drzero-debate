# Dr. Zero build plan (after 10 verifiers)

Date: 2026-11-26. Source: `/data/parity-v2/drzero/verify/v1..v10`. Master list: `all-proposals.md`.

## 1. Status of BUILD items (owner approved "build the BUILD ones")

| Item | Agent / branch | Status |
| --- | --- | --- |
| D11, D09, D14, D13 | B / eng-drzero-planner | merged 8c7d72fe (D13 not wired into `author.py`) |
| D33, D01-D05 | A / eng-drzero-ab | merged (on main via cfe6ecbb; touched tests OK) |
| D30, D32 | C / eng-drzero-ops | merged 2d072424 |
| D19 + D20, D37 | D / eng-drzero-speed | merged 799cd0cc |
| D22 | w2-gateproof | building (shadow mode first) |
| M01 file-level reuse stamp (v10) | w2-gateproof | building |

## 2. BUILD-SMALL (owner OK 2026-11-26)

| Wave | Agent / branch | Items | Status |
| --- | --- | --- | --- |
| 1 | E / eng-drzero-triage | D10, D12, M12, M13, run1-02, D39 | merged 216fe079 (M12 mkcard check off until triage reruns on main) |
| 1 | F / eng-drzero-canary | D08, run1-29, Q9 | merged a19738a5 (+ landq fix 0a029f7f) |
| 1 | G / eng-drzero-hygiene | D34-D, D36, M26, M10, M11, M14, D29, M23, M24, M25, M29 | merged d290731e (D29 report only) |
| 2 | w2-gateproof (opus) | M01, D20 rest, M03, M05, D21A, D22, base_cache env override | building |
| 2 | w2-strict | M06, D06a, D07a, D35-B | building |
| 2 | w2-cache | M02, M04 (target.py) | merged f4c125b4. Skipped: D28 (needs live byte audit build2/build3), M22 (gate_fast.sh), OUT_ROOT (inside D04) |
| 2 | w2-ledger | D15, M16-M20, gap-int-2, D38, D41 | building |
| 2 | w2-sync | sync.sh merge guard (new), D34-C, M15, M26 rest | building |
| 2 | w2-author | D13 wiring, D17, D18, M07, M08, M09, run2-21 | building |
| 2 | w2-misc | slotq rc 5 class, triage default output, landq backup-retry, opstatus review_seconds | building |
| lift | operator | M27 (LD define), M28 (land b684588 after a fresh check) | sent to operator |

### Item groups by file

| Group (file) | Items |
| --- | --- |
| Gate and proof (`proof.py`, `cardrun.py`) | D20 (no "gate.rc before record"), M03, M05, D21 part A |
| Build cache (`buildcache.py`, `target.py`, `funcdiff_cached.py`) | M02, M04, D28 (after byte audit per host) |
| Author and cards (`author.py`, `author_packet.py`, `author-prompt.md`) | D13 wiring, D17, D18 (keep Hex-Rays cache), M07, M08, M09, run2-21 |
| Triage and planner (`triage.py`, `mkcard.py`) | D10, D12, M12, M13, run1-02 |
| Ledger (`ledger.py`) | D15 (tries field), M16-M20, gap-int-2 credit fix (29 → about 1) |
| Ops (`sched.py`, `sync.sh`, `meter.py`, `score.py`, `events.py`) | D29 (no EXIT_INPUT change, no warm-host sort), D34-C, D34-D, D35-B, D36, D38, D41, M10, M11, M14, M15, M21-M29 |
| Canary | D08 (real set), run1-29 (kill-lander mode), Q9 stub G1 check |
| Strict compare | M06 (EH compare), D06a, D07a |
| Docs | D39 |

## 3. LATER and REJECT

See `/data/parity-v2/drzero/verify/v*.md`. REJECT: D16, D23, D27, D06b (P6/P8), D06d, T8 rest, run2-09, run2-26, M61-M68.

## 4. Corrections to the master list (v10)

| Row | Wrong part |
| --- | --- |
| D12 | 16.5 / 3M are proposed values, not stale ones. |
| D02 | The 0.31 figure was not recomputed. |
| D17-D20 | Gains are overstated. |
| D21 | "0 of 136 failed" does not prove the check ran. |
| D27 | Docs-free key is unsafe unless the compare re-runs. |
| D28 | Judge rerun peak is 7, not 4. |
| D30 | 2860 s timeout has no p99 basis. |
| D04 | The two "digests" are commit SHAs. |

## 5. Wave 3 queue (from wave 2 reports)

| Item | File | Note |
| --- | --- | --- |
| M04 binding: add `target.config_digest()` to `checker_digest()` | `proof.py` | After w2-gateproof merges. Digest bump: batch with M22. |
| M22: `--setenv CMAKE_BUILD_PARALLEL_LEVEL` in bwrap | `gate_fast.sh` | Digest bump |
| funcdiff_scope pickle name: same key formula as `funcdiff_cached.py` | `funcdiff_scope.py:192` | Or accept one cold run |
| D28 byte audit build2 + build3, then D28 | `cardrun.py`, `slotq` | Needs live hosts |
| 2 failures on main since 2d072424: `test_gate_fast.GcTail...frees_slot_lock_and_stdio`, `test_no_code_folder_data` (canary result files, gate_full.sh build-cache) | tests / canary.py | Fix or park before next gate |
| `test_no_code_folder_data` now also flags `triage.py:1343` (`HERE / 'triage-calibration.json'`, tracked-file fallback read from w2-misc cecadad8). Add a reviewed ALLOW entry or drop the fallback. Full suite 2026-11-26 on ddfc9150: 2036 tests, 1 failure (this test); GcTail passed. | `triage.py` | Same test as the known failure |
