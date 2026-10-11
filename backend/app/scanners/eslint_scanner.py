"""
ESLint Security Scanner for JavaScript Source Code
"""

import shutil
import json
import uuid
from pathlib import Path
from typing import List, Optional
from backend.app.scanners.base import BaseScanner
from backend.app.models.schemas import NormalizedFinding

class ESLintScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="eslint", supported_languages=["javascript"])

    def is_installed(self) -> bool:
        return shutil.which("eslint") is not None or shutil.which("npx") is not None

    def get_version(self) -> Optional[str]:
        if not self.is_installed():
            return None
        try:
            cmd = ["eslint", "--version"] if shutil.which("eslint") else ["npx", "eslint", "--version"]
            res = self._safe_run(cmd, timeout=5)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def scan_file(self, file_path: Path, language: str) -> List[NormalizedFinding]:
        if language != "javascript" or not self.is_installed() or not file_path.exists():
            return []

        findings = []
        try:
            cmd_base = ["eslint"] if shutil.which("eslint") else ["npx", "eslint"]
            cmd = cmd_base + ["-f", "json", "--no-eslintrc", "--env", "browser,node,es6", str(file_path)]
            res = self._safe_run(cmd, timeout=12)
            output = res.stdout.strip()
            if not output:
                return []

            data = json.loads(output)
            for file_entry in data:
                messages = file_entry.get("messages", [])
                for idx, msg_item in enumerate(messages):
                    rule_id = msg_item.get("ruleId") or "js-security-flaw"
                    severity_code = msg_item.get("severity", 1)
                    severity = "critical" if severity_code == 2 else "medium"
                    line_no = msg_item.get("line", 1)
                    col_no = msg_item.get("column", 0)
                    msg_text = msg_item.get("message", "JavaScript security warning")

                    finding = NormalizedFinding(
                        id=f"ESLINT-{file_path.name}-{line_no}-{idx}-{uuid.uuid4().hex[:6]}",
                        file=file_path.name,
                        line=line_no,
                        column=col_no,
                        scanner="eslint",
                        rule=rule_id,
                        cwe="CWE-JavaScript",
                        severity=severity,
                        title=f"ESLint Issue: {rule_id}",
                        description=msg_text,
                        code_snippet=""
                    )
                    findings.append(finding)
        except Exception:
            pass

        return findings
