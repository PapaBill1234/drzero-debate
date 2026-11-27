#!/usr/bin/env python3
"""Self-evolving proposer/solver debate about the parity v2 engine.

Idea from Dr. Zero (Meta, arXiv 2601.07055): a proposer asks harder and
harder questions, a solver answers them with tools, and the difficulty
follows the solver success rate. Dr. Zero trains the model weights. We
cannot train weights, so here the "evolution" lives in files:

  curriculum.json  difficulty level per subject (1..10)
  lessons.jsonl    verified findings; every later prompt reads them
  questions.jsonl  every question, answer, grade and token cost

Agents (each one a `claude-gw -p` call, read-only tools):

  3 proposers   P-cost (auditor), P-build (engineer), P-break (adversary)
  3 solvers     S-code (reads code), S-data (measures logs/ledgers),
                S-design (research + design, may web search)
  1 base        judge: verifies each answer against the repo, grades it,
                keeps or drops the lesson, moves the difficulty;
                at the end writes REPORT.md

Usage:
  python3 -I drzero.py run --out /data/parity-v2/drzero/run1 --rounds 4
  python3 -I drzero.py report --out /data/parity-v2/drzero/run1
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

HOME = Path.home()
ENGINE = HOME / "Documents/Codex/private-project/design/parity-v2"
LIFT = HOME / "Documents/Codex/private-project/bns-lift"
DATA = Path("/data/parity-v2")
CLAUDE = str(HOME / ".local/bin/claude-gw")

SUBJECTS = {
    "tokens": "Token efficiency of the parity v2 engine: tokens per MATCH, "
              "prompt size, retries, review cost, cache use. The old wave "
              "system made about 67k tokens per MATCH; v2 made 136-160k.",
    "quality": "Better parity quality: more real MATCHes per card, fewer "
               "regressions, better review, better card selection.",
    "hard": "Functions that agents fail to MATCH (block order, register "
            "choice, inlining, folded code, EH, STL layout). Find the "
            "patterns and the fixes or tools that unblock them.",
    "tools": "The Python tools in parityctl/: correctness, speed, "
             "clear errors, missing tools, dead code, test gaps.",
    "ops": "Unattended operation: pauses, usage limits, crash recovery, "
           "land queue, backups, build hosts, canary gaps.",
}

PROPOSERS = {
    "P-cost": "You are a cost auditor. You hunt for wasted tokens, time and builds.",
    "P-build": "You are a senior build engineer. You ask how the engine really behaves.",
    "P-break": "You are an adversary. You look for hidden failure modes and false claims.",
}
SOLVERS = {
    "S-code": "You answer by reading code and git history. Quote file:line.",
    "S-data": "You answer by measuring: ledgers, logs, results JSON, meter.py. Give numbers.",
    "S-design": "You answer with a concrete design. You may search the web for prior art. Tie it to this code.",
}

RULES = """Rules:
- Read only. Never edit, write, commit or push anything.
- Never read ~/.claude/.credentials*, ~/.codex/auth.json, ~/.local/state/**, keys, or the IDA licence. Never print a key.
- Do not open IDA. Do not start builds or agents.
- Write in ASD-STE100: short sentences, active voice. Give sizes in tokens.
- Every claim needs evidence (file:line, command output, number). Mark guesses with ❓."""

READ_TOOLS = ["Read", "Grep", "Glob",
              "Bash(git log:*)", "Bash(git show:*)", "Bash(git diff:*)",
              "Bash(rg:*)", "Bash(wc:*)", "Bash(ls:*)", "Bash(head:*)", "Bash(tail:*)",
              "Bash(jq:*)", "Bash(python3 -I parityctl/meter.py:*)"]
DENY_TOOLS = ["Write", "Edit", "NotebookEdit", "Agent", "Task"]

Q_SCHEMA = {"type": "object", "required": ["question", "why", "how_to_check"],
            "properties": {"question": {"type": "string"}, "why": {"type": "string"},
                           "how_to_check": {"type": "string"}}}
A_SCHEMA = {"type": "object", "required": ["answer", "evidence", "proposal", "confidence"],
            "properties": {"answer": {"type": "string"},
                           "evidence": {"type": "array", "items": {"type": "string"}},
                           "proposal": {"type": "string"},
                           "confidence": {"type": "number"}}}
J_SCHEMA = {"type": "object",
            "required": ["score", "verified", "too_easy", "lesson", "gain", "notes"],
            "properties": {"score": {"type": "number"}, "verified": {"type": "boolean"},
                           "too_easy": {"type": "boolean"}, "lesson": {"type": "string"},
                           "gain": {"type": "string", "enum": ["none", "low", "medium", "high"]},
                           "notes": {"type": "string"}}}

LOCK = threading.Lock()


def call(prompt, schema, out, tag, tools, effort, model, budget_turns):
    """One claude-gw -p call. Returns (structured_output, usage dict)."""
    cmd = [CLAUDE, "-p", "--model", model, "--effort", effort,
           "--output-format", "json", "--no-session-persistence",
           "--json-schema", json.dumps(schema),
           "--add-dir", str(LIFT), "--add-dir", str(DATA),
           "--max-turns", str(budget_turns)]
    if tools:
        cmd += ["--allowedTools", *tools, "--disallowedTools", *DENY_TOOLS]
    else:
        cmd += ["--tools", ""]
    for attempt in range(3):
        p = subprocess.run(cmd, cwd=ENGINE, capture_output=True, text=True,
                           input=prompt, timeout=3600)  # stdin: argv has a size limit (E2BIG)
        try:
            d = json.loads(p.stdout)
        except json.JSONDecodeError:
            d = {"is_error": True, "result": (p.stdout + p.stderr)[-2000:]}
        if not d.get("is_error") and d.get("structured_output") is not None:
            break
        if any(k in str(d.get("result", "")).lower() for k in ("usage limit", "rate limit", "quota")):
            print(f"[{tag}] usage limit; stop", file=sys.stderr)
            sys.exit(75)
        time.sleep(10 * (attempt + 1))
    u = d.get("usage") or {}
    cost = {"in": u.get("input_tokens", 0), "out": u.get("output_tokens", 0),
            "cc": u.get("cache_creation_input_tokens", 0),
            "cr": u.get("cache_read_input_tokens", 0),
            "turns": d.get("num_turns", 0)}
    with LOCK, open(out / "calls.jsonl", "a") as f:
        f.write(json.dumps({"t": time.time(), "tag": tag, **cost,
                            "error": bool(d.get("is_error"))}) + "\n")
    print(f"  call {tag}: {cost['turns']} turns, {cost['in'] + cost['out'] + cost['cc']} tokens nocr"
          f"{' ERROR' if d.get('is_error') else ''}", flush=True)
    return d.get("structured_output"), cost


def load_state(out):
    cur = out / "curriculum.json"
    curriculum = json.loads(cur.read_text()) if cur.exists() else {}
    lessons = []
    lp = out / "lessons.jsonl"
    if lp.exists():
        lessons = [json.loads(x) for x in lp.read_text().splitlines() if x.strip()]
    return curriculum, lessons


def lessons_text(lessons, subject, n=12):
    mine = [l for l in lessons if l["subject"] == subject][-n:]
    other = [l for l in lessons if l["subject"] != subject][-4:]
    if not mine and not other:
        return "No lessons yet."
    return "\n".join(f"- [{l['subject']} L{l['level']}] {l['lesson']}" for l in mine + other)


def past_questions(out, subject):
    qp = out / "questions.jsonl"
    if not qp.exists():
        return "None."
    qs = [json.loads(x) for x in qp.read_text().splitlines() if x.strip()]
    qs = [q for q in qs if q["subject"] == subject][-8:]
    return "\n".join(f"- L{q['level']} score {q['grade']['score']:.1f}: {q['question']}" for q in qs) or "None."


def one(out, rnd, i, subject, curriculum, lessons, args):
    SUBJECTS = args.subject_map
    pname = list(PROPOSERS)[(rnd + i) % 3]
    sname = list(SOLVERS)[(rnd + 2 * i) % 3]
    level = curriculum[subject]
    common = (f"System under study: the parity v2 engine at {ENGINE} (code in parityctl/, docs *.md), "
              f"its run data under {DATA}, and the C++ lift at {LIFT}.\n{RULES}\n{args.context}\n")
    qp = (f"{PROPOSERS[pname]}\n{common}\nSubject: {SUBJECTS[subject]}\n"
          f"Difficulty level {level} of 10. Level 1 = a fact you can check in one file. "
          f"Level 10 = a deep question that needs many files, data and a design to answer.\n"
          f"Verified lessons so far (build on them; do not ask them again):\n{lessons_text(lessons, subject)}\n"
          f"Questions already asked:\n{past_questions(out, subject)}\n"
          f"Explore the repo briefly. Then write ONE new question at this level. "
          f"It must be answerable from the repo or data, and the answer must lead to a concrete improvement.")
    q, qc = call(qp, Q_SCHEMA, out, f"r{rnd}-{subject}-{pname}", READ_TOOLS,
                 args.effort, args.model, 15)
    if not q:
        return None
    sp = (f"{SOLVERS[sname]}\n{common}\nSubject: {SUBJECTS[subject]}\n"
          f"Verified lessons:\n{lessons_text(lessons, subject)}\n"
          f"Question (level {level}): {q['question']}\nWhy it matters: {q['why']}\n"
          f"Answer it with tools. Then give one concrete proposal (what to change, where, expected gain).")
    stools = READ_TOOLS + (["WebSearch", "WebFetch"] if sname == "S-design" else [])
    a, ac = call(sp, A_SCHEMA, out, f"r{rnd}-{subject}-{sname}", stools,
                 args.effort, args.model, args.solver_turns)
    if not a:
        return None
    jp = (f"You are the judge (base model). {common}\nSubject: {subject}. Level {level}.\n"
          f"Question: {q['question']}\nHow to check: {q['how_to_check']}\n"
          f"Answer: {a['answer']}\nEvidence: {json.dumps(a['evidence'])}\nProposal: {a['proposal']}\n"
          f"Check the key evidence yourself with tools (open the cited files, rerun a cheap command). "
          f"score 0..1 = how correct and useful. verified = you confirmed the main claim. "
          f"too_easy = the solver needed almost no work. lesson = one ASD-STE100 sentence that a "
          f"future agent must know (empty if nothing verified). gain = value of the proposal.")
    g, gc = call(jp, J_SCHEMA, out, f"r{rnd}-{subject}-judge", READ_TOOLS,
                 args.effort, args.model, 15)
    if not g:
        return None
    rec = {"round": rnd, "subject": subject, "level": level, "proposer": pname, "solver": sname,
           "question": q["question"], "why": q["why"], "answer": a["answer"],
           "evidence": a["evidence"], "proposal": a["proposal"], "confidence": a["confidence"],
           "grade": g, "tokens": {k: qc[k] + ac[k] + gc[k] for k in ("in", "out", "cc", "cr")}}
    with LOCK:
        with open(out / "questions.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        if g["verified"] and g["lesson"].strip():
            with open(out / "lessons.jsonl", "a") as f:
                f.write(json.dumps({"subject": subject, "level": level, "round": rnd,
                                    "lesson": g["lesson"], "gain": g["gain"],
                                    "proposal": a["proposal"]}) + "\n")
    print(f"r{rnd} {subject:8} L{level} {pname}/{sname} score {g['score']:.2f} "
          f"verified {g['verified']} easy {g['too_easy']} gain {g['gain']}", flush=True)
    return rec


def evolve(curriculum, recs):
    """Dr. Zero rule: keep tasks hard but solvable."""
    for r in recs:
        s, g = r["subject"], r["grade"]
        if g["verified"] and (g["too_easy"] or g["score"] >= 0.8):
            curriculum[s] = min(10, curriculum[s] + 1)
        elif g["score"] < 0.4:
            curriculum[s] = max(1, curriculum[s] - 1)


def run(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    subjects = args.subjects.split(",") if args.subjects else list(args.subject_map)
    for rnd in range(args.start, args.start + args.rounds):
        curriculum, lessons = load_state(out)
        for s in subjects:
            curriculum.setdefault(s, args.start_level)
        with cf.ThreadPoolExecutor(args.parallel) as ex:
            futs = [ex.submit(one, out, rnd, i, s, curriculum, lessons, args)
                    for i, s in enumerate(subjects)]
            recs = [f.result() for f in futs]
        recs = [r for r in recs if r]
        evolve(curriculum, recs)
        (out / "curriculum.json").write_text(json.dumps(curriculum, indent=1))
        print(f"round {rnd} done; curriculum {curriculum}", flush=True)
    report(args)


def report(args):
    out = Path(args.out)
    qs = [json.loads(x) for x in (out / "questions.jsonl").read_text().splitlines() if x.strip()]
    calls = [json.loads(x) for x in (out / "calls.jsonl").read_text().splitlines() if x.strip()]
    nocr = sum(c["in"] + c["out"] + c["cc"] for c in calls)
    digest = "\n\n".join(
        f"[{q['subject']} L{q['level']} score {q['grade']['score']:.2f} verified {q['grade']['verified']} "
        f"gain {q['grade']['gain']}]\nQ: {q['question']}\nA: {q['answer'][:1500]}\nProposal: {q['proposal']}"
        for q in qs)
    prompt = (f"{args.context}\nYou are the base model. Below are all graded questions of a self-evolving debate about "
              f"the parity v2 engine at {ENGINE}.\n{RULES}\n\n{digest}\n\n"
              "Write REPORT.md in ASD-STE100. Per subject: the top proposals ranked by gain and evidence "
              "(only verified ones at the top), what each costs to build, and which file it changes. "
              "Then one table of the 10 best actions over all subjects, in order. Then open questions.")
    r, c = call(prompt, {"type": "object", "required": ["markdown"],
                         "properties": {"markdown": {"type": "string"}}},
                out, "report", None, args.effort, args.model, 3)
    head = (f"<!-- drzero run: {len(qs)} questions, {len(calls)} calls, {nocr} tokens nocr "
            f"(input + output + cache creation) -->\n")
    (out / "REPORT.md").write_text(head + (r or {}).get("markdown", "report failed"))
    print(f"REPORT.md written; {len(qs)} questions; {nocr} tokens nocr")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--subjects", default="")
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--solver-turns", type=int, default=40)
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--subjects-file", help="JSON {name: description}; replaces the built-in subjects")
    ap.add_argument("--context-file", help="text added to every prompt (goals, facts)")
    ap.add_argument("--start-level", type=int, default=2)
    args = ap.parse_args()
    args.subject_map = json.loads(Path(args.subjects_file).read_text()) if args.subjects_file else SUBJECTS
    args.context = Path(args.context_file).read_text() if args.context_file else ""
    run(args) if args.cmd == "run" else report(args)


if __name__ == "__main__":
    main()
