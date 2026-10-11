"""
Autonomous AI Secure Code Repair Pipeline with Verification & Retry Loop
Implements the full end-to-end loop:
REAL DevGPT DATASET -> SOURCE FILE -> STATIC SCANNERS -> FINDING -> LOCAL AI AGENT
  -> Analyze Vulnerability -> Generate Secure Repair -> Apply to Sandbox Copy
  -> Compile / Syntax Check (gcc/g++/csc) -> Security Re-scan
  -> Is Security Finding Resolved?
     YES -> VERIFIED -> Final Report
     NO  -> AGENT RETRY (Re-analyze + feedback) -> Attempt 2 -> Attempt 3 -> REPAIR_FAILED
Maximum retry attempts: 3.
Stores every repair attempt.
"""

from typing import List, Optional, Dict, Any
from backend.app.models.schemas import (
    NormalizedFinding,
    PipelineRepairRequest,
    PipelineRepairResponse,
    RepairAttemptInfo,
    VerifyRequest,
    VerifyResponse
)
from backend.app.ollama.repairer import ai_repairer
from backend.app.ollama.client import ollama_client
from backend.app.verification.verifier import repair_verifier
from backend.app.scanners.scanner_manager import scanner_manager

class RepairPipeline:
    def execute_pipeline(self, req: PipelineRepairRequest) -> PipelineRepairResponse:
        """
        Execute the autonomous repair and verification pipeline with iterative retry loop.
        Never overwrites original code. Max 3 attempts.
        """
        code = req.code
        lang = req.language.lower()
        fname = req.filename or f"source.{lang}"
        max_attempts = min(max(1, req.max_attempts), 3)

        # 1. Establish baseline findings if not already provided
        baseline_findings: List[NormalizedFinding] = req.all_findings or []
        if not baseline_findings:
            scan_res = scanner_manager.scan_code(code, lang, filename=fname)
            baseline_findings = scan_res.findings

        # Target finding to resolve
        target_finding = req.target_finding or (baseline_findings[0] if baseline_findings else None)

        # Check local Ollama readiness
        if not ollama_client.is_running():
            return PipelineRepairResponse(
                filename=fname,
                language=lang,
                original_code=code,
                final_repaired_code=code,
                final_status="OLLAMA_OFFLINE",
                total_attempts=0,
                attempts=[],
                baseline_findings=baseline_findings,
                final_remaining_findings=baseline_findings,
                is_verified=False,
                model_used="None",
                summary=(
                    "Local AI is offline. Start Ollama locally ('ollama serve' or start Ollama app) "
                    "with a local model (e.g. 'ollama pull qwen2.5-coder') and try again. Zero cloud APIs used."
                )
            )

        target_model = req.model_name or ollama_client.get_best_model() or "qwen2.5-coder"

        attempts: List[RepairAttemptInfo] = []
        current_code = code
        previous_repaired_code = ""
        previous_explanation = ""
        compiler_feedback = ""
        rescan_feedback = ""
        final_repaired_code = code
        final_status = "REPAIR_FAILED"
        final_remaining_findings = baseline_findings
        is_verified = False

        for attempt_idx in range(1, max_attempts + 1):
            retry_context = None
            if attempt_idx > 1:
                retry_context = {
                    "attempt": attempt_idx,
                    "previous_repaired_code": previous_repaired_code,
                    "compiler_output": compiler_feedback,
                    "remaining_findings": rescan_feedback,
                    "previous_explanation": previous_explanation
                }

            # STEP 1 to 9: Local AI Agent generates structured repair
            repair_res = ai_repairer.repair(
                code=code,
                language=lang,
                findings=baseline_findings,
                target_finding=target_finding,
                model_name=target_model,
                retry_context=retry_context
            )

            current_repaired_code = repair_res.repaired_code
            previous_repaired_code = current_repaired_code
            previous_explanation = repair_res.explanation_of_modifications
            final_repaired_code = current_repaired_code

            # STEP 8 & 9: Compile/Syntax Check and Security Re-scan in safe sandbox
            verify_res: VerifyResponse = repair_verifier.verify(VerifyRequest(
                original_code=code,
                repaired_code=current_repaired_code,
                language=lang,
                filename=fname,
                baseline_findings=baseline_findings,
                target_finding=target_finding
            ))

            final_remaining_findings = verify_res.remaining_findings

            # Check if targeted finding is eliminated
            target_resolved = False
            if target_finding:
                target_cwe_clean = target_finding.cwe.lower().replace("-", "")
                finding_still_present = any(
                    (target_cwe_clean in rf.cwe.lower().replace("-", "") or rf.cwe.lower().replace("-", "") in target_cwe_clean)
                    and abs(rf.line - target_finding.line) <= 5
                    for rf in verify_res.remaining_findings
                )
                target_resolved = not finding_still_present
            else:
                target_resolved = verify_res.findings_reduced > 0 or len(verify_res.remaining_findings) == 0

            # Record this attempt
            attempt_info = RepairAttemptInfo(
                attempt=attempt_idx,
                status=verify_res.status,
                compiler=verify_res.compiler_verification.status,
                compiler_exit_code=verify_res.compiler_verification.exit_code,
                compiler_output=verify_res.compiler_verification.output,
                baseline_findings_count=verify_res.baseline_findings_count,
                remaining_findings_count=verify_res.remaining_findings_count,
                findings_reduced=verify_res.findings_reduced,
                reduction_rate=verify_res.reduction_rate,
                targeted_finding_resolved=target_resolved,
                ai_output=repair_res.structured_output,
                repaired_code=current_repaired_code,
                feedback_to_ai=(
                    f"Compiler status: {verify_res.compiler_verification.status}. "
                    f"Remaining findings: {verify_res.remaining_findings_count}. "
                    f"Target finding resolved: {target_resolved}"
                ) if attempt_idx < max_attempts and verify_res.status != "VERIFIED" else None
            )
            attempts.append(attempt_info)

            # STEP 10: Repair Decision
            if verify_res.status == "VERIFIED":
                final_status = "VERIFIED"
                is_verified = True
                break

            # If not verified, prepare feedback for next retry attempt
            compiler_feedback = verify_res.compiler_verification.output if verify_res.compiler_verification.status != "PASS" else "Compiler: PASS (No syntax errors)"
            remaining_descriptions = [f"Line {rf.line} [{rf.cwe}]: {rf.description}" for rf in verify_res.remaining_findings[:5]]
            rescan_feedback = "\n".join(remaining_descriptions) if remaining_descriptions else "Target vulnerability not resolved."

        # If after max_attempts not verified
        if not is_verified:
            # If last attempt was compilation failure
            if attempts and attempts[-1].compiler == "FAIL":
                final_status = "COMPILATION_FAILED"
            elif attempts and attempts[-1].status == "VERIFICATION_UNAVAILABLE":
                final_status = "VERIFICATION_UNAVAILABLE"
            else:
                final_status = "REPAIR_FAILED"

        summary_msg = (
            f"Pipeline completed with status {final_status} in {len(attempts)} attempt(s). "
            f"Vulnerabilities reduced from {len(baseline_findings)} to {len(final_remaining_findings)}."
        )

        return PipelineRepairResponse(
            filename=fname,
            language=lang,
            original_code=code,
            final_repaired_code=final_repaired_code,
            final_status=final_status,
            total_attempts=len(attempts),
            attempts=attempts,
            baseline_findings=baseline_findings,
            final_remaining_findings=final_remaining_findings,
            is_verified=is_verified,
            model_used=target_model,
            summary=summary_msg
        )

repair_pipeline = RepairPipeline()
