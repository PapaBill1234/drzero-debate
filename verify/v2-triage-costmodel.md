# Verify batch v2-triage-costmodel (D10, D12, run1 T4, T7, T8, H2-H6, open questions 3, 4, 5, 7)

Read only. Code: engine main `design/parity-v2/parityctl` (HEAD 397f8ac4 tree). Data: `/data/parity-v2` on 2026-11-26. This file: about 3.5k tokens.

| Item | Verdict | Defect today (file:line) | Evidence quality | Risk | Scope if BUILD | Effort | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D10 (all) | BUILD-SMALL | `triage.py:459-460` one fixed branch_inversion hint; `triage.py:250` moved_calls keeps register tokens; `triage.py:754-768` groups only path pairs | measured (counts), plausible (gain) | None for MATCH, proof or safety checks. Triage is advice only. | 3 parts below (H6, H2a, group key). About 40 lines in `triage.py`, about 50 lines in `tests/test_triage.py` | S | D09 (agent B edits `triage.py`): land after it. Then re-run triage (D09/H1). |
| H6 branch_inversion hint per tail direction | BUILD-SMALL (part of D10) | `triage.py:459-460` | measured: v2b triage 26/26 BI items carry `detail.tail`, 12 in the top 50 (run1 file: 33/47, 3 in top 50). Fix effect: plausible, n=8 labels | None. No ease change. | `hint()`: 3 texts by `d.get('tail')` (dup tail, shared tail, none + split-test fallback). 3 tests. | S | D09 |
| H2 instruction_order | BUILD-SMALL (callee filter only); LATER (classify_order, INLINE-GAP, STALE) | `triage.py:250` (no callee filter), `relevant()` `triage.py:418-420` reads it | measured: pseudo tokens are rare (run1 file 2 items with `r8` first; v2b 1 of 15, not first). Mined: instruction_order 0 exact / 9 cases. INLINE-GAP = guess ❓ | Low. Filter can lower conf of an item whose only moved call is a register (intended). | `_callee()` filter: drop registers and `qword ptr [reg + off]`, keep `import:X`. 1 test. | S | D09 |
| D10 cross-exe group key | BUILD-SMALL (part of D10) | `triage.py:754-768` (path_pair only); `mkcard.py:52-55` dedups name+score only at card time | measured: v2b 24 functions in 2+ exes = 81 of 152 items | Low. Group only when function, cause, score and changed count are equal; skip items with `cross_exe_split`. | Extend `group_fixes()` with key (function, cause, score, changed) -> `same_fix_as`. 1 test. | S | D09 |
| H3 inline_dir | LATER | `triage.py:276` cause by call counts only | guess: "28 of 40 wrong" not checked by the judge. Mined: 22 call-fix labels, only 1 predicted missing_call, 7 predicted tail_merge (cause choice is the gap, not direction) | Medium (needs lift-source call graph; wrong `noinline` advice changes all exes) | - | M | D09 re-run on LobbyDaemon |
| H4 data_ref families | DONE | `triage.py:119-155, 549-580, 754-768`; `insn_diff.py:230-272` (e8dedf77, 348dc407) | measured | - | - | - | - |
| H5 mined cases + hint gate | DONE | `triage.py:876-1140` (cf38d4b7); `triage-calibration.json` 173 cases, 57 labelled | measured | - | - | - | - |
| D12 / T4 one unit (beq) | BUILD-SMALL | `feedback.py:155` `_num` drops dict tokens; `feedback.py:400-413` never reads meter `beq`; `feedback.py:569` fits estimate/pred; `plan_cards.py:89-92` 1.35 and 320k | measured: pooled beq/pred = 16.5 (n=8 gap cards; range 9.3-36.0); 5 of 8 cards over 3M beq | Planner only. Every current draft (171k-324k model tokens) is over 3M at x16.5: plan splits more. Land both halves in one change. | `from_ledger_record`: meter author card -> `author_tokens = beq`, src `meter`, skip superseded; token factor from meter pairs only. `plan_cards.py:89-92`: fallback 16.5, `CARD_CAP` = author `card_cap` 3,000,000, `CARD_MIN` about 1.4M. About 40 lines + 3 tests. | S | D02, D11 (both edit `plan_cards.py`) |
| D12 print fitted p_new (Q7) | DONE | `plan_cards.py:940-941, 1007-1014`; `rerank --write` rewrites drafts (`:1292`) | measured (code) | - | - | - | - |
| D12 / T8 CLASSES re-fit | DONE (shape_cc); REJECT (shape_imm 0.15, P_OUT_OF_CARD 0.6, P3_imm exclude regex) | `repair.py:105-141` already has shape_cc 0.6 and the n>=5 rule | measured: shape_cc 16/22 symbols later accept; shape_imm 0/2 symbols; signature 3/5 (9 of 14 rejects from engine cards) | P3_imm regex in `ltcg_layout` would propose excludes for real constant bugs. | - | - | - |
| D12 / T7 review_item + carry | DONE | `repair.py:636-651` (ledger median, fallback 8000), `repair.py:662-686` (untouched = 0); `cardrun.py:1152-1155, 1193, 1317` carry + global_carry | measured: median 7,766 (n=335); 10 carried events since 15:38 | - | - | - | - |
| Q3 review_item rule | DONE | `repair.py:641` median rule | measured | - | - | - | - |
| Q4 match_value units | LATER | `exclude_policy.json:4` 50k; cost mixes estimate (`per_function` 8000) and plain review tokens | measured: only 16 of 335 review events have `beq` (median 5.0k) | A value-only switch to beq (0.49-1.43M) drops the gate threshold from 0.32 to about 0.01: gate off. | - | - | D01-D03 (credit and baseline), D12 |
| Q5 order of T1 and Q1 | DONE (in work) | agent B worktree `drzero-planner` changes `gains()`, `exe_state`, scope order in one diff | measured (diff) | - | - | - | D11 |
| Q7 INLINE-GAP = PGO? | LATER | Character::* still DIFF on 6824f3d (85.6-91.3) | guess ❓. Originals: linker 10.0, only a CodeView debug entry; no PGO note in lessons or build | - | - | - | - |

