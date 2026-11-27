# Dr. Zero run1: what the report means

Source: `/data/parity-v2/drzero/run1/REPORT-rounds1-4.md` (rounds 1-4, 20 questions, all verified, mean score 0.84, cost 2.02M tokens nocr).

Estimates marked ❓ are my rough numbers. They are not measured. The operator must measure each fix after it lands.

## 1. Short answer

The debate found that v2 is not slow and costly because of its design. It loses most of its value in 4 places:

| Place | What goes wrong | Effect today |
| --- | --- | --- |
| Credit | 62 accepted reviews give 0 credit, because their digest is for an old `review.py`. | Paid work does not count. Only about half of the raw MATCHes get credit. |
| Author context | Authors run as general subagents with no limit. Context grows to about 168k tokens. | Most author tokens are cache reads of the same text again and again. |
| Reviews | The reuse function `carry()` ran 0 times in 355 reviews. | The same items are reviewed again at about 8k tokens each. |
| Fix list | Items that cannot MATCH (lone LTCG constants) are at the top of the list. | Agents spend builds on work with no gain. |

There are also operation faults. A dead host blocks a slot for about 2.2 hours. 21 % of lands need a person. Limit texts and crashes can park good cards.

## 2. Token effect (cost per MATCH)

v2 today: 136k-160k tokens nocr per MATCH. Manual wave today: 84k.

| Fix | Mechanism | Rough effect on v2 tokens per MATCH ❓ |
| --- | --- | --- |
| Credit stays valid; feedback uses credited MATCH | Same tokens, more MATCH counted (credited share 0.31 → about 0.43) | −25 % to −30 % |
| Author context split at 100k; authors through author.py limits | Author cache reads fall by 25-30 %; author is the largest cost | −12 % to −18 % |
| Review reuse (`carry()` works) and correct `review_item` | Up to 51 % of review tokens are repeats | −8 % to −12 % |
| Fix list order (lone_constant, data_ref split) | 12 dead items leave the top 50; 13-16 builds saved | −3 % to −6 % |
| Repair gate values corrected | The gate stops blocking the repairs that gave 29 of 29 credited MATCH | protects gain; no direct cut |

Combined (the effects multiply, not add):

| Case ❓ | v2 tokens per MATCH | Compared with manual wave (84k) |
| --- | ---: | --- |
| Bad case | about 95k | still 13 % more |
| Middle case | about 75k | about 10 % cheaper |
| Good case | about 65k | about 23 % cheaper |

So these fixes alone can bring v2 near or below the manual wave. The run2 debate looks for the rest.

## 3. Time and reliability effect

| Fix | Today | After the fix |
| --- | --- | --- |
| ssh keep-alive and wait timeout | A dead host holds a slot for 7,875 s (2.2 h) | Found in about 60 s |
| Precheck before the build | 3 of 9 proof failures run a full build first (one wasted 26 min) | Stop in less than 1 s |
| Lazy proof lookup | 195 s per ledger backfill | 0.5 s |
| Land counts after push | 21 % of lands need a person | about 0 % ❓ |
| Limit texts from one source | 11 limit texts can park a good card | 0 |
| Crash does not use a retry | A card parks on crash 3 | Stays in the queue |

These fixes do not make a normal build faster. They remove the long stalls and the manual work. The 1-hour wave goal is the subject of run2.

## 4. How much of each problem the fixes solve

| Problem | Share solved by run1 fixes ❓ | What is left |
| --- | ---: | --- |
| Unattended operation (parks, stalls, manual lands) | 80-90 % | Real crash data; dedicated server setup |
| Credit and quality accounting | 70-80 % | Re-review cost (about 0.5M tokens once); p values with small samples |
| Token cost per MATCH | 40-55 % of the gap to 84k, or all of it in the good case | Author prompt size, review design (run2) |
| Hard functions (cannot MATCH) | 20-30 % | Real fixes need labelled cases; LTCG items stay hard |
| Wave wall time (4-5 h → 1 h) | 10-15 % | Build and funcdiff speed, more hosts, pipelining (run2) |
| Tool quality | 50-60 % | Run data in the code folder, atomic writes, dead modules |

## 5. Order of work (given to the CLI operator)

1. ssh keep-alive (S, 2 lines).
2. Credit stays valid (S to start).
3. Land counts after push (M).
4. `lone_constant` ease 0.1 (S).
5. Feedback on credited MATCH (M).
6. Repair gate values (S).
7. Limit texts and crash wait (S).
8. data_ref split (M).
9. Precheck (M).
10. Then: find why `carry()` never runs, author context split, StreamMeter, lazy proof lookup.

S = less than 30 lines. M = 30-150 lines. L = more than 150 lines.

## 6. Limits of this report

- 2 answers (quality L4, tools L4) could not finish large file scans. Their numbers are partial.
- The token savings come from past ledgers. The ledger has gaps (7 cards with timestamp 0; 99 reviews record only the last call).
- The judge is the same model as the solvers. It checked the evidence with tools, but it can share a blind spot.
