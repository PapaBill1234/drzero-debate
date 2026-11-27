# Verify batch v8-measurement (D37-D41, run2 Q4, Q5)

Date: 2026-11-26. Read only. Engine main `41c9881a`, bns-lift `3c8e78c`. Scratch scripts: `/tmp/v8m/*.py` (not kept).

| Item | Verdict | Defect today (file:line) | Evidence quality | Risk | Scope if BUILD | Effort | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D37 timing fields in `record_build` | BUILD | `ledger.py:401-402` (no t0, slot, phases, cache fields); `cardrun.py:640-645` (only `done` steps, no `review`, no t0/slot); `cardrun.py:1032` (base `full/` dir is deleted, so its phases and cache events are lost); `gate_fast.sh:74-78` (gc runs between `gate.rc` and the last line, no mark) | Measured: 31 v2b full dirs re-read (table in D37 paragraph) | None on MATCH or proof (ledger is the cost view, write is in try/except). Keep the old uid for `done` steps. | New `gate_summary(full_dir)` in cardrun.py (phases, cc/link/fd hit+miss, vs_new, gc_s = mtime(gate.log) − mtime(gate.rc), extra_s = gate_sh end − last cc event). Pass t0, slot, host, cl_jobs, parent_step (env from author.py), status, phases, cache to `record_build`. Record failed and interrupted steps (uid with `uniq()`). Add `review` to the tuple. Capture base summary before the rmtree. `summarize`: skip events with parent_step, put `review` in its own sum. No gate_fast.sh change. About 50 lines. | S | None hard. Use the `wave` source of D03. Leave `wave start/end` to D32. |
| D38 meter the lead | BUILD-SMALL | `ledger.py:94` (`TOKEN_KINDS` has no lead); `ledger.py:1261` (meter role is always `author`); `integrate.py:246-258` (no lead hook) | Measured: lead 1,775,532 nocr; per-land windows sum to the total exactly | Low. A new kind must not create a phantom card row in `summarize`. Windows must not overlap. | `ledger.record_lead(transcript, since, until, card, wave)`: `meter.measure_files` window, `kind='lead'`, raw, seconds, compactions, cold writes (> 20k cache_creation). Add `lead` to TOKEN_KINDS and a lead bucket in `report` totals. CLI `ledger.py lead`. Commits/actor and match_symbols: drop (they are D03). About 70 lines. | M | D32 (call site, transcript path), D03 (wave id) |
| D39 one MATCH rule in WAVES-VS-V2 | BUILD-SMALL (doc) | `docs/WAVES-VS-V2.md` on main has no v2b section. Section 9 is on unmerged branch `eng/v2batch-metric` (`c01c368a`), lines 217-262. It does not state the MATCH rule or the token scope. | Measured (baseline diff, lead and parent meter); parent window share ❓ | None (doc only) | Add 9.5 "Counting rule": both 58 and 15 are the same rule (Σ MATCH delta = DIFF→MATCH + new keys − lost). Split pool items from new keys. State the token scope: 84k excludes the lead, 181k includes it. Give both scopes. Tries/attempt metrics: later (need D15). About 25 lines. | S | Merge `eng/v2batch-metric` first |
| D40 `turns.py` | LATER | `author.py:1182-1186` (session totals only); no turns.py | Measured tool split; per-function attribution guess (35 % not attributable) | Low | Not now. Optional S add-on: `wall_s`, `tool_s` {tool: s} on the author event, after D28. | (M) | D28 |
| D41 meter leftovers | BUILD-SMALL | `meter.py:253-285` `Meter.feed` has no `stream_event` branch. `ledger.py:384-399` does not compare raw and tokens. `ledger.py:407` (no `closed` state). DONE: `author.py:175`, `:501-519`, `:584-591`, `:681-682` (tests `test_author.py:1434,1491`). | Measured: 2 split sessions lose 39,998 output tokens in raw | Low. Files with a result line keep the result (no change). Lead transcripts have no stream_event lines. | `meter.py` stream_event branch (message_start id, message_delta max output per id; merge into `self.msgs` by id). `record_author`: `meter_mismatch=true` when raw and tokens output differ > 2 %. No "use the larger". Then `ledger.py remeter`. `closed` credit: give to D03 owner. About 30 lines. | S | None. D38 uses the same meter. |
| Q4 review median | Answered | — | Measured | — | — | — | — |
| Q5 Edit tail | Answered | — | Measured (cause plausible ❓) | — | — | — | D28 |

