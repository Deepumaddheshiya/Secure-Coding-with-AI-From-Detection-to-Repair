"""
Snyk Code Static Security Scanner
Integrates the 4th scanner from the research paper: Snyk CLI (v1.1294.0+ in paper).
Supports C, C++, and C#. Requires Snyk CLI and optional SNYK_TOKEN for cloud rule lookup.
Does not fabricate findings; reports live execution results or clear unavailability status.
"""

import os
import shutil
import json
import uuid
from pathlib import Path
from typing import List, Optional
from backend.app.scanners.base import BaseScanner
from backend.app.models.schemas import NormalizedFinding
from backend.app.config import BASE_DIR

class SnykScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="snyk", supported_languages=["c", "cpp", "csharp"])

    def is_installed(self) -> bool:
        return shutil.which("snyk") is not None

    def get_version(self) -> Optional[str]:
        if not self.is_installed():
            return None
        try:
            res = self._safe_run(["snyk", "--version"], timeout=5)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def scan_file(self, file_path: Path, language: str) -> List[NormalizedFinding]:
        if language not in ("c", "cpp", "csharp") or not self.is_installed() or not file_path.exists():
            return []

        findings: List[NormalizedFinding] = []
        # Snyk Code CLI invocation
        token = os.getenv("SNYK_TOKEN", "")
        env = os.environ.copy()
        if token:
            env["SNYK_TOKEN"] = token

        cmd = ["snyk", "code", "test", "--json", str(file_path)]
        try:
            import subprocess
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=45,
                env=env
            )
        except Exception:
            return []

        output = res.stdout.strip()
        if not output:
            return []

        try:
            data = json.loads(output)
            # Snyk output format can be a list or a dict with "runs" or "issues"
            issues = []
            if isinstance(data, dict):
                runs = data.get("runs", [])
                if runs:
                    results = runs[0].get("results", [])
                    rules = runs[0].get("tool", {}).get("driver", {}).get("rules", [])
                    rule_map = {r.get("id"): r for r in rules}
                    for idx, item in enumerate(results):
                        rule_id = item.get("ruleId", "snyk-rule")
                        rule_info = rule_map.get(rule_id, {})
                        cwe_tags = rule_info.get("properties", {}).get("cwe", [])
                        cwe = cwe_tags[0] if cwe_tags else "CWE-General"
                        level = item.get("level", "warning")
                        sev_map = {"error": "critical", "warning": "medium", "note": "low"}
                        severity = sev_map.get(level, "medium")

                        locations = item.get("locations", [])
                        line_no = 1
                        col_no = 0
                        if locations:
                            phys = locations[0].get("physicalLocation", {}).get("region", {})
                            line_no = phys.get("startLine", 1)
                            col_no = phys.get("startColumn", 0)

                        msg = item.get("message", {}).get("text", "Snyk finding")
                        snippet = self._extract_snippet(file_path, line_no)

                        findings.append(NormalizedFinding(
                            id=f"SNYK-{file_path.name}-{line_no}-{idx}-{uuid.uuid4().hex[:6]}",
                            file=file_path.name,
                            line=line_no,
                            column=col_no,
                            scanner="snyk",
                            rule=rule_id,
                            cwe=cwe,
                            severity=severity,
                            title=f"Snyk Finding: {rule_id}",
                            description=msg,
                            code_snippet=snippet
                        ))
        except Exception:
            pass

        return findings

snyk_scanner = SnykScanner()
