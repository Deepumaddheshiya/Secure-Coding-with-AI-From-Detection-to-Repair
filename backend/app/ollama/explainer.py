"""
Local AI Security Explanation Engine
Queries local Ollama to explain vulnerabilities, root causes, impacts, and recommendations.
"""

import json
import re
from typing import Dict, Any, Optional
from backend.app.ollama.client import ollama_client
from backend.app.models.schemas import NormalizedFinding, AIExplainResponse

class AIExplainer:
    def explain(self, code: str, language: str, finding: NormalizedFinding, model_name: Optional[str] = None) -> AIExplainResponse:
        """Generate structured vulnerability explanation using local Ollama."""
        target_model = model_name or ollama_client.get_best_model()

        # If Ollama is unavailable, return structured deterministic rule explanation
        if not ollama_client.is_running() or not target_model:
            return AIExplainResponse(
                vulnerability_explanation=f"Finding '{finding.title}' detected by scanner {finding.scanner} on line {finding.line}. {finding.description}",
                root_cause=f"Insecure construct or function call '{finding.rule}' identified in {language.upper()} source code.",
                security_impact=f"Potential violation classified under {finding.cwe}. Severity rated as {finding.severity.upper()}.",
                recommendation=f"Replace '{finding.rule}' with safe alternatives, enforce strict bounds and input validation.",
                cwe=finding.cwe,
                model_used="Deterministic Static Rule Engine (Local AI Offline)"
            )

        system_prompt = (
            "You are an expert Application Security and Secure Coding specialist. "
            "Analyze the given vulnerability finding and code snippet. "
            "You must return ONLY a valid JSON object with the following exact keys:\n"
            "{\n"
            '  "vulnerability_explanation": "...",\n'
            '  "root_cause": "...",\n'
            '  "security_impact": "...",\n'
            '  "recommendation": "...",\n'
            '  "cwe": "..."\n'
            "}"
        )

        user_prompt = (
            f"Programming Language: {language}\n"
            f"Vulnerability Finding: {finding.title}\n"
            f"Scanner: {finding.scanner}\n"
            f"Rule: {finding.rule}\n"
            f"CWE: {finding.cwe}\n"
            f"Line Number: {finding.line}\n"
            f"Code Snippet:\n```\n{finding.code_snippet or code[:400]}\n```\n\n"
            f"Full Source Context:\n```\n{code[:1200]}\n```\n\n"
            "Provide your security analysis in the requested JSON format."
        )

        gen_result = ollama_client.generate(prompt=user_prompt, model=target_model, system_prompt=system_prompt)
        if not gen_result.get("success"):
            return AIExplainResponse(
                vulnerability_explanation=f"Local AI Error: {gen_result.get('error')}. Scanner detail: {finding.description}",
                root_cause=f"Triggered by rule {finding.rule} at line {finding.line}.",
                security_impact=f"Classified under {finding.cwe} ({finding.severity}).",
                recommendation="Review the flagged code and apply bounds-checked APIs.",
                cwe=finding.cwe,
                model_used=target_model or "Local AI Unavailable"
            )

        raw_resp = gen_result.get("response", "")
        # Parse JSON from response
        try:
            # Strip markdown code blocks if present
            cleaned = re.sub(r"^```json\s*", "", raw_resp, flags=re.MULTILINE)
            cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE).strip()
            # Find outermost JSON object
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return AIExplainResponse(
                    vulnerability_explanation=data.get("vulnerability_explanation", finding.description),
                    root_cause=data.get("root_cause", f"Vulnerable construct '{finding.rule}' at line {finding.line}"),
                    security_impact=data.get("security_impact", f"Risk categorized as {finding.cwe}"),
                    recommendation=data.get("recommendation", "Replace with safe APIs."),
                    cwe=data.get("cwe", finding.cwe),
                    model_used=gen_result.get("model", target_model)
                )
        except Exception:
            pass

        # Fallback if model output was not valid JSON
        return AIExplainResponse(
            vulnerability_explanation=raw_resp[:600],
            root_cause=f"Triggered by {finding.rule} at line {finding.line}",
            security_impact=f"Potential exploit via {finding.cwe}",
            recommendation="Apply safe library functions and parameter validation.",
            cwe=finding.cwe,
            model_used=gen_result.get("model", target_model)
        )

ai_explainer = AIExplainer()
