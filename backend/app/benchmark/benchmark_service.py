"""
Benchmark Service for AI-SecureCode
Bridges the Historical DevGPT Benchmark (48 Cases) and Local Ollama Benchmark Execution.
Loads real DevGPT source files, scanner findings, and metadata.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.config import BENCHMARK_DIR, BASE_DIR
from backend.app.ollama.client import ollama_client
from backend.app.scanners.scanner_manager import scanner_manager
from backend.app.models.schemas import NormalizedFinding

REPORT_JSON = BASE_DIR / "evaluation_report.json"
LOCAL_BENCHMARK_REPORT = BASE_DIR / "local_ollama_benchmark_report.json"

HISTORICAL_MODELS = [
    "gpt-5-2025-08-07",
    "gpt-4.1-2025-04-14",
    "claude-opus-4-1-20250805"
]

class BenchmarkService:
    def get_historical_report(self) -> Dict[str, Any]:
        """Load the pre-computed historical benchmark evaluation report (48 DevGPT cases)."""
        if REPORT_JSON.exists():
            try:
                with open(REPORT_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["type"] = "HISTORICAL_LLM_BENCHMARK"
                    data["note"] = (
                        "Historical benchmark evaluating Claude Opus 4.1, GPT-4.1, and GPT-5 "
                        "on 48 DevGPT vulnerability samples with 74 baseline live flaws."
                    )
                    return data
            except Exception:
                pass
        return {"summary": {}, "cases": [], "type": "HISTORICAL_LLM_BENCHMARK"}

    def get_all_cases(self) -> List[Dict[str, Any]]:
        """List all 48 real DevGPT test cases with real metadata from the dataset directory."""
        if not BENCHMARK_DIR.exists():
            return []

        from evaluator import parse_case_info, get_case_files

        cases_list = []
        case_dirs = sorted([d for d in os.listdir(BENCHMARK_DIR) if (BENCHMARK_DIR / d).is_dir() and d.startswith("File_")])

        for c_name in case_dirs:
            case_dir = BENCHMARK_DIR / c_name
            info = parse_case_info(case_dir)
            files = get_case_files(case_dir, info.get("target_file", ""))
            
            target_file = files.get("original_filename") or info.get("target_file") or "source.c"
            ext = Path(target_file).suffix.lower()
            lang = "cpp" if ext in [".cpp", ".cc", ".cxx"] else ("csharp" if ext in [".cs"] else "c")

            # Extract primary CWE
            findings = info.get("scanner_findings", [])
            primary_cwe = "CWE-Security"
            for f in findings:
                text = str(f.get("text", "")).upper()
                cwe_match = re.search(r"CWE-\d+", text)
                if cwe_match:
                    primary_cwe = cwe_match.group(0)
                    break

            cases_list.append({
                "case_id": c_name,
                "target_file": target_file,
                "language": lang,
                "scanners": info.get("scanners", ["flawfinder"]),
                "recorded_findings_count": len(findings),
                "primary_cwe": primary_cwe,
                "has_code": bool(files.get("original_code")),
                "models_available": list(files.get("models", {}).keys())
            })

        return cases_list

    def get_case_detail(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full original source code, normalized findings, and comparisons for a benchmark case."""
        case_dir = BENCHMARK_DIR / case_id
        if not case_dir.exists():
            return None

        from evaluator import parse_case_info, get_case_files, run_flawfinder_on_code
        info = parse_case_info(case_dir)
        files = get_case_files(case_dir, info.get("target_file", ""))

        def read_file(p):
            if p and os.path.exists(p):
                try:
                    return Path(p).read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    pass
            return ""

        orig_code = read_file(files["original_code"])
        target_file = files.get("original_filename") or info.get("target_file") or "Code_001.c"
        ext = Path(target_file).suffix.lower()
        lang = "cpp" if ext in [".cpp", ".cc", ".cxx"] else ("csharp" if ext in [".cs"] else "c")

        # Convert recorded scanner findings to NormalizedFinding
        normalized_findings: List[Dict[str, Any]] = []
        recorded_findings = info.get("scanner_findings", [])

        code_lines = orig_code.splitlines() if orig_code else []

        for idx, rf in enumerate(recorded_findings):
            line_no = int(rf.get("line", 1)) if str(rf.get("line", "")).isdigit() else 1
            scanner = rf.get("scanner", "static_scanner")
            text = rf.get("text", "")
            rf_type = rf.get("type", "SecurityWarning")
            sev = rf.get("severity", "medium").lower()
            if sev in ["note", "info"]:
                sev = "low"
            elif sev in ["warning"]:
                sev = "medium"
            elif sev in ["error", "critical"]:
                sev = "high"

            cwe = "CWE-General"
            cwe_match = re.search(r"CWE-\d+", text)
            if cwe_match:
                cwe = cwe_match.group(0)
            elif "strtok" in text.lower():
                cwe = "CWE-20"
            elif "buffer" in text.lower() or "overflow" in text.lower():
                cwe = "CWE-120"
            elif "printf" in text.lower() or "format" in text.lower():
                cwe = "CWE-134"

            # Snippet extraction
            snippet = rf.get("source_code", "")
            if not snippet and code_lines:
                target_idx = max(0, min(line_no - 1, len(code_lines) - 1))
                s_start = max(0, target_idx - 2)
                s_end = min(len(code_lines), target_idx + 3)
                snippet_lines = []
                for s_i in range(s_start, s_end):
                    p = "-> " if s_i == target_idx else "   "
                    snippet_lines.append(f"{p}{s_i + 1:4d} | {code_lines[s_i]}")
                snippet = "\n".join(snippet_lines)

            normalized_findings.append({
                "id": f"DEVGPT-{case_id}-{idx + 1}",
                "file": target_file,
                "line": line_no,
                "column": 0,
                "scanner": scanner,
                "rule": rf_type,
                "cwe": cwe,
                "severity": sev,
                "title": f"DevGPT Finding: {rf_type}",
                "description": text,
                "code_snippet": snippet
            })

        # Run live local scanner (flawfinder) on original code to get live hits
        live_scan = scanner_manager.scan_code(orig_code, lang, filename=target_file)
        live_findings = [f.model_dump() for f in live_scan.findings]

        # Combine or fallback
        all_findings = live_findings if live_findings else normalized_findings

        claude_code = read_file(files["models"]["claude-opus-4-1-20250805"]["code_path"])
        gpt4_code = read_file(files["models"]["gpt-4.1-2025-04-14"]["code_path"])
        gpt5_code = read_file(files["models"]["gpt-5-2025-08-07"]["code_path"])

        orig_hits = run_flawfinder_on_code(files["original_code"])
        claude_hits = run_flawfinder_on_code(files["models"]["claude-opus-4-1-20250805"]["code_path"])
        gpt4_hits = run_flawfinder_on_code(files["models"]["gpt-4.1-2025-04-14"]["code_path"])
        gpt5_hits = run_flawfinder_on_code(files["models"]["gpt-5-2025-08-07"]["code_path"])

        return {
            "case_id": case_id,
            "target_file": target_file,
            "language": lang,
            "scanners": info.get("scanners", []),
            "dataset_findings": normalized_findings,
            "live_findings": live_findings,
            "findings": all_findings,
            "original_code": orig_code,
            "orig_flawfinder_hits": orig_hits,
            "historical_repairs": {
                "claude-opus-4-1-20250805": {
                    "code": claude_code,
                    "flawfinder_hits": claude_hits,
                    "reduction": max(0, len(orig_hits) - len(claude_hits))
                },
                "gpt-4.1-2025-04-14": {
                    "code": gpt4_code,
                    "flawfinder_hits": gpt4_hits,
                    "reduction": max(0, len(orig_hits) - len(gpt4_hits))
                },
                "gpt-5-2025-08-07": {
                    "code": gpt5_code,
                    "flawfinder_hits": gpt5_hits,
                    "reduction": max(0, len(orig_hits) - len(gpt5_hits))
                }
            }
        }

    def run_local_model_benchmark(self, model_name: str, limit_cases: int = 5) -> Dict[str, Any]:
        """Run benchmark using local Ollama model on a subset of test cases and compare."""
        if not ollama_client.is_running():
            return {
                "success": False,
                "error": "Local Ollama is offline. Start Ollama and load a coding model to run Local Benchmark."
            }

        cases = sorted([d for d in os.listdir(BENCHMARK_DIR) if (BENCHMARK_DIR / d).is_dir() and d.startswith("File_")])[:limit_cases]
        from evaluator import parse_case_info, get_case_files, run_flawfinder_on_code
        from backend.app.ollama.repairer import ai_repairer

        results = []
        total_orig_flaws = 0
        total_local_flaws = 0

        for c_name in cases:
            case_dir = BENCHMARK_DIR / c_name
            info = parse_case_info(case_dir)
            files = get_case_files(case_dir, info.get("target_file", ""))
            
            orig_path = files["original_code"]
            if not orig_path or not os.path.exists(orig_path):
                continue

            orig_code = Path(orig_path).read_text(encoding="utf-8", errors="ignore")
            orig_hits = run_flawfinder_on_code(orig_path)
            total_orig_flaws += len(orig_hits)

            ext = Path(orig_path).suffix.lower()
            lang = "cpp" if ext in [".cpp", ".cc", ".cxx"] else ("csharp" if ext in [".cs"] else "c")

            norm_findings = scanner_manager.scan_code(orig_code, lang).findings
            
            rep_res = ai_repairer.repair(
                code=orig_code,
                language=lang,
                findings=norm_findings,
                model_name=model_name
            )

            rep_hits = scanner_manager.scan_code(rep_res.repaired_code, lang).findings
            total_local_flaws += len(rep_hits)

            results.append({
                "case": c_name,
                "file": files["original_filename"],
                "orig_flaws": len(orig_hits),
                "repaired_flaws": len(rep_hits),
                "reduced": max(0, len(orig_hits) - len(rep_hits)),
                "model_used": model_name
            })

        overall_reduction = round(((total_orig_flaws - total_local_flaws) / total_orig_flaws) * 100, 2) if total_orig_flaws > 0 else 0

        res_payload = {
            "success": True,
            "type": "LOCAL_LLM_BENCHMARK",
            "model_tested": model_name,
            "cases_evaluated": len(results),
            "total_orig_flaws": total_orig_flaws,
            "total_remaining_flaws": total_local_flaws,
            "flaws_reduced": total_orig_flaws - total_local_flaws,
            "reduction_rate": overall_reduction,
            "case_details": results
        }

        with open(LOCAL_BENCHMARK_REPORT, "w", encoding="utf-8") as f:
            json.dump(res_payload, f, indent=2)

        return res_payload

benchmark_service = BenchmarkService()