## D37

The defect is real and the data is on disk. I re-read all 31 v2b `full-*` dirs (gate.phases, `clone/build-vs2010/cache-events.jsonl`, gate.rc and gate.log mtimes). The 60-1,355 s range has three causes. Cache misses are not one of them:

| Build | Seconds | gc tail | vsobj_restore | Tail after last cc event (pdb_layout, selftest) | cc miss |
| --- | ---: | ---: | ---: | ---: | ---: |
| cg-01 baea32a6 | 1,355 | 921 | 195 | 52 | 5 |
| pod-01 ef905620 | 1,015 | 617 | 172 | 63 | 13 |
| merge-03 1369f5f3 | 408 | 2 | 1 | 103 | 253 |
| lg-01b 91913409 | 248 | 2 | 3 | 171 | 8 |
| merge-02 e76b748e | 59 | 1 | 1 | 40 | 4 |

The 5 cc misses of cg-01 are the CMake probes. They are present in every build. So the data already proves D19 (gc) and part of D20 and D21. The only data that is lost is the base build data (`cardrun.py:1032` deletes the dir). No gate_fast.sh change is necessary: gc_s comes from the two mtimes, and the gate_extra tail comes from the last cc event time. If you change gate_fast.sh, do it together with D19 and D04. A change after D04 can make all base keys new once. `host` is always local until D28 lands. Do not store `overlap`: compute it at query time from t0 and seconds.

Test: `tests/test_cardrun.py`. Use a fixture full dir with gate.phases, cache-events.jsonl and gate.rc/gate.log mtimes. Check that the event has phases, cache counts, gc_s, t0 and slot. Check that a failed step writes a `status='failed'` event with a new uid. Check that a second `done` run with the same key writes no new event. `tests/test_ledger.py`: `summarize` does not add events that have parent_step.

## D38

The lead is not in the ledger. `ledger.py report` therefore shows the author-only cost (about 68k per MATCH). That number is under the 84k goal, so it is misleading. `meter.measure_files` works with `since`/`until` today. On the v2b lead transcript the land windows give pod-01 499,529, wmain-01 105,474, cg-02 308,020, merge-01 215,214, merge-02 226,133, merge-03c 360,733 and 60,429 after the last land. The sum is 1,775,532, equal to the full file. The lead output counts are real: 525 messages, 0 under 10 tokens, median 411. The transcript has 5 compactions. Do not use kind `meter` for the lead: `superseded()` keeps only the last meter event of a card. integrate.py is the wrong call site. It runs inside cardrun and does not know the lead session. The lead driver (D32) or landq knows the transcript. Give it as an argument or as env `PARITY_LEAD_TRANSCRIPT`. The operator now runs through claude-gw. Its transcript path is not checked ❓. Test: `tests/test_ledger_meter.py`. Two windows over one fixture transcript must sum to the whole. A repeated call writes nothing (uid = transcript sha + since + until). Compactions are counted. `report` shows a lead bucket and no phantom card.

## D39

The counting premise is weaker than the entry says. I re-ran the baseline diff (4 exes, git show). Manual d67687a→6824f3d: pool 207, DIFF→MATCH 55, new keys 3, lost 0, Σ 2438→2496 = +58. v2b 6824f3d→3c8e78c: pool 152, DIFF→MATCH 7, new keys 8 (RefCntObject::operator delete ×4, wmain$dtor$0 ×3, Console::Flush), lost 0, Σ 2496→2511 = +15. So 84k (4.89M/58) and 181k (2.72M/15) already use one MATCH rule. The real differences are these:

