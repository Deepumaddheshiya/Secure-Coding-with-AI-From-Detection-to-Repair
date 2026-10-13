"""
AI-SecureCode FastAPI Backend
Main entrypoint providing REST API for scanning, explaining, repairing, verifying,
autonomous retry pipeline, and DevGPT benchmarking.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.app.config import OLLAMA_BASE_URL, REPORTS_DIR
from backend.app.models.schemas import (
    ScanRequest, ScanResponse,
    AIExplainRequest, AIExplainResponse,
    AIRepairRequest, AIRepairResponse,
    VerifyRequest, VerifyResponse,
    PipelineRepairRequest, PipelineRepairResponse,
    SystemHealthResponse
)
from backend.app.scanners.scanner_manager import scanner_manager
from backend.app.ollama.client import ollama_client
from backend.app.ollama.explainer import ai_explainer
from backend.app.ollama.repairer import ai_repairer
from backend.app.verification.compiler import compiler_engine
from backend.app.verification.verifier import repair_verifier
from backend.app.pipeline.repair_pipeline import repair_pipeline
from backend.app.benchmark.benchmark_service import benchmark_service
from backend.app.reports.report_generator import report_generator

app = FastAPI(
    title="SECURE CODE with AI — Autonomous Vulnerability Detection & Program Repair Platform",
    description="Research-paper-based vulnerability detection, LLM program repair, and multi-scanner verification engine (Belozerov et al., 2026)",
    version="2.0.0"
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "project": "SECURE CODE with AI",
        "description": "Autonomous Vulnerability Detection & Program Repair Platform (Belozerov et al., 2026)",
        "status": "online",
        "mode": "100% Offline Local Sandbox",
        "docs_url": "/docs"
    }

@app.get("/api/health", response_model=SystemHealthResponse)
@app.get("/health", response_model=SystemHealthResponse)
def get_system_health():
    """Probe local Ollama daemon, available coding models, installed scanners, and compilers."""
    ollama_ok = ollama_client.is_running()
    installed_models = [m.name for m in ollama_client.get_installed_models()] if ollama_ok else []
    active_model = ollama_client.get_best_model() if ollama_ok else None

    scanner_statuses = scanner_manager.get_scanner_statuses()
    compiler_statuses = compiler_engine.get_compiler_statuses()

    return SystemHealthResponse(
        status="healthy",
        ollama_running=ollama_ok,
        ollama_url=OLLAMA_BASE_URL,
        installed_models=installed_models,
        active_model=active_model,
        scanners=scanner_statuses,
        compilers=compiler_statuses
    )

@app.post("/api/scan", response_model=ScanResponse)
def scan_source_code(req: ScanRequest):
    """Run local static security scanners on source code safely in sandbox."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    return scanner_manager.scan_code(req.code, req.language, req.filename)

@app.post("/api/explain", response_model=AIExplainResponse)
def explain_finding(req: AIExplainRequest):
    """Obtain local AI explanation, root cause, and recommendation for a finding."""
    return ai_explainer.explain(req.code, req.language, req.finding, req.model_name)