## Reasons

**D10.** Two of the four families exist. `data_ref` is split into path_literal, icf_alias, data_name and ltcg_inline, with net refs and the ICF resolver fix (H4 DONE). Mined cases and the hint gate exist (H5 DONE). The open parts are cheap hint and grouping changes. Value is now lower than in run1: 145 of the 152 v2b triage items are open with an A or B proof in bns-lift `Docs/Parity/unmatchable.md`. Many B rows quote only the generic triage hint as the reason. The changes help LobbyDaemon (300 DIFF on 6824f3d) and later targets. Build them after D09, because D09 also edits `triage.py`.

**H6.** All 26 branch_inversion items in the v2b triage (`/data/parity-v2/v2batch/triage/triage-latest.json`) carry a tail direction. 12 are in the top 50. Ranks 10-14 and 18-21 are one function each in 4 exes. The plain swap hint is still calibrated "show" (precision 0.81 on 16 mined cases). So keep the swap as the no-tail text and add the two tail texts. Do not add an ease factor.

**H2.** The callee filter is correct but small. Register tokens head the list in 2 run1 items only. The order classes and the INLINE-GAP group rest on a guess. The calibration already marks instruction_order uncalibrated (0 exact of 9). At 10 cases the gate shows it as "unverified" without new code. STALE marking is covered when D09/H1 re-runs triage on main.

**H3.** No data supports the inline direction claim beyond the run1 answer. The mined labels show a different gap: call fixes get the cause tail_merge. Re-measure on a fresh LobbyDaemon triage first.

**D12 / T4.** The defect is real. `feedback.collect` gives author_tokens only from result-file estimates (170k-450k). The ledger has 11 meter events with `beq` that the reader drops. Pooled beq / planner prediction is exactly 16.5 on the 8 gap cards. Per kind: core 14.5 (n=2 ❓), channel 21.6, job 13.1. The open cards are job and chain (pooled), so the ratio is 1.26 and the rank order does not change. The gain is a planner cap in the same unit as the author `card_cap` (`author.py:153`). The factor comes from old subagent sessions without context split. Fit it from meter events only, and refit after D13 and D17.

**D12 other parts.** Q7 printing, the review median, the carry and the shape_cc value are in the code. The shape_imm and P_OUT_OF_CARD changes rest on 2 symbols and 1 item. The code rule "change only at n >= 5" is right. The proposed P3_imm exclude regex cannot tell a TLS offset from a wrong constant. Reject it.

**T7, Q3.** Done as proposed. The fallback is 8000. The ledger median is now 7,766.

**T8.** See D12 other parts.

**Q4.** Change value and cost together, in one unit, after the credit and baseline work (D01-D03). Today a value-only change switches the gate off.

**Q5.** Agent B builds both in one change (D11).

**Q7.** Still open. No PGO evidence. A cheap test: check the original PDB for split (cold) function chunks. Run it as a card experiment, not as engine work.
