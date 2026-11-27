# drzero: a self-evolving agent debate that audits a build engine

`drzero.py` makes Claude agents ask each other harder and harder questions about a code base. A judge checks each answer with tools. The verified answers become lessons and proposals. We used it to audit the **parity v2 engine**: the system that drives Claude agents to lift a game binary back to C++ until each function matches byte for byte ("MATCH").

The idea comes from **Dr. Zero** (Meta, [arXiv 2601.07055](https://arxiv.org/abs/2601.07055)). There, a proposer and a solver train each other: the proposer makes tasks at the edge of what the solver can do. We cannot train model weights. So in this tool the "evolution" lives in files: a difficulty curriculum and a list of verified lessons that every later prompt reads.

## 1. How it works

```
             ┌──────────── curriculum.json (level 1..10 per subject) ───────────┐
             │                                                                   │
             ▼                                                                   │
  ┌────────────────────┐   question   ┌────────────────────┐   answer +   ┌─────┴──────┐
  │ Proposer (1 of 3)  │ ───────────▶ │ Solver (1 of 3)    │ ───────────▶ │   Judge    │
  │ P-cost  auditor    │              │ S-code   reads code│   evidence   │ re-checks  │
  │ P-build engineer   │              │ S-data   measures  │   proposal   │ evidence,  │
  │ P-break adversary  │              │ S-design web+design│              │ grades     │
  └────────▲───────────┘              └────────────────────┘              └─────┬──────┘
           │                                                                    │
           └──────────────── lessons.jsonl (verified lessons only) ◀────────────┘
```

| Step | What happens |
| --- | --- |
| 1 | Per round, each subject gets one question. Proposer and solver rotate over the rounds. |
| 2 | The **proposer** explores the repo, reads the lessons and past questions, and writes ONE new question at the current level of the subject. Level 1 = a fact in one file. Level 10 = a question that needs many files, data and a design. |
| 3 | The **solver** answers with read-only tools. It gives evidence (file:line, command output, numbers) and one concrete proposal. |
| 4 | The **judge** opens the cited files and reruns cheap commands. It gives a score 0-1, `verified`, `too_easy`, a one-sentence lesson and a gain (none/low/medium/high). |
| 5 | **Evolve** (the Dr. Zero rule: keep tasks hard but solvable): verified and (too easy or score ≥ 0.8) → level + 1. Score < 0.4 → level − 1. |
| 6 | After the last round, one call writes `REPORT.md`: top proposals per subject, the 10 best actions, open questions. |

Every agent is one headless `claude -p` call with a JSON schema for its output:

- Read-only tools only: Read, Grep, Glob, `git log/show/diff`, `rg`, `ls`, `jq`, and the token meter. Write, Edit and sub-agents are denied.
- The rules in every prompt forbid reading credentials and keys, starting builds and opening IDA.
- Only the S-design solver may search the web.
- A usage-limit reply stops the run with exit code 75, so a resume is clean.

## 2. Files

| Path | Content |
| --- | --- |
| `drzero.py` | The tool (291 lines, standard library only) |
| `runs/smoke/` | 1-question smoke test |
| `runs/run1/` | Run 1: 5 general subjects, 8 rounds |
| `runs/run2/` | Run 2: 6 subjects for the owner goal "1-hour wave, fewer tokens per MATCH than the manual wave" |
| `runs/*/questions.jsonl` | Every question, answer, evidence, proposal, grade and token cost |
| `runs/*/lessons.jsonl` | Verified lessons only |
| `runs/*/calls.jsonl` | One row per model call: tokens in/out/cache, turns, error |
| `runs/*/curriculum.json` | Final level per subject |
| `runs/*/REPORT.md` | The report written by the base model |
| `examples/` | The run 2 subjects file and context file |
| `docs/run1-explained.md` | What the run 1 report means in plain words, with estimated effect |
| `docs/all-proposals.md` | Master list of all proposals (D01-D41, M01-M68, run1/run2 items) |
| `verify/` | 10 independent verifier reports that re-checked the proposals before we built them |
| `docs/build-plan.md` | Which proposals we built, on which branch, and what we rejected |
| `docs/baseline-check.md` | The baseline numbers that the runs compare against |

## 3. Usage

```bash
# 4 rounds over the built-in subjects
python3 -I drzero.py run --out runs/run1 --rounds 4

# Resume with 4 more rounds (the curriculum and lessons carry over)
python3 -I drzero.py run --out runs/run1 --rounds 4 --start 5

# Own subjects and goals
python3 -I drzero.py run --out runs/run2 --rounds 8 \
  --subjects-file examples/run2-subjects.json --context-file examples/run2-context.txt

# Only rewrite the report
python3 -I drzero.py report --out runs/run1
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--rounds` / `--start` | 4 / 1 | Number of rounds / first round number (to resume) |
| `--parallel` | 3 | Subjects worked on at the same time |
| `--solver-turns` | 40 | Turn limit for a solver (proposer and judge: 15) |
| `--model` / `--effort` | opus / medium | Model and effort for all agents |
| `--start-level` | 2 | Start level for a new subject |

To use it on another code base, change `ENGINE`, `LIFT`, `DATA` and `CLAUDE` at the top of `drzero.py`, and give your own subjects and context.

## 4. Results

| Run | Questions | Verified | Gain high / medium / low | Calls | Tokens (no cache reads) | Cache reads | Wall time |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| smoke | 1 | 1 | 0 / 1 / 0 | 4 | 0.1M | 0.7M | 0.1 h |
| run1 | 39 | 39 | 16 / 21 / 2 | 121 | 5.0M | 50.3M | 7.3 h |
| run2 | 47 | 46 | 12 / 27 / 8 | 144 | 6.7M | 69.3M | 5.3 h |

The curriculum worked as intended: every subject climbed from level 2 to level 8-10, so the later questions became deep, multi-file questions.

### Run 1: general audit (tokens, quality, hard functions, tools, ops)

The main result: v2 was not slow and costly because of its design. It lost most of its value in 4 places.

| Place | What went wrong |
| --- | --- |
| Credit | 62 accepted reviews gave 0 credit, because their digest pointed at an old version of the review tool. |
| Author context | Authors ran with no context limit. Context grew to about 168k tokens, mostly repeated cache reads. |
| Review reuse | The reuse function `carry()` ran 0 times in 355 reviews, so items were reviewed again and again. |
| Fix list order | Items that can never MATCH were at the top of the list, so agents spent builds on them. |

It also found operation faults: a dead build host held a slot for 2.2 h (no ssh keep-alive), 21 % of lands needed a person, and limit messages or crashes could park good cards.

### Run 2: the 1-hour wave and the token goal

| Finding | Evidence (from the report) |
| --- | --- |
| The wave is limited by its critical path, not by the number of build hosts. | Peak 4 builds at the same time out of 18 slots |
| 3 stalls dominate the path. | The `gc` tail, an uncached layout-check tail, and fresh base builds for docs-only changes |
| The card runner never used the slot queue. | All 28 full builds ran locally while 10 remote slots were idle |
| The lead session, not the card agents, used most tokens. | Lead 63 % of tokens; true wave cost 186.5k tokens per MATCH (author-only figure 68.2k) |
| Some safety holes were real. | One card got 29 MATCH from a gate with no layout check |

### From proposals to code

1. The 2 reports and the per-question proposals were merged into one master list (`docs/all-proposals.md`).
2. 10 verifier agents re-checked them independently (`verify/`). The verifiers corrected several numbers (for example, some gains were overstated).
3. Each item was then marked BUILD, LATER or REJECT.
4. BUILD items went to the engine in small branches, each with tests and a canary run (`docs/build-plan.md`).
5. Examples of fixes that landed: ssh keep-alive, credit that stays valid, land counted after push, a precheck before builds, crash retry, a usage-limit stop, cache keys, and remote-first build slots.

## 5. Lessons about the method

| # | Lesson |
| --- | --- |
| 1 | **The judge must check with tools.** Asking the judge for an opinion only is not enough. Re-opening the cited files caught wrong numbers. |
| 2 | **A second, independent check is still needed.** The judge uses the same model as the solver and can share its blind spot. The 10 verifiers corrected several "verified" claims. |
| 3 | **The curriculum keeps the debate useful.** Without the level, proposers repeat easy questions. With it, round 6-8 questions crossed many files and logs. |
| 4 | **The lessons file stops repeats.** The proposer gets the verified lessons and the past questions, so it moves on to new ground. |
| 5 | **A context file aims the debate at a goal.** Run 2 got a goal (1-hour wave, < 84k tokens per MATCH) and base numbers. Its answers were much more concrete than run 1. |
| 6 | **Cost is moderate.** About 130k tokens (no cache reads) per question, 5-7M per run. |
| 7 | **Most token cost is in long-lived sessions, not in the work agents.** Both runs pointed at lead and operator context as the main cost. This led to a "clear after 3-4 cards" rule and a token watch per MATCH. |

## 6. Limits

- The tool expects the `claude` CLI (here a wrapper called `claude-gw`) with `--json-schema` and `--output-format json`.
- The paths at the top of `drzero.py` point at our own engine. The run data refers to files that are not in this repo.
- Gains in the reports are estimates from past ledgers. Marks with ❓ are not measured.
- Host IP addresses in the run data are redacted.