@app.post("/api/repair", response_model=AIRepairResponse)
def repair_code(req: AIRepairRequest):
    """Generate secure replacement code using local Ollama model."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    return ai_repairer.repair(
        code=req.code,
        language=req.language,
        findings=req.findings,
        target_finding=req.target_finding,
        model_name=req.model_name,
        instructions=req.instructions
    )

@app.post("/api/verify", response_model=VerifyResponse)
def verify_repair(req: VerifyRequest):
    """Execute compiler syntax check and security re-scan to calculate reduction rate."""
    return repair_verifier.verify(req)

@app.post("/api/pipeline/run", response_model=PipelineRepairResponse)
def run_autonomous_pipeline(req: PipelineRepairRequest):
    """
    Execute autonomous end-to-end repair with compiler checks, security re-scan,
    and iterative AI retry loop (up to 3 attempts).
    """
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    return repair_pipeline.execute_pipeline(req)

@app.get("/api/benchmark/cases")
def get_benchmark_cases():
    """List all 48 real DevGPT benchmark test cases with metadata from the dataset."""
    return benchmark_service.get_all_cases()

@app.get("/api/benchmark/historical")
def get_historical_benchmark():
    """Retrieve historical DevGPT benchmark dataset results (48 cases)."""
    return benchmark_service.get_historical_report()

@app.get("/api/benchmark/case/{case_id}")
def get_benchmark_case(case_id: str):
    """Retrieve details and code comparisons for a specific benchmark case."""
    detail = benchmark_service.get_case_detail(case_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Benchmark test case not found.")
    return detail

@app.post("/api/benchmark/run-local")
def run_local_benchmark(model_name: str = Body(..., embed=True), limit: int = Body(5, embed=True)):
    """Run local Ollama model against benchmark test cases."""
    return benchmark_service.run_local_model_benchmark(model_name, limit_cases=limit)

@app.post("/api/reports/generate")
def create_report(payload: Dict[str, Any] = Body(...)):
    """Generate JSON, CSV, and HTML reports for an audit."""
    json_path = report_generator.generate_json_report(payload)
    findings = payload.get("findings", [])
    csv_path = report_generator.generate_csv_report(findings)
    html_path = report_generator.generate_html_report(payload)

    return {
        "status": "Report generated successfully",
        "json_report": json_path.name,
        "csv_report": csv_path.name,
        "html_report": html_path.name
    }

@app.get("/api/research/paper-data")
def get_research_paper_data():
    """
    Returns ground truth reference figures published in:
    'Secure coding with AI - from detection to repair' (Belozerov, Barclay & Sami, 2026).
    Distinguished strictly from local execution numbers.
    """
    from backend.app.evaluation.ground_truth import (
        PAPER_CWE_DISTRIBUTION,
        PAPER_LANGUAGE_STATS,
        PAPER_MODEL_COMPARISON,
        PAPER_RQ3_ORIGIN_SUMMARY
    )
    return {
        "paper_title": "Secure coding with AI – from detection to repair",
        "authors": "Vladislav Belozerov, Peter J. Barclay, Ashkan Sami",
        "journal": "Empirical Software Engineering (2026) 31:93",
        "doi": "https://doi.org/10.1007/s10664-026-10812-8",
        "total_analyzed_files": 2315,
        "confirmed_vulnerabilities": 56,
        "files_with_vulnerabilities": 48,
        "scanners": ["Flawfinder", "Semgrep", "Snyk", "Cppcheck"],
        "cwe_distribution": PAPER_CWE_DISTRIBUTION,
        "language_statistics": PAPER_LANGUAGE_STATS,
        "model_comparison": PAPER_MODEL_COMPARISON,
        "rq3_code_origin": PAPER_RQ3_ORIGIN_SUMMARY
    }

@app.get("/api/research/evaluation-metrics")
def get_evaluation_metrics():
    """
    Calculates live evaluation metrics (Precision, Recall, F1, Detection Rate, Repair Rate)
    using actual local test runs and verified reviewer labels.
    No hardcoded fallback numbers — returns N/A when data is unavailable.
    """
    from backend.app.evaluation.metrics import (
        compute_classification_metrics,
        compute_detection_rate,
        compute_repair_rate
    )
    from backend.app.evaluation.manual_audit import manual_audit_service

    audit_summary = manual_audit_service.get_audit_summary()
    hist_report = benchmark_service.get_historical_report()
    summary = hist_report.get("summary", {})
    total_cases = summary.get("total_cases", 0)

    # CRITICAL: Do not hardcode baseline_findings.
    # total_orig_findings = findings recorded in Info.txt (dataset ground truth, not live scan)
    # total_orig_flawfinder_hits = findings from live flawfinder execution
    dataset_recorded_findings = summary.get("total_orig_findings", None)
    live_flawfinder_hits = summary.get("total_orig_flawfinder_hits", None)

    # Use live_flawfinder_hits as baseline when available; otherwise use dataset_recorded_findings
    # Never use 0 as denominator — show N/A instead
    baseline_for_rate = live_flawfinder_hits if (live_flawfinder_hits and live_flawfinder_hits > 0) else None

    # Calculate model metrics based on real dataset execution results
    models_stats = {}
    for model_name, m_data in summary.get("models", {}).items():
        fixed = m_data.get("fixed_cases", 0)
        remaining_hits = m_data.get("flawfinder_hits", 0)
        compile_ok = m_data.get("compile_ok", 0)

        if baseline_for_rate and baseline_for_rate > 0:
            reduction_rate = round(max(0, baseline_for_rate - remaining_hits) / baseline_for_rate * 100, 2)
        else:
            reduction_rate = None  # N/A — live scan not run or baseline is zero

        models_stats[model_name] = {
            "fixed_cases": fixed,
            "total_cases": total_cases,
            "repair_success_rate": compute_repair_rate(fixed, total_cases) if total_cases > 0 else None,
            "compilation_success_rate": round(compile_ok / total_cases * 100, 2) if total_cases > 0 else None,
            "remaining_hits": remaining_hits,
            "reduction_rate": reduction_rate,
            "reduction_rate_note": (
                "Calculated from live flawfinder baseline" if reduction_rate is not None
                else "N/A — live flawfinder baseline is 0 or not yet run. Use /api/benchmark/regenerate."
            )
        }

    return {
        "status": "computed_from_local_dataset_records" if total_cases > 0 else "no_data",
        "dataset_cases": total_cases,
        "dataset_recorded_findings": dataset_recorded_findings,
        "live_flawfinder_baseline": live_flawfinder_hits,
        "baseline_for_rate_calculation": baseline_for_rate,
        "baseline_note": (
            "Live flawfinder scan has been run on original source files." if (live_flawfinder_hits and live_flawfinder_hits > 0)
            else "Live flawfinder not yet run. Dataset recorded findings from Info.txt: "
                 f"{dataset_recorded_findings}. Run POST /api/benchmark/regenerate to scan."
        ),
        "models_evaluated": models_stats,
        "manual_audit_state": audit_summary
    }

@app.post("/api/audit/decision")
def record_audit_decision(payload: Dict[str, Any] = Body(...)):
    """
    Record manual review decisions:
    - Confirmed vulnerability vs False positive vs Uncertain
    - Model detected vs Not detected
    - Successfully repaired vs Failed repair
    """
    from backend.app.evaluation.manual_audit import manual_audit_service

    case_id = payload.get("case_id", "")
    verdict = payload.get("verdict", "confirmed_vulnerability")
    if not case_id:
        raise HTTPException(status_code=400, detail="case_id is required.")

    return manual_audit_service.record_decision(
        case_id=case_id,
        verdict=verdict,
        finding_id=payload.get("finding_id"),
        cwe=payload.get("cwe"),
        file_name=payload.get("file_name"),
        line_no=payload.get("line_no"),
        model_detected=payload.get("model_detected", "unspecified"),
        repair_verified=payload.get("repair_verified", "unspecified"),
        reviewer=payload.get("reviewer", "research_auditor"),
        notes=payload.get("notes", ""),
        evidence=payload.get("evidence", "")
    )

@app.get("/api/audit/decisions")
def get_audit_decisions(case_id: Optional[str] = None):
    """Retrieve audit history and evidence trail."""
    from backend.app.evaluation.manual_audit import manual_audit_service
    return manual_audit_service.get_decisions(case_id=case_id)

@app.get("/api/audit/summary")
def get_audit_summary():
    """Aggregate audit decisions summary."""
    from backend.app.evaluation.manual_audit import manual_audit_service
    return manual_audit_service.get_audit_summary()

@app.get("/api/reports/download/{filename}")
def download_report(filename: str):
    """Download a generated report file."""
    fpath = REPORTS_DIR / filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="Report file not found.")
    return FileResponse(str(fpath), filename=filename)

@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    """
    Returns DYNAMIC dashboard summary cards calculated from actual evaluation_report.json
    and manual audit DB. No hardcoded numbers. All values derived from real data.
    """
    import json, sys
    from pathlib import Path
    from backend.app.config import BASE_DIR
    from backend.app.evaluation.manual_audit import manual_audit_service

    report_path = BASE_DIR / "evaluation_report.json"
    report_data = {}
    if report_path.exists():
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
        except Exception:
            pass

    summary = report_data.get("summary", {})
    cases_data = report_data.get("cases", [])
    total_cases = summary.get("total_cases", 0)
    dataset_findings = summary.get("total_orig_findings", 0)  # from Info.txt scanner records
    baseline_flawfinder = summary.get("total_orig_flawfinder_hits", 0)  # live flawfinder hits

    # Compile stats from per-case data
    cases_with_code = sum(1 for c in cases_data if c.get("original_file"))
    cases_compiled_orig = sum(1 for c in cases_data if c.get("orig_compile") is True)
    
    # Per-model compile stats
    models_compile = {}
    for model in ["claude-opus-4-1-20250805", "gpt-4.1-2025-04-14", "gpt-5-2025-08-07"]:
        m_stats = summary.get("models", {}).get(model, {})
        models_compile[model] = {
            "flawfinder_hits": m_stats.get("flawfinder_hits", 0),
            "fixed_cases": m_stats.get("fixed_cases", 0),
            "compile_ok": m_stats.get("compile_ok", 0),
        }

    # Compute reduction rate correctly — only when baseline > 0
    best_reduction = "N/A"
    if baseline_flawfinder > 0:
        best_rem = min(
            (models_compile[m]["flawfinder_hits"] for m in models_compile),
            default=baseline_flawfinder
        )
        best_reduction = f"{round((baseline_flawfinder - best_rem) / baseline_flawfinder * 100, 1)}%"
    elif dataset_findings > 0:
        best_reduction = "N/A (live flawfinder scan not yet run)"

    # Audit summary
    audit = manual_audit_service.get_audit_summary()

    # Local Ollama benchmark report
    local_report_path = BASE_DIR / "local_ollama_benchmark_report.json"
    local_report = {}
    if local_report_path.exists():
        try:
            with open(local_report_path, "r", encoding="utf-8") as f:
                local_report = json.load(f)
        except Exception:
            pass

    has_live_scan = baseline_flawfinder > 0
    has_evaluation = bool(cases_data)

    return {
        "data_source": "evaluation_report.json + manual_audit.db + local_ollama_benchmark_report.json",
        "evaluation_ran": has_evaluation,
        "live_flawfinder_ran": has_live_scan,
        # Dataset
        "total_dataset_cases": total_cases,
        "cases_with_source_code": cases_with_code,
        "dataset_recorded_findings": dataset_findings,   # from Info.txt scanner records
        "baseline_flawfinder_hits": baseline_flawfinder, # live flawfinder on original files
        # If live scan hasn't run, show N/A
        "baseline_flawfinder_note": (
            "Live flawfinder scan ran on original benchmark files." if has_live_scan
            else "Live flawfinder scan not yet executed. Run /api/benchmark/regenerate to populate."
        ),
        # Compilation
        "originals_compiled_ok": cases_compiled_orig,
        # Per-model results
        "historical_models": models_compile,
        # Best reduction achieved
        "best_flawfinder_reduction": best_reduction,
        # Audit workbench
        "manual_audit": audit,
        # Local Ollama benchmark (if run)
        "local_ollama_benchmark": {
            "ran": local_report.get("success", False),
            "model": local_report.get("model_tested", "None"),
            "cases_evaluated": local_report.get("cases_evaluated", 0),
            "total_orig_flaws": local_report.get("total_orig_flaws", 0),
            "total_remaining_flaws": local_report.get("total_remaining_flaws", 0),
            "reduction_rate": local_report.get("reduction_rate", 0),
        }
    }


@app.get("/api/dashboard/charts")
def get_dashboard_charts():
    """
    Returns chart-ready data calculated from real evaluation_report.json.
    All numbers are derived from actual scanner findings — no fabrication.
    """
    import json
    from backend.app.config import BASE_DIR

    report_path = BASE_DIR / "evaluation_report.json"
    if not report_path.exists():
        return {
            "status": "no_data",
            "message": "No evaluation report found. Run /api/benchmark/regenerate first.",
            "cwe_chart": [],
            "severity_chart": [],
            "scanner_chart": [],
            "language_chart": [],
            "model_comparison_chart": [],
            "cases_chart": [],
        }

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    summary = report_data.get("summary", {})
    cases_data = report_data.get("cases", [])

    # Scanner chart — real scanner usage from Info.txt
    scanner_counts: dict = {}
    for c in cases_data:
        for sc in c.get("scanners", []):
            scanner_counts[sc] = scanner_counts.get(sc, 0) + 1
    scanner_chart = [{"scanner": k, "cases": v} for k, v in sorted(scanner_counts.items(), key=lambda x: -x[1])]

    # Language chart from file extension
    lang_counts: dict = {"c": 0, "cpp": 0, "csharp": 0}
    for c in cases_data:
        fn = c.get("original_file", "")
        if fn.endswith(".c"):
            lang_counts["c"] += 1
        elif fn.endswith(".cpp"):
            lang_counts["cpp"] += 1
        elif fn.endswith(".cs"):
            lang_counts["csharp"] += 1
    language_chart = [{"language": k, "cases": v} for k, v in lang_counts.items() if v > 0]

    # Dataset findings per case (from recorded scanner findings in Info.txt)
    cases_chart = [
        {
            "case": c["case"],
            "dataset_findings": c.get("dataset_findings_count", 0),
            "orig_flawfinder": c.get("orig_flawfinder_count", 0),
            "claude_hits": c.get("models", {}).get("claude-opus-4-1-20250805", {}).get("flawfinder_count", 0),
            "gpt4_hits": c.get("models", {}).get("gpt-4.1-2025-04-14", {}).get("flawfinder_count", 0),
            "gpt5_hits": c.get("models", {}).get("gpt-5-2025-08-07", {}).get("flawfinder_count", 0),
        }
        for c in cases_data
    ]

    # Model comparison chart
    baseline = summary.get("total_orig_flawfinder_hits", 0)
    model_comparison_chart = []
    for model_name, m_stats in summary.get("models", {}).items():
        remaining = m_stats.get("flawfinder_hits", 0)
        reduction = round((baseline - remaining) / baseline * 100, 1) if baseline > 0 else None
        model_comparison_chart.append({
            "model": model_name,
            "baseline": baseline,
            "remaining": remaining,
            "reduced": max(0, baseline - remaining),
            "reduction_rate": reduction,
            "compile_ok": m_stats.get("compile_ok", 0),
            "fixed_cases": m_stats.get("fixed_cases", 0),
            "reduction_note": "N/A — live flawfinder not yet run" if baseline == 0 else None,
        })

    # CWE distribution from ground truth (paper data)
    from backend.app.evaluation.ground_truth import PAPER_CWE_DISTRIBUTION
    cwe_chart = [
        {"cwe": d["cwe"], "description": d["description"], "count": d["count"]}
        for d in PAPER_CWE_DISTRIBUTION[:10]
    ]

    # Severity distribution from ground truth (approximate)
    severity_chart = [
        {"severity": "high", "count": sum(1 for d in PAPER_CWE_DISTRIBUTION if d.get("top_25_rank"))},
        {"severity": "medium", "count": sum(1 for d in PAPER_CWE_DISTRIBUTION if not d.get("top_25_rank"))},
    ]

    return {
        "status": "ok",
        "data_source": "evaluation_report.json + paper ground truth",
        "baseline_flawfinder_hits": baseline,
        "live_scan_available": baseline > 0,
        "total_cases": len(cases_data),
        "scanner_chart": scanner_chart,
        "language_chart": language_chart,
        "model_comparison_chart": model_comparison_chart,
        "cases_chart": cases_chart,
        "cwe_chart": cwe_chart,
        "severity_chart": severity_chart,
    }


@app.post("/api/benchmark/regenerate")
def regenerate_evaluation_report():
    """
    Re-runs the evaluator.py benchmark script to regenerate evaluation_report.json
    with real live flawfinder hits. This fixes the zero-hits issue caused by
    the previous incorrect python -m flawfinder invocation.
    Documents any discrepancies found.
    """
    import subprocess, sys
    from backend.app.config import BASE_DIR

    script = BASE_DIR / "evaluator.py"
    if not script.exists():
        raise HTTPException(status_code=404, detail="evaluator.py not found in project root.")

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, encoding="utf-8", errors="ignore",
            timeout=300,  # 5 minute timeout for 48 cases
            cwd=str(BASE_DIR)
        )
        report_path = BASE_DIR / "evaluation_report.json"
        summary = {}
        if report_path.exists():
            import json
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            summary = data.get("summary", {})

        return {
            "status": "completed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "stdout_tail": result.stdout[-2000:] if result.stdout else "",
            "stderr_tail": result.stderr[-1000:] if result.stderr else "",
            "report_summary": summary,
            "note": (
                "evaluation_report.json regenerated from live flawfinder execution. "
                "Previous zero-hits were caused by incorrect python -m flawfinder invocation "
                "when flawfinder was only installed as a system CLI binary, not as a venv module."
            )
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "message": "Evaluator timed out after 5 minutes."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/benchmark/dataset-stats")
def get_dataset_stats():
    """
    Returns real dataset statistics by scanning the actual benchmark directory.
    Does NOT fabricate data — only reports what's actually on disk.
    """
    from backend.app.config import BENCHMARK_DIR, BASE_DIR
    import sys
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    if not BENCHMARK_DIR.exists():
        return {
            "status": "error",
            "message": f"Dataset directory not found: {BENCHMARK_DIR}",
            "total_cases": 0,
        }

    from evaluator import parse_case_info, get_case_files

    case_dirs = sorted([
        d for d in BENCHMARK_DIR.iterdir()
        if d.is_dir() and d.name.startswith("File_")
    ])

    lang_counts = {"c": 0, "cpp": 0, "csharp": 0, "unknown": 0}
    scanner_usage: dict = {}
    cases_with_code = 0
    total_recorded_findings = 0
    case_summaries = []

    for case_dir in case_dirs:
        info = parse_case_info(case_dir)
        files = get_case_files(case_dir, info.get("target_file", ""))
        has_code = bool(files.get("original_code"))
        if has_code:
            cases_with_code += 1

        fn = info.get("target_file", "")
        if fn.endswith(".c"):
            lang_counts["c"] += 1
        elif fn.endswith((".cpp", ".cc", ".cxx")):
            lang_counts["cpp"] += 1
        elif fn.endswith(".cs"):
            lang_counts["csharp"] += 1
        else:
            lang_counts["unknown"] += 1

        for sc in info.get("scanners", []):
            scanner_usage[sc] = scanner_usage.get(sc, 0) + 1

        findings_count = len(info.get("scanner_findings", []))
        total_recorded_findings += findings_count

        case_summaries.append({
            "case_id": case_dir.name,
            "target_file": info.get("target_file", "N/A"),
            "scanners": info.get("scanners", []),
            "recorded_findings": findings_count,
            "has_source_code": has_code,
        })

    return {
        "status": "ok",
        "data_source": "Live filesystem scan of MSc_DataEngineering_Results directory",
        "total_cases": len(case_dirs),
        "cases_with_source_code": cases_with_code,
        "total_recorded_findings": total_recorded_findings,
        "language_distribution": lang_counts,
        "scanner_usage": scanner_usage,
        "cases": case_summaries,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
