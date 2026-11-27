# Brief: verify Dr. Zero proposals (read only)

Write in ASD-STE100: short sentences, active voice, tables. Give sizes in tokens.

## Context
- Dr. Zero is a self-evolving model debate. In 2 runs it wrote 86 graded proposals for the parity v2 engine. The engine lifts server exes to C++ and counts functions that MATCH the original.
- The judge marked almost every entry "verified". That label is NOT a real filter. Treat every claim as a hypothesis.
- The owner does not want to miss good ideas. Your job: decide for each item, from the real code and data, whether it is real and worth building.

## Sources
| What | Path |
| --- | --- |
| Engine main (read only, a live operator uses it) | /home/ubuntu/Documents/Codex/private-project/design/parity-v2 (code in parityctl/) |
| Master list (41 merged items D01-D41 + dropped entries) | drzero/all-proposals.md in the engine |
| Full proposal texts (search by source ID, e.g. "run2-11") | /data/parity-v2/drzero/all-proposals.txt |
| Raw graded answers (question, answer, grade) | /data/parity-v2/drzero/run1/questions.jsonl, run2/questions.jsonl |
| Reports | /data/parity-v2/drzero/run1/REPORT.md, run2/REPORT.md |
| Run data (ledgers, waves, logs) | /data/parity-v2 (read only) |
| bns-lift (PUBLIC lift repo, gate tools) | /home/ubuntu/Documents/Codex/private-project/bns-lift |

## Items already being built (do not verify; mention only when your item depends on one)
D01-D05, D33 (agent A: credit, proof, backup); D09, D11, D13, D14 (agent B: planner, triage, cards); D30, D32 (agent C: remote deadlines, lead driver).

## For each item
1. Read the full source proposal(s) and the judge notes.
2. Check the code: does the defect or gap exist today? Give file:line. Is it already done (fully or partly)?
3. Check the numbers that the claim rests on, from data under /data/parity-v2 if possible. Say "measured", "plausible" or "guess".
4. Check the risk: can it break MATCH counting, proof safety or server safety checks? Does it conflict with another item?
5. Give a verdict: BUILD (real and worth it), BUILD-SMALL (only a reduced part), LATER (real, low value now), DONE (already in code), REJECT (wrong, stale or harmful).
6. For BUILD and BUILD-SMALL: the exact scope (files, functions, about how many lines), the test to add, the effort (S/M/L), and the order dependency.

## Rules
- Read only. Do not edit any repo file. Do not commit. The only file you write is your result file.
- Do not run waves, builds, model calls, claude-gw or ssh. Cheap local reads, greps, sqlite queries and short python3 -I scripts are fine.
- Never read or print credentials, keys or auth files.
- Do not open IDA.

## Output
Write /data/parity-v2/drzero/verify/<your batch name>.md with one table:
| Item | Verdict | Defect today (file:line) | Evidence quality | Risk | Scope if BUILD | Effort | Depends on |
Then one short paragraph per item with the reason.
Final reply to the lead: the table only (no paragraphs), under 400 words.
