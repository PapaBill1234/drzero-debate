<!-- drzero run: 1 questions, 3 calls, 129901 tokens nocr (input + output + cache creation) -->
# REPORT.md: parity v2 engine, graded debate results

## 0. How this report was made

| Item | Value |
| --- | --- |
| Input | 1 graded question: subject `tools`, level L2, score 0.86, verified = True, gain = medium |
| My own checks | None. The rules say "Do not open IDA". I have no other file or shell tool, so I did not read files again. |
| Evidence source | All file:line facts below come from the verified debate answer. I did not measure them again. |
| File output | I did not write `REPORT.md` to disk because the rules say "Read only". This text is the content for that file. |

Legend: ✅ = the debate verified it. ❓ = it is a guess or the debate did not measure it.

---

## 1. Subject: tools (hard-coded uv cache path)

### 1.1 Facts (verified in debate)

| # | Fact | Evidence |
| --- | --- | --- |
| F1 | 20 files in `parityctl/` hard-code `~/.cache/uv/archive-v0/IbzDUkmlTzOa319J/lib/python3.12/site-packages`. | backend.py:46 `SITE`, buildonce.py:66 `UVLIB`, remote_build.py:1070 `UV_SITE`, step5_slices.py:6, gate_fast.sh:22, preview_build.sh:73, cardrun.py:167 ✅ |
| F2 | The 20 files are 13 Python constants (10 tools and 3 tests) and 7 shell scripts. | test_insn_diff.py:20, test_strict.py:124, test_cfgcheck.py:94 ✅ |
| F3 | No file checks that the directory exists before use. No file reads an environment override. | Debate answer ✅ |
| F4 | The path exists today. It holds capstone 5.0.9, pefile 2024.8.26 and ordlookup. | Debate answer ✅ |
| F5 | System python3 3.14.4 cannot import capstone or pefile. A missing path gives a failure. It does not find another copy. | Debate answer ✅ |
| F6 | Python loaders stop with `SystemExit` from funcdiff.py:38. The message is "funcdiff needs capstone and pefile (uv pip install capstone pefile)". It does not name the path. It gives the wrong fix. | strict.load, insn_diff.load_funcdiff, backend.load_x86 measured ✅ |
| F7 | `buildonce.file_id` catches `OSError` and returns `'-'`. The cache key changes and nothing fails. | buildonce.py:150 ✅ |
| F8 | Shell gates and builds: bwrap prints "Can't find source path .../capstone" and exits with rc=1. The text goes only to gate.log or run.log. gate.rc=1 looks the same as a real gate failure. | gate_fast, gate_full, preview_build, linked_build_* measured ✅ |
| F9 | 9 tests (3 direct, 6 through `backend.SITE`) skip silently when the path is missing. No test covers the missing-path case. | Debate answer ✅ |
| F10 | gate_fast.sh already uses exit code 4 for preflight failures. | gate_fast.sh:41-42 ✅ |
| F11 | The remote probe prints an empty string when the path is missing. | Debate answer ✅ (the debate gives no line number ❓) |

### 1.2 Failure modes today

```
uv cache clean  /  new uv hash
        │
        ├── Python tools ──► SystemExit (funcdiff.py:38) ── wrong fix text, no path
        ├── buildonce   ──► file_id → '-' ── silent cache-key change   (worst: no signal)
        ├── shell gates ──► bwrap rc=1 in gate.log ── looks like a real gate failure
        ├── tests       ──► silent skip ── CI stays green
        └── remote probe──► empty string ── looks like a valid value
```

### 1.3 Proposals, ranked by gain and evidence

