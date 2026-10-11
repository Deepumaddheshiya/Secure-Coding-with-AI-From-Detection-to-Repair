"""
Semgrep Static Security Scanner
"""

import sys
import shutil
import json
import uuid
from pathlib import Path
from typing import List, Optional
from backend.app.scanners.base import BaseScanner
from backend.app.models.schemas import NormalizedFinding

class SemgrepScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="semgrep", supported_languages=["c", "cpp", "csharp", "python", "javascript"])

    def is_installed(self) -> bool:
        return shutil.which("semgrep") is not None or shutil.which("py") is not None

    def get_version(self) -> Optional[str]:
        if not self.is_installed():
            return None
        try:
            cmd = ["semgrep", "--version"] if shutil.which("semgrep") else ["py", "-m", "semgrep", "--version"]
            res = self._safe_run(cmd, timeout=5)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def scan_file(self, file_path: Path, language: str) -> List[NormalizedFinding]:
        if not self.is_installed() or not file_path.exists():
            return []

        findings: List[NormalizedFinding] = []
        cmd = [
            "semgrep",
            "--config=auto",
            "--json",
            "--quiet",
            str(file_path)
        ] if shutil.which("semgrep") else [
            "py", "-m", "semgrep",
            "--config=auto",
            "--json",
            "--quiet",
            str(file_path)
        ]

        res = self._safe_run(cmd, timeout=60)
        if not res.stdout:
            return []

        try:
            data = json.loads(res.stdout)
            results = data.get("results", [])
            for idx, item in enumerate(results):
                check_id = item.get("check_id", "semgrep_rule")
                extra = item.get("extra", {})
                msg = extra.get("message", "Semgrep security finding")
                sev_raw = extra.get("severity", "WARNING").lower()
                if sev_raw in ("error", "high"):
                    severity = "critical"
                elif sev_raw in ("warning", "medium"):
                    severity = "medium"
                else:
                    severity = "low"

                metadata = extra.get("metadata", {})
                cwe_raw = metadata.get("cwe", "CWE-General")
                if isinstance(cwe_raw, list) and len(cwe_raw) > 0:
                    cwe = cwe_raw[0]
                else:
                    cwe = str(cwe_raw)

                start = item.get("start", {})
                line_no = start.get("line", 1)
                col_no = start.get("col", 0)

                code_snippet = extra.get("lines", "").strip()
                if not code_snippet:
                    code_snippet = self._extract_snippet(file_path, line_no)

                finding = NormalizedFinding(
                    id=f"SEMGREP-{file_path.name}-{line_no}-{idx}-{uuid.uuid4().hex[:6]}",
                    file=file_path.name,
                    line=line_no,
                    column=col_no,
                    scanner="semgrep",
                    rule=check_id,
                    cwe=cwe,
                    severity=severity,
                    title=f"Semgrep Finding: {check_id.split('.')[-1]}",
                    description=msg,
                    code_snippet=code_snippet
                )
                findings.append(finding)
        except Exception:
            pass

        return findings

semgrep_scanner = SemgrepScanner()