| Difference | Manual wave | v2b |
| --- | --- | --- |
| Share of MATCH from new keys | 3 of 58 (5 %) | 8 of 15 (53 %) |
| nocr per pool-item MATCH | 4.89M / 55 = 89k | 2.72M / 7 = 389k |
| Token scope | Workflow agents only (201k research + 4.55M build + 139k integrate). The parent session is not counted. | Authors 943k + lead 1.77M |
| Parent or lead, same window | 1.31M nocr in the parent session 24752902, 09:00-12:53Z, 103 messages. Part of it can be other work ❓. | 1.77M |
| Lead excluded | 84k | 943k / 15 = 63k |
| Lead included | ≤ (4.89M + 1.31M) / 58 = 107k ❓ | 181k (186.5k with reviews) |

Write this table into section 9. It is the important doc fix. Do not compare 84k with 181k. Tokens per attempt and yield per tries class need the D15 `tries` field. Add them later.

## D40

The transcripts give the time split. 61 Edits take 155 s from message end, Grep 161 calls 31.8 s, Bash 13.3 s, Read 5.2 s. This took a 40-line scratch script. Per-function attribution is fuzzy: 35 % is not attributable ❓. No consumer needs it: the per-function cap (D16) is rejected, and D15 works per item and try, not per token. The triage evidence exists at card level today. Only pod-01 landed MATCH from an author card (235.6k of 984k author nocr, 24 %). The entry says 63 % of nocr bought no MATCH. I get 76 %, without credit to the merge cards ❓. Build turns.py only when a planner rule needs per-function cost.

## D41

run1-09 changes 1 and 2 are DONE in author.py (`--include-partial-messages`, StreamMeter stream_event branch, cap check only while no result, over-cap `ok` with reason; tests exist). Commit 46f88dfb at 13:21Z. The ledger `raw` comes from `meter.py` (`author.py:436-442` → `measure_session`), and meter.py ignores stream_event lines. Measured on the 11 v2b logs:

| Session | meter.py output | message_delta output | Result line |
| --- | ---: | ---: | --- |
| lg-01 s01 | 233 | 21,965 | none (split) |
| pod-01 s01 | 246 | 18,512 | none (split) |
| 9 other sessions | equal | equal | yes |

Each context split (100k, `author.py:152`) makes one more session with no result line. So the error comes back in each wave: about 4 % of author nocr, and more in beq because output has a high weight. The mismatch flag is a cheap guard after the fix. The `closed` credit changes no total, because `report` already adds the tokens of cards with no credit. It only separates "pending" from "closed". It edits `record_credit`, which D03 also changes. Give it to the D03 owner. Test: `tests/test_meter.py`. A no-result fixture with stub assistant output and message_delta gives the delta output. A fixture with a result line is unchanged. `tests/test_ledger.py`: the flag is set when the output differs by more than 2 %.

## Q4 (review token median)

1,807 is correct. Ledger, 338 not-carried model draws: median total 7,808, median nocr (total − cached_input) 1,807, sum nocr 1,150,490. The 16 draws with v1 raw give a median nocr of 1,951. 16,894 is not a median: 6,065,566 / 359 = 16,896. It is a mean over an unknown set of 359 events, and its total is 2.5 × the ledger sum (2,405,352). I cannot reproduce it. The M4 meter fix does not apply: review.py writes the review tokens from provider usage, not from meter.py.

## Q5 (Edit tail)

The tail is real. 61 Edits: median 0.33 s, max 19.4 s, sum 155 s from message end (186.7 s from the tool block). There are no hook lines (`--safe-mode`). File size does not explain it: a 6 KB ObjectPool.h Edit took 9.7 s. Slow calls (> 5 s) also occur in Grep (18 s) and Bash (5.9 s). They come at the same seconds in parallel sessions (lg-01a and scd-01a at 14:24:28-41, lg-01b and lg-01c at 14:38:50-52), and most come while a local gate_sh or parity_sh runs. The likely cause is host-wide I/O or CPU contention ❓, not the Edit tool. The fix is D28 (builds off the local host). Do not make an author-side change. The sum over all parallel sessions is ≤ 155 s, so the critical-path share is smaller.