| Rank | Proposal | Gain | Evidence | Cost ❓ (diff size) | Files changed |
| --- | --- | --- | --- | --- | --- |
| P1 | Add one resolver `uv_site()` in new `parityctl/uvsite.py`. It reads `PARITY_UV_SITE`, falls back to the current hash path, and checks `capstone/__init__.py`, `pefile.py` and `ordlookup/`. On failure it raises `SystemExit(2)` and names the path and the fix. It also runs as a CLI and prints the path. | High: 1 source of truth. A hash change needs 1 env var. | F1, F3, F6 ✅ | ~600 tokens | new `uvsite.py` |
| P2 | In buildonce, call `uv_site()` before the cache key is built. Remove the `'-'` path for this input. | High: closes the only silent wrong result. | F7 ✅ | ~150 tokens | buildonce.py (near :66 and :150) |
| P3 | In the 7 shell scripts, use `lib="${PARITY_UV_SITE:-$(python3 -I "$p/uvsite.py")}" \|\| exit 4`. Run it before `disk_guard` and bwrap. | High: rc 4 with the path on stderr, not rc 1 hidden in gate.log. | F8, F10 ✅ | ~350 tokens (7 × ~50) | gate_fast.sh, gate_full, preview_build.sh, linked_build_*, 7 scripts in total ❓ (the debate did not name all 7) |
| P4 | Replace the 10 Python tool constants with `uv_site()`. Call it once at each entry point. | Medium: removes the misleading funcdiff.py:38 text for these tools. | F1, F6 ✅ | ~500 tokens | backend.py:46, remote_build.py:1070, step5_slices.py:6, cardrun.py:167, and 6 more ❓ |
| P5 | Add 1 test. Set `PARITY_UV_SITE` to an empty temp directory. Expect `SystemExit` code 2 with the path in the message. Expect `gate_fast.sh` to give rc 4 with the path on stderr. | Medium: stops the problem from coming back. | F9 ✅ | ~400 tokens | new test file, for example `test_uvsite.py` ❓ |
| P6 | Make `remote_host_setup.sh` and the remote probe use the same value. Make the probe print `MISSING`, not an empty string. | Medium: remote errors become visible. | F11 ✅ (line ❓) | ~150 tokens | remote_host_setup.sh, remote_build.py (probe) |
| P7 | Change the 3 test constants to `uv_site()`. Decide if a missing path skips or fails. | Low to medium: tests stop skipping silently. | F2, F9 ✅ | ~150 tokens | test_insn_diff.py:20, test_strict.py:124, test_cfgcheck.py:94 |
| P8 | Fix the funcdiff.py:38 text. Name the path that was searched and point to `PARITY_UV_SITE`. | Low: defence in depth if P1 is bypassed. | F6 ✅ | ~80 tokens | funcdiff.py:38, funcdiff86 equivalent ❓ |

Total estimated diff: about 2,400 tokens ❓.

### 1.4 Answer to the graded question

| Question | Answer |
| --- | --- |
| Which tools check that the directory exists? | None (F3). |
| What happens when the directory is missing? | Python: misleading `SystemExit`. buildonce: silent `'-'` key. Shell: bwrap rc=1 in a log file. Tests: silent skip (F6 to F9). |
| Clear stop or later failure? | No tool stops early with a clear message. Some tools fail later, and buildonce does not fail at all. |
| Can 1 shared constant with 1 preflight check replace the 20 copies? | Yes. Use P1 + P3 + P4 + P7. The shell side calls the Python resolver, so there is 1 source. |

---

## 2. Top 10 actions over all subjects

Only 1 subject was graded, so all 10 actions come from `tools`.

| # | Action | Proposal | Why this order |
| --- | --- | --- | --- |
| 1 | Create `parityctl/uvsite.py` with `uv_site()`, the `PARITY_UV_SITE` override, a 3-item check, `SystemExit(2)` and CLI mode. | P1 | All other actions need it. |
| 2 | Call `uv_site()` in buildonce before the key is built. | P2 | Removes the only silent wrong result (F7). |
| 3 | Add the preflight with `\|\| exit 4` to gate_fast.sh. | P3 | Gate results are trusted most. rc 1 is ambiguous today (F8). |
| 4 | Add the same preflight to the other 6 shell scripts. | P3 | Same fault, same fix. |
| 5 | Replace the 10 Python tool constants. | P4 | Gives a clear message for all tools. |
| 6 | Add the missing-path test (Python and gate_fast.sh). | P5 | Protects actions 1 to 5. |
| 7 | Make the remote probe print `MISSING` and share the value with remote_host_setup.sh. | P6 | Remote errors become visible. |
| 8 | Change the 3 test constants. Decide between skip and fail. | P7 | Stops silent skips in CI. |
| 9 | Fix the funcdiff.py:38 message. | P8 | Defence in depth. |
| 10 | Clear `__pycache__` copies and grep again for the hash `IbzDUkmlTzOa319J`. Expect 0 hits outside `uvsite.py`. | — | Confirms that the 20 copies are now 1. |

---

## 3. Open questions

1. Which 7 shell scripts and 10 Python tools exactly make up the 20 files? The debate names only some of them. ❓
2. When the path is missing, must tests skip or fail? A failure is safer. It can break CI on hosts without uv. ❓
3. Which `SystemExit` code is correct in Python: 2, as proposed, or 4, to match the shell? ❓
4. Does the remote host use the same uv hash? If it does not, `PARITY_UV_SITE` must be set on both sides. ❓
5. Can capstone and pefile go into a pinned project venv (`uv sync`) instead of the uv archive cache? That removes the hash problem at the source. ❓
6. Do old buildonce cache entries with a `'-'` key exist now? If so, they must be removed after action 2. ❓
7. Where is the remote probe line? The debate gives no file:line. ❓

---

## Notes

- **Rule conflict.** The prompt says "Read only. Never edit, write…". It also asks me to "Write REPORT.md". I followed the read-only rule. This document is the file content. I did not write it to disk.
- **No checks by me.** All facts come from the verified debate answer. The cost estimates and the unnamed files are guesses, and I marked them with ❓.
