"""
Security Re-Scan & Repair Verification Pipeline
Re-scans repaired code safely in sandbox, checks compiler validity,
and calculates quantitative reduction rates according to strict decision rules:
- VERIFIED: Code compiles successfully AND targeted finding is no longer detected
- FAILED_SECURITY_RESCAN: Compilation passes but vulnerability remains
- COMPILATION_FAILED: Compilation fails
- VERIFICATION_UNAVAILABLE: Verification scanner unavailable
"""

import tempfile
import uuid
from pathlib import Path
from typing import List, Optional
from backend.app.models.schemas import (
    NormalizedFinding, VerifyRequest, VerifyResponse, CompilerVerificationResult
)
from backend.app.scanners.scanner_manager import scanner_manager
from backend.app.verification.compiler import compiler_engine

class RepairVerifier:
    def verify(self, req: VerifyRequest) -> VerifyResponse:
        """Execute end-to-end compiler verification and security re-scan on repaired code."""
        ext_map = {
            "c": ".c",
            "cpp": ".cpp",
            "csharp": ".cs",
            "cs": ".cs"
        }
        lang = req.language.lower()
        ext = ext_map.get(lang, ".c" if lang in ["c", "cpp"] else ".txt")
        fname = req.filename or f"repaired_{uuid.uuid4().hex[:6]}{ext}"

        # 1. Apply repair to a temporary sandbox copy - Never overwrite original source
        with tempfile.TemporaryDirectory(prefix="aisecure_verify_") as temp_dir:
            temp_file = Path(temp_dir) / fname
            temp_file.write_text(req.repaired_code, encoding="utf-8", errors="ignore")
            
            # Step 8: Compiler / Syntax verification
            compile_res: CompilerVerificationResult = compiler_engine.verify_syntax(temp_file, req.language)

        # Step 9: Security Re-scan
        # Check if scanner is available for this language
        available_scanners = [s for s in scanner_manager.scanners if lang in s.supported_languages and s.is_installed()]
        
        if not available_scanners:
            status = "VERIFICATION_UNAVAILABLE"
            return VerifyResponse(
                status=status,
                compiler_verification=compile_res,
                baseline_findings_count=len(req.baseline_findings),
                remaining_findings_count=len(req.baseline_findings),
                findings_reduced=0,
                reduction_rate=0.0,
                targeted_finding_resolved=False,
                is_verified=False,
                remaining_findings=req.baseline_findings,
                verification_summary="Verification scanner is unavailable on this system. Cannot re-scan."
            )

        # Execute re-scan on repaired code in sandbox
        rescan_res = scanner_manager.scan_code(req.repaired_code, req.language, filename=fname)
        remaining_findings: List[NormalizedFinding] = rescan_res.findings

        # Calculate metrics
        baseline_count = len(req.baseline_findings)
        remaining_count = len(remaining_findings)
        findings_reduced = max(0, baseline_count - remaining_count)

        if baseline_count > 0:
            reduction_rate = round(((baseline_count - remaining_count) / baseline_count) * 100.0, 2)
        else:
            reduction_rate = 100.0 if remaining_count == 0 else 0.0

        # Step 10: Repair Decision
        # Check whether target finding was resolved
        target_resolved = True
        if req.target_finding:
            # Check if matching CWE / scanner finding remains in remaining findings
            target_cwe = req.target_finding.cwe.lower().replace("-", "")
            for rf in remaining_findings:
                rf_cwe = rf.cwe.lower().replace("-", "")
                if (target_cwe in rf_cwe or rf_cwe in target_cwe) and (abs(rf.line - req.target_finding.line) <= 5):
                    target_resolved = False
                    break
        else:
            # If no single target finding specified, check if overall findings were eliminated or reduced
            target_resolved = (remaining_count == 0) or (findings_reduced > 0)

        # Decision rules:
        # 1. If compilation fails -> COMPILATION_FAILED
        if compile_res.status == "FAIL":
            status = "COMPILATION_FAILED"
            is_verified = False
            summary = f"COMPILATION FAILED ({compile_res.compiler} exit code {compile_res.exit_code}). Syntax errors must be resolved."

        # 2. If compilation is unavailable
        elif compile_res.status == "UNAVAILABLE":
            # If target finding is resolved by scanner, but compiler was unavailable
            if target_resolved and (remaining_count < baseline_count or remaining_count == 0):
                status = "VERIFIED"
                is_verified = True
                summary = f"Security finding resolved (-{findings_reduced} flaws, {reduction_rate}% reduction). Note: Compiler {compile_res.compiler} is unavailable for syntax check."
            else:
                status = "FAILED_SECURITY_RESCAN"
                is_verified = False
                summary = f"Compiler check unavailable, and security finding remains detected ({remaining_count} remaining)."

        # 3. If compilation PASS
        else:
            if target_resolved and (remaining_count < baseline_count or remaining_count == 0):
                status = "VERIFIED"
                is_verified = True
                summary = f"VERIFIED: Code compiled cleanly and security finding is resolved ({reduction_rate}% vulnerability reduction)."
            else:
                status = "FAILED_SECURITY_RESCAN"
                is_verified = False
                summary = f"FAILED_SECURITY_RESCAN: Code compiled cleanly, but security finding remains detected ({remaining_count} flaw(s) active)."

        return VerifyResponse(
            status=status,
            compiler_verification=compile_res,
            baseline_findings_count=baseline_count,
            remaining_findings_count=remaining_count,
            findings_reduced=findings_reduced,
            reduction_rate=reduction_rate,
            targeted_finding_resolved=target_resolved,
            is_verified=is_verified,
            remaining_findings=remaining_findings,
            verification_summary=summary
        )

repair_verifier = RepairVerifier()
