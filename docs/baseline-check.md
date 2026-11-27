# Baseline check: run1 T2 ("re-pin the proof baseline")

Date: 2026-11-26. Read only. No build ran. No baseline changed.

## Answer

| Question | Answer |
| --- | --- |
| Which exe? | LobbyDaemon. |
| Is the drift real? | Yes. The baseline file at d5b3dc3 had 645 MATCH (825 rows). Card proofs on base d5b3dc3 with no card source change already show 673 (proof-gap01 candidate_match 673, paired 837). `git log bc01acc..d5b3dc3 -- src` has 0 commits. So the +28 came from the checker/tools, not from card source. |
| Is it fixed now? | Yes, for the baseline file. Accept commit 0c8f3e9 (2026-11-25 17:19, "accept gap-int-2 baseline (LobbyDaemon 674 MATCH)") re-pinned it to a real build of the landed tree. Every later accept writes the real build. All proofs from gap-04b on judge against 674 or 677. |
| Current baseline | 8af60dd (HEAD for Docs/Parity/baseline): LobbyDaemon 1452 rows, 1024 MATCH, 127 EXCLUDED, 301 DIFF. 1024 + 127 = 1151. This agrees with the fresh build yddpzgm7 at ef90562 (1151 MATCH, 1451 paired). There are 0 `src` commits after 8af60dd. |
| Is the ledger fixed? | No. The ledger still holds the drifted credit. |

## Affected credits and numbers

| Item | Source | Recorded | Real (vs 673/674) |
| --- | --- | --- | --- |
| gap-int-2 credit row | ledger/events.jsonl seq 2, `ref_match 29` (auto 7 + review_accept 22), state landed | +29 | about +1 (landed tree = 674; fresh base = 673) |
| gap-01 proof | gap/proof-gap01.json | 645 → 673, new 28 | 0 (no source change on d5b3dc3) |
| gap-02 proof | gap/g02/proof-gap02.json | 645 → 675, new 30 | about +2 |
| gap-03 proof | gap/proof-gap03.json | 645 → 676, new 31 | about +3 |
| gap-04 proof (first) | gap/proof-gap04.json | 645 → 675, new 30 | about +2. The ledger credit for gap-04 (13, pending) uses 674. It is not affected. |
| gap-05 proof | gap/proof-gap05.json | 645 → 674, new 29 | about +1. The ledger credit for gap-05 is 0. It is not affected. |
| merge proofs | gap/int/proof-merge-035e323.json and *-vs-main / *-vs-merge | 645 → 678, new 33 | about +5 before the reverts; the landed tree gives +1 |
| Planner calibration | feedback.py ref_real (pooled 0.645 in the proposals) | uses the 29 | too high. Re-compute after the ledger fix. |

Proofs on base 0c8f3e9 or later (gap-04b/04c, gap-06..26, gap-15, misc a/b) use the re-pinned 674 or 677. They are not affected by this drift. Their overlap (double count) is a separate issue (run1 Q3).

## Open points

- ❓ 887c258 ("accept tools-pdbq-pdbcls-funcdiff-imm") moved LobbyDaemon from 674 to 677 with a tools change. This is a small drift of the same type (+3). gap-26 judges against 677. I did not check if a card got credit for these 3.
- ❓ 8af60dd has 1452 rows. The ef90562 build has 1451 paired. I did not check the 1 extra row.
- Fix that is still needed: correct the gap-int-2 credit row (29 → about 1) through a new ledger event. Do not edit history. Then re-run the feedback calibration. This is in the files that eng-drzero-ab owns (integrate.py, feedback.py, ledger.py). I did not change them.
- To stop a new drift: a checker or tools change must re-pin the baseline in the same accept (run1 L1, checker digest).

## Sources

- bns-lift: `git show <rev>:Docs/Parity/baseline/LobbyDaemon.json` for d5b3dc3, bc01acc, 0c8f3e9, 887c258, e0e8fff, 8af60dd.
- /data/parity-v2/gap/proof-gap*.json, gap/g02/proof-gap02.json, gap/int/proof-*.json (`exes.LobbyDaemon`).
- /data/parity-v2/ledger/events.jsonl (kind = credit).
- /data/parity-v2/drzero/all-proposals.txt line 958 (judge notes: main-build-hjwtkCdg at d5b3dc3 = 673 MATCH, 837 paired).
