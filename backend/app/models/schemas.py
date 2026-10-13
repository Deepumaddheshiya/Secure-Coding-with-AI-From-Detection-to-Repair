"""
AI-SecureCode Pydantic Data Models & Schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class NormalizedFinding(BaseModel):
    """
    Normalized finding representation complying strictly with project standard:
    {
        "file": "",
        "line": 0,
        "column": 0,
        "scanner": "",
        "rule": "",
        "cwe": "",
        "severity": "",
        "title": "",
        "description": "",
        "code_snippet": ""
    }
    """
    id: str = ""
    file: str
    line: int
    column: int = 0
    scanner: str
    rule: str
    cwe: str
    severity: str
    title: str = ""
    description: str
    code_snippet: str = ""

class ScannerStatus(BaseModel):
    name: str
    installed: bool
    version: Optional[str] = None
    supported_languages: List[str] = []
    status_message: Optional[str] = None

class CompilerStatus(BaseModel):
    language: str
    tool_name: str
    installed: bool
    version: Optional[str] = None

class ScanRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None
    enabled_scanners: Optional[List[str]] = None

class ScanResponse(BaseModel):
    filename: str
    language: str
    total_findings: int
    scanners_executed: List[str]
    scanners_unavailable: List[str]
    findings: List[NormalizedFinding]

class StructuredAIOutput(BaseModel):
    """Structured AI output format required from local Ollama model."""
    analysis: str = ""
    root_cause: str = ""
    security_impact: str = ""
    cwe: str = ""
    severity: str = ""
    repair_strategy: str = ""
    repaired_code: str = ""
    changes: List[str] = []

class AIExplainRequest(BaseModel):
    code: str
    language: str
    finding: NormalizedFinding
    model_name: Optional[str] = None

class AIExplainResponse(BaseModel):
    vulnerability_explanation: str
    root_cause: str
    security_impact: str
    recommendation: str
    cwe: Optional[str] = None
    model_used: Optional[str] = None

class AIRepairRequest(BaseModel):
    code: str
    language: str
    findings: List[NormalizedFinding] = []
    target_finding: Optional[NormalizedFinding] = None
    model_name: Optional[str] = None
    instructions: Optional[str] = None

class AIRepairResponse(BaseModel):
    model_used: str
    structured_output: Optional[StructuredAIOutput] = None
    repaired_code: str
    changes: List[str] = []
    explanation_of_modifications: str = ""
    is_repaired: bool = True

class CompilerVerificationResult(BaseModel):
    language: str = ""
    compiler: str = "unknown"
    compiled: Optional[bool] = None
    status: str
    exit_code: int
    output: str

class VerifyRequest(BaseModel):
    original_code: str
    repaired_code: str
    language: str
    filename: Optional[str] = None
    baseline_findings: List[NormalizedFinding] = []
    target_finding: Optional[NormalizedFinding] = None

class VerifyResponse(BaseModel):
    status: str
    compiler_verification: CompilerVerificationResult
    baseline_findings_count: int
    remaining_findings_count: int
    findings_reduced: int
    reduction_rate: float
    targeted_finding_resolved: bool
    is_verified: bool = False
    remaining_findings: List[NormalizedFinding] = []
    verification_summary: str = ""

class RepairAttemptInfo(BaseModel):
    """Records each attempt in the AI Retry Loop (Attempts 1 to 3)."""
    attempt: int
    status: str = ""
    model: Optional[str] = None
    ai_output: Optional[StructuredAIOutput] = None
    repaired_code: str = ""
    compiler: str
    compiler_exit_code: int
    compiler_output: str
    baseline_findings_count: int = 0
    remaining_findings_count: int = 0
    findings_reduced: int = 0
    reduction_rate: float
    targeted_finding_resolved: bool
    remaining_findings: List[NormalizedFinding] = []
    feedback_to_ai: Optional[str] = None

class PipelineRepairRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None
    target_finding: Optional[NormalizedFinding] = None
    all_findings: Optional[List[NormalizedFinding]] = None
    model_name: Optional[str] = None
    max_attempts: int = 3

class PipelineRepairResponse(BaseModel):
    case_id: Optional[str] = None
    filename: str
    language: str
    original_code: str
    final_repaired_code: str
    final_status: str
    total_attempts: int
    attempts: List[RepairAttemptInfo]
    baseline_findings: List[NormalizedFinding] = []
    final_remaining_findings: List[NormalizedFinding] = []
    is_verified: bool
    model_used: str
    summary: str

class OllamaModelInfo(BaseModel):
    name: str
    size: Optional[int] = None
    modified_at: Optional[str] = None
    parameter_size: Optional[str] = None

class SystemHealthResponse(BaseModel):
    status: str
    ollama_running: bool
    ollama_url: str
    installed_models: List[str]
    active_model: Optional[str] = None
    scanners: List[ScannerStatus]
    compilers: List[CompilerStatus]
