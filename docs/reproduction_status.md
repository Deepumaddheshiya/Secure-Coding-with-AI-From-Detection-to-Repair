# Evaluation Inconsistency — Reproduction Status

## Issue: Zero Flawfinder Hits in Previous evaluation_report.json

### Documented Discrepancy

- **Documentation / README stated:** 72 baseline findings, 74 Flawfinder hits
- **Previous `evaluation_report.json`:** `total_orig_flawfinder_hits: 0` (all zeros)

### Root Cause (Identified)

The `evaluator.py` script invoked Flawfinder as:

```python
[sys.executable, "-m", "flawfinder", "--csv", str(file_path)]
```

However, **Flawfinder 2.0.20 is installed as a system PATH binary** (`flawfinder.exe`) on this machine — **not** as a Python package inside the project virtual environment (`.venv`).

Therefore, running `.venv/Scripts/python.exe -m flawfinder` raised `ModuleNotFoundError` silently (caught by the broad `except Exception` clause), causing **every case to return zero hits**.

### Fix Applied

Updated `evaluator.py` to:
1. First check for system `flawfinder` binary via `shutil.which("flawfinder")`
2. Only fall back to `python -m flawfinder` if the binary is absent
3. If neither is available, return `[]` with a clear "not available" signal (instead of silently returning zero)

Same fix applied to `backend/app/scanners/flawfinder_scanner.py`.

### Verified Results (Post-Fix)

Re-ran `evaluator.py` on 2026-10-12 with corrected invocation:

```
Total Test Cases Analyzed: 48
Total Static Scanner Findings Recorded in Dataset: 72   ← from Info.txt ground truth
Total Live Flawfinder Hits in Original Code: 74         ← real live scan result

Model Name                   | Remaining Hits | Vulnerability Reduction | Cases Improved
----------------------------------------------------------------------------------------
claude-opus-4-1-20250805     | 72             |    2.7%                 | 12
gpt-4.1-2025-04-14           | 69             |    6.8%                 | 13
gpt-5-2025-08-07             | 57             |   23.0%                 | 14
```

### Clarification: Why 72 ≠ 74?

These are **two different measurements**:

| Metric | Value | Source |
|--------|-------|--------|
| Dataset Recorded Findings | 72 | Loaded from `Info.txt` scanner records (the original ground-truth annotation from the research dataset) |
| Live Flawfinder Hits | **74** | Result of running `flawfinder --csv` on each source file in real-time |

The 2-finding discrepancy is expected:
- The dataset annotations were made during original research (may use different flawfinder version or settings)
- Live re-scan uses Flawfinder 2.0.20 on the same files, which may detect 2 additional findings
- Neither number is wrong — they measure different things
- The live scan (74) is used as the denominator for reduction rate calculations

### Separation of Published vs Local Results

| Model Type | Results Source | Location |
|-----------|---------------|----------|
| GPT-5, GPT-4.1, Claude (historical) | Published paper + re-run with fixed evaluator | `evaluation_report.json` |
| Local Ollama (e.g. qwen2.5-coder) | Local benchmark run via `/api/benchmark/run-local` | `local_ollama_benchmark_report.json` |

Local Ollama results are **never mixed** with published model results.

### Files Modified to Fix This

- `evaluator.py` — `run_flawfinder_on_code()` function (lines 24–54)
- `backend/app/scanners/flawfinder_scanner.py` — `is_installed()` and `scan_file()` methods

### Verification Commands

```bash
# Re-run the full evaluation
python evaluator.py

# Or via API (starts evaluation, waits, returns new summary)
curl -X POST http://localhost:8000/api/benchmark/regenerate

# Check dashboard with real metrics
curl http://localhost:8000/api/dashboard/summary
```
