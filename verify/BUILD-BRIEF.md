# Builder brief: Dr. Zero BUILD-SMALL items

You build a small group of engine fixes in your own git worktree. Owner approved BUILD-SMALL on 2026-11-26.

## Inputs

| What | Where |
| --- | --- |
| Master list (D rows) | `/home/ubuntu/Documents/Codex/private-project/design/parity-v2/drzero/all-proposals.md` |
| Verdicts and scope per item | `/data/parity-v2/drzero/verify/v1..v10*.md` (v10 = M rows) |
| Build plan | `design/parity-v2/drzero/build-plan.md` |
| Engine code | `<your worktree>/parityctl/` |

Build only the part that the verifier marked as good. Drop the parts the verifier rejected. If the verifier found a premise wrong, say so and skip it.

## Rules

1. Work only in your worktree and on your branch. Do not merge. Do not push. Do not edit the main checkout `design/parity-v2`.
2. Touch only the files of your group. Other agents own `integrate.py`, `ledger.py`, `feedback.py`, `backup/sync.sh`, `author.py`, `cardrun.py`, `buildcache.py`, `gate_fast.sh`, `proof.py`. If you need a change there, write it under "Needed in other files" in your report.
3. One commit per item (or per small group). Author and committer: `Claude <noreply@anthropic.com>`. Use `--no-verify`. No Co-Authored-By. Set `GIT_COMMITTER_NAME=Claude GIT_COMMITTER_EMAIL=noreply@anthropic.com`.
4. Run Python with `python3 -I`. Use `/usr/bin/grep` (the shell grep is slow).
5. Tests: `cd parityctl && python3 -I -m unittest discover -s tests -p '<file>'`. Add a test for each fix. Run the touched test files after each item. Run the full suite only once, at the end, in the background (it takes about 10 min on this disk). Main has 0 failures at 2d072424.
6. No live runs: no ssh to build hosts, no model calls, no waves. Use fakes.
7. Never print or copy keys or auth files. Never touch the IDA licence. No binaries in git.
8. Write in ASD-STE100. Report with tables. Sizes in tokens.

## Report (your final message)

| Item | Status (done / partial / skipped) | Commit | Defect (file:line) | Test |

Then: full-suite result, "Needed in other files", follow-ups.
