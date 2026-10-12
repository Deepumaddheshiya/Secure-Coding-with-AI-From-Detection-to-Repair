"""
AI-SecureCode FastAPI Backend
Main entrypoint providing REST API for scanning, explaining, repairing, verifying,
autonomous retry pipeline, and DevGPT benchmarking.
"""

import sys
import types
from pathlib import Path

# Fix import paths for both root execution and nested/Vercel deployment
_current_file = Path(__file__).resolve()
_backend_dir = _current_file.parent.parent  # directory containing 'app'
_repo_dir = _backend_dir.parent             # root repo directory

for _p in [str(_backend_dir), str(_repo_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Alias 'backend' module in sys.modules if not present (e.g. on Vercel where root is 'backend')
if "backend" not in sys.modules:
    _backend_pkg = types.ModuleType("backend")
    _backend_pkg.__path__ = [str(_backend_dir)]
    sys.modules["backend"] = _backend_pkg

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
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

# Enable CORS for local React/Vite development & Netlify production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://harmonious-sprinkles-e6bc45.netlify.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def normalize_vercel_paths(request, call_next):
    """Normalize paths if Vercel routes request with entrypoint filename prefix."""
    path = request.scope.get("path", "")
    original_path = request.headers.get("x-matched-path") or request.headers.get("x-rewrite-url")
    if original_path and not any(original_path.startswith(p) for p in ["/app/main.py", "/api/index.py"]):
        request.scope["path"] = original_path
    else:
        for prefix in ["/app/main.py", "/app/main", "/api/index.py", "/index.py", "/main.py"]:
            if path.startswith(prefix):
                new_path = path[len(prefix):]
                if not new_path.startswith("/"):
                    new_path = "/" + new_path
                request.scope["path"] = new_path
                break
    return await call_next(request)



@app.get("/")
@app.get("/api")
@app.get("/api/")
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
    total_cases = summary.get("total_cases", 48)
    baseline_findings = summary.get("total_orig_findings", 72)

    # Calculate model metrics based on real dataset execution results
    models_stats = {}
    for model_name, m_data in summary.get("models", {}).items():
        fixed = m_data.get("fixed_cases", 0)
        remaining_hits = m_data.get("flawfinder_hits", 0)
        compile_ok = m_data.get("compile_ok", 0)
        reduction_rate = round(max(0, baseline_findings - remaining_hits) / baseline_findings * 100, 2) if baseline_findings > 0 else 0.0
        
        models_stats[model_name] = {
            "fixed_cases": fixed,
            "total_cases": total_cases,
            "repair_success_rate": compute_repair_rate(fixed, total_cases),
            "compilation_success_rate": round(compile_ok / total_cases * 100, 2) if total_cases > 0 else 0.0,
            "remaining_hits": remaining_hits,
            "reduction_rate": reduction_rate
        }

    return {
        "status": "computed_from_local_dataset_records",
        "dataset_cases": total_cases,
        "baseline_recorded_findings": baseline_findings,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
