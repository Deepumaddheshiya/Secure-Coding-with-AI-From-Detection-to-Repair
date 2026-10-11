"""
Bandit Scanner for Python Source Code
"""

import sys
import json
import uuid
from pathlib import Path
from typing import List, Optional
from backend.app.scanners.base import BaseScanner
from backend.app.models.schemas import NormalizedFinding

class BanditScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="bandit", supported_languages=["python"])

    def is_installed(self) -> bool:
        try:
            import bandit
            return True
        except ImportError:
            return False

    def get_version(self) -> Optional[str]:
        try:
            import bandit
            return getattr(bandit, "__version__", "1.9.4")
        except Exception:
            return None

    def scan_file(self, file_path: Path, language: str) -> List[NormalizedFinding]:
        if language != "python" or not file_path.exists():
            return []

        findings = []
        try:
            res = self._safe_run([sys.executable, "-m", "bandit", "-f", "json", "-q", str(file_path)], timeout=15)
            output = res.stdout.strip()
            if not output:
                return []

            data = json.loads(output)
            results = data.get("results", [])

            for idx, item in enumerate(results):
                sev_raw = item.get("issue_severity", "MEDIUM").lower()
                severity = "critical" if sev_raw == "high" else ("medium" if sev_raw == "medium" else "low")
                line_no = item.get("line_number", 1)
                col_no = item.get("col_offset", 0)
                cwe_dict = item.get("issue_cwe", {})
                cwe_id = f"CWE-{cwe_dict.get('id')}" if cwe_dict.get("id") else "CWE-Security"
                test_id = item.get("test_id", "B000")
                test_name = item.get("test_name", "bandit_issue")
                issue_text = item.get("issue_text", "Security flaw detected")
                code_snippet = item.get("code", "").strip()

                finding = NormalizedFinding(
                    id=f"BANDIT-{file_path.name}-{line_no}-{idx}-{uuid.uuid4().hex[:6]}",
                    file=file_path.name,
                    line=line_no,
                    column=col_no,
                    scanner="bandit",
                    rule=f"{test_id}:{test_name}",
                    cwe=cwe_id,
                    severity=severity,
                    title=f"Python Security Issue: {test_name}",
                    description=issue_text,
                    code_snippet=code_snippet
                )
                findings.append(finding)
        except Exception as e:
            pass

        return findings
