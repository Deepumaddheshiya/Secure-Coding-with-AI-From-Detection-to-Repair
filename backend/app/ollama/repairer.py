"""
Local AI Secure Code Repair Engine
Directs local Ollama coding models to generate minimal, functionality-preserving secure repairs.
Enforces:
- Structured JSON output:
  {
      "analysis": "",
      "root_cause": "",
      "security_impact": "",
      "cwe": "",
      "severity": "",
      "repair_strategy": "",
      "repaired_code": "",
      "changes": []
  }
- Safe JSON validation & robust fallback parsing
- Steps 1-9 agent reasoning
- Support for Retry Loop feedback (compiler errors & scanner re-scan findings)
"""

import json
import re
from typing import List, Optional, Dict, Any
from backend.app.ollama.client import ollama_client
from backend.app.models.schemas import (
    NormalizedFinding, AIRepairResponse, StructuredAIOutput
)

class AIRepairer:
    def repair(
        self,
        code: str,
        language: str,
        findings: List[NormalizedFinding],
        target_finding: Optional[NormalizedFinding] = None,
        model_name: Optional[str] = None,
        instructions: Optional[str] = None,
        retry_context: Optional[Dict[str, Any]] = None
    ) -> AIRepairResponse:
        """
        Generate structured secure repair using local Ollama model.
        Supports initial repair as well as iterative retries with compiler/scanner feedback.
        """
        target_model = model_name or ollama_client.get_best_model()

        if not ollama_client.is_running() or not target_model:
            return AIRepairResponse(
                original_code=code,
                repaired_code=code,
                explanation_of_modifications=(
                    "Local Ollama is offline or no model is installed. "
                    "Please start Ollama ('ollama serve' or open the Ollama app) "
                    "and pull a coding model (e.g., 'ollama pull qwen2.5-coder' or 'ollama pull deepseek-coder')."
                ),
                model_used="None (Local Ollama Offline)",
                is_repaired=False,
                structured_output=StructuredAIOutput(
                    analysis="Local Ollama is offline. No local AI model could be reached.",
                    root_cause="Ollama daemon not running on http://localhost:11434.",
                    security_impact="Unable to synthesize automated AI repair without local LLM.",
                    cwe=target_finding.cwe if target_finding else "Unknown",
                    severity=target_finding.severity if target_finding else "Unknown",
                    repair_strategy="Start Ollama service locally and retry.",
                    repaired_code=code,
                    changes=[]
                )
            )

        # 1. Format findings and target finding
        tf = target_finding or (findings[0] if findings else None)
        target_cwe = tf.cwe if tf else "CWE-General"
        target_sev = tf.severity if tf else "Medium"
        target_line = tf.line if tf else 0
        target_scanner = tf.scanner if tf else "Static Scanner"
        target_desc = tf.description if tf else "Vulnerability detected in code."
        target_code = tf.code_snippet if tf else ""

        all_findings_summary = "\n".join([
            f"- Line {f.line} [{f.scanner}]: {f.cwe} ({f.severity}) -> {f.description}"
            for f in findings[:6]
        ])

        # 2. System prompt enforcing Steps 1-9 and strict JSON output
        system_prompt = (
            "You are an expert secure coding assistant. You analyze security vulnerabilities and generate "
            "minimal, safe, functionality-preserving source code repairs.\n\n"
            "MANDATORY RESPONSIBILITIES:\n"
            "STEP 1: Understand the vulnerable source code.\n"
            "STEP 2: Understand the scanner finding.\n"
            "STEP 3: Understand CWE and severity.\n"
            "STEP 4: Identify the root cause.\n"
            "STEP 5: Determine the security impact.\n"
            "STEP 6: Generate the smallest safe repair.\n"
            "STEP 7: Preserve the original functionality exactly.\n"
            "STEP 8: Return repaired source code that compiles cleanly.\n"
            "STEP 9: Explain exactly what was changed.\n\n"
            "STRICT RULES:\n"
            "1. Output MUST be ONLY a single valid JSON object matching the schema below. No markdown text outside JSON.\n"
            "2. Do NOT truncate or abbreviate the repaired_code. Output the COMPLETE runnable source code.\n"
            "3. Do NOT claim the vulnerability is fixed; verification is performed externally by compilers and scanners.\n"
            "4. Follow this JSON schema exactly:\n"
            "{\n"
            '  "analysis": "Brief analysis of the vulnerable source code and finding",\n'
            '  "root_cause": "Specific underlying technical root cause of the flaw",\n'
            '  "security_impact": "Potential exploit impact (e.g., buffer overflow, memory corruption, crash)",\n'
            '  "cwe": "' + target_cwe + '",\n'
            '  "severity": "' + target_sev + '",\n'
            '  "repair_strategy": "Concrete strategy used to patch the flaw with smallest safe change",\n'
            '  "repaired_code": "Complete, valid repaired source code preserving original behavior",\n'
            '  "changes": ["List of specific modifications applied"]\n'
            "}"
        )

        # 3. Build user prompt (including retry feedback if applicable)
        user_prompt_parts = [
            f"Programming Language: {language.upper()}",
            f"Target Vulnerability:\n- CWE: {target_cwe}\n- Severity: {target_sev}\n- Line: {target_line}\n- Scanner: {target_scanner}\n- Description: {target_desc}",
        ]
        if target_code:
            user_prompt_parts.append(f"Vulnerable Code Snippet / Context:\n{target_code}")

        if all_findings_summary:
            user_prompt_parts.append(f"All Reported Findings:\n{all_findings_summary}")

        user_prompt_parts.append(f"Original Source Code:\n```{language.lower()}\n{code}\n```")

        # Retry context injection
        if retry_context:
            attempt_num = retry_context.get("attempt", 2)
            prev_code = retry_context.get("previous_repaired_code", "")
            comp_out = retry_context.get("compiler_output", "")
            rem_findings = retry_context.get("remaining_findings", "")
            prev_expl = retry_context.get("previous_explanation", "")

            user_prompt_parts.append(
                f"\n=== AGENT RETRY FEEDBACK (Attempt #{attempt_num}) ===\n"
                f"Your previous repair did NOT pass verification. Please re-analyze and correct the flaws:\n"
            )
            if comp_out:
                user_prompt_parts.append(f"COMPILER / SYNTAX ERROR OUTPUT:\n{comp_out}\n")
            if rem_findings:
                user_prompt_parts.append(f"SECURITY RE-SCAN REMAINING FINDINGS:\n{rem_findings}\n")
            if prev_expl:
                user_prompt_parts.append(f"Previous Repair Explanation:\n{prev_expl}\n")
            if prev_code:
                user_prompt_parts.append(f"Previous Repaired Code Attempt:\n```{language.lower()}\n{prev_code}\n```\n")
            user_prompt_parts.append("Generate a NEW, corrected repair addressing these specific errors while preserving original functionality.")

        if instructions:
            user_prompt_parts.append(f"Additional Instructions: {instructions}")

        user_prompt_parts.append("Return the complete repair strictly as the requested JSON object.")
        user_prompt = "\n\n".join(user_prompt_parts)

        # 4. Invoke local Ollama
        gen_result = ollama_client.generate(prompt=user_prompt, model=target_model, system_prompt=system_prompt)
        if not gen_result.get("success"):
            return AIRepairResponse(
                original_code=code,
                repaired_code=code,
                explanation_of_modifications=f"Local AI Error: {gen_result.get('error')}",
                model_used=target_model,
                is_repaired=False,
                structured_output=StructuredAIOutput(
                    analysis=f"Ollama execution failed: {gen_result.get('error')}",
                    root_cause=target_desc,
                    security_impact="Execution halted due to local AI model error.",
                    cwe=target_cwe,
                    severity=target_sev,
                    repair_strategy="Retry after verifying Ollama status.",
                    repaired_code=code,
                    changes=[]
                )
            )

        raw_response = gen_result.get("response", "").strip()

        # 5. Safe validation & parsing of structured output
        structured = self._parse_structured_output(raw_response, code, target_cwe, target_sev)

        return AIRepairResponse(
            original_code=code,
            repaired_code=structured.repaired_code,
            explanation_of_modifications=structured.repair_strategy or "; ".join(structured.changes) or structured.analysis,
            model_used=gen_result.get("model", target_model),
            is_repaired=True,
            structured_output=structured
        )

    def _parse_structured_output(
        self,
        raw_text: str,
        fallback_code: str,
        fallback_cwe: str,
        fallback_sev: str
    ) -> StructuredAIOutput:
        """
        Robust JSON extractor and validator.
        Handles markdown json fences, leading/trailing prose, and malformed strings.
        """
        # Step A: Attempt direct JSON load or fence extraction
        candidate_json = raw_text.strip()
        if "```json" in candidate_json:
            match = re.search(r"```json\s*(.*?)\s*```", candidate_json, re.DOTALL)
            if match:
                candidate_json = match.group(1).strip()
        elif "```" in candidate_json:
            match = re.search(r"```\s*(?:\{.*?\})\s*```", candidate_json, re.DOTALL)
            if match:
                candidate_json = match.group(0).strip("`").strip()

        # If still surrounded by other text, locate outermost braces
        if not candidate_json.startswith("{"):
            brace_start = candidate_json.find("{")
            brace_end = candidate_json.rfind("}")
            if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                candidate_json = candidate_json[brace_start:brace_end + 1].strip()

        parsed_dict = None
        try:
            parsed_dict = json.loads(candidate_json)
        except Exception:
            # Step B: Safe repair attempt for common JSON issues (unescaped newlines in code)
            try:
                # Replace literal newlines inside strings or try regex extraction of fields
                parsed_dict = self._regex_extract_fields(candidate_json, raw_text)
            except Exception:
                pass

        if parsed_dict and isinstance(parsed_dict, dict):
            rep_code = parsed_dict.get("repaired_code", "")
            # If code contains markdown markers, clean them
            if "```" in rep_code:
                code_match = re.search(r"```(?:\w+)?\n(.*?)```", rep_code, re.DOTALL)
                if code_match:
                    rep_code = code_match.group(1).strip()
                else:
                    rep_code = rep_code.replace("```", "").strip()

            if not rep_code.strip():
                rep_code = self._extract_code_block(raw_text) or fallback_code

            changes = parsed_dict.get("changes", [])
            if isinstance(changes, str):
                changes = [changes]

            return StructuredAIOutput(
                analysis=str(parsed_dict.get("analysis", "Security analysis conducted by local AI agent.")),
                root_cause=str(parsed_dict.get("root_cause", "Identified memory or input safety flaw.")),
                security_impact=str(parsed_dict.get("security_impact", "Potential security vulnerability.")),
                cwe=str(parsed_dict.get("cwe", fallback_cwe)),
                severity=str(parsed_dict.get("severity", fallback_sev)),
                repair_strategy=str(parsed_dict.get("repair_strategy", "Applied bounded safe replacement.")),
                repaired_code=rep_code,
                changes=changes
            )

        # Step C: Fallback parsing if JSON was completely invalid
        extracted_code = self._extract_code_block(raw_text) or fallback_code
        return StructuredAIOutput(
            analysis="Local AI provided unstructured repair response; safely parsed code block.",
            root_cause="Vulnerability in original source code.",
            security_impact="Potential security violation flagged by static analyzer.",
            cwe=fallback_cwe,
            severity=fallback_sev,
            repair_strategy="Replaced vulnerable statement with local AI generated logic.",
            repaired_code=extracted_code,
            changes=["Applied secure coding patch extracted from local model output."]
        )

    def _regex_extract_fields(self, candidate_json: str, raw_text: str) -> Dict[str, Any]:
        """Regex-based extraction when JSON string escaping is imperfect."""
        data = {}
        for key in ["analysis", "root_cause", "security_impact", "cwe", "severity", "repair_strategy"]:
            m = re.search(rf'"{key}"\s*:\s*"([^"]+)"', candidate_json)
            if m:
                data[key] = m.group(1)

        # Extract repaired_code (which often contains unescaped newlines/quotes)
        m_code = re.search(r'"repaired_code"\s*:\s*"(.*?)"\s*,\s*"changes"', candidate_json, re.DOTALL)
        if m_code:
            data["repaired_code"] = m_code.group(1).encode().decode('unicode_escape', errors='ignore')
        else:
            data["repaired_code"] = self._extract_code_block(raw_text)

        # Extract changes list
        m_changes = re.search(r'"changes"\s*:\s*\[(.*?)\]', candidate_json, re.DOTALL)
        if m_changes:
            raw_items = m_changes.group(1)
            items = re.findall(r'"([^"]+)"', raw_items)
            data["changes"] = items

        return data

    def _extract_code_block(self, text: str) -> Optional[str]:
        """Extract code from ``` ... ``` markdown block."""
        match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

ai_repairer = AIRepairer()
