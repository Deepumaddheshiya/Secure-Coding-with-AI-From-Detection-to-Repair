"""
Flawfinder Static Scanner for C/C++ Source Code
"""

import sys
import shutil
import csv
import io
import uuid
from pathlib import Path
from typing import List, Optional
from backend.app.scanners.base import BaseScanner
from backend.app.models.schemas import NormalizedFinding

class FlawfinderScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="flawfinder", supported_languages=["c", "cpp"])

    def is_installed(self) -> bool:
        return shutil.which("flawfinder") is not None or shutil.which("py") is not None

    def get_version(self) -> Optional[str]:
        if not self.is_installed():
            return None
        try:
            cmd = ["flawfinder", "--version"] if shutil.which("flawfinder") else ["py", "-m", "flawfinder", "--version"]
            res = self._safe_run(cmd, timeout=5)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def scan_file(self, file_path: Path, language: str) -> List[NormalizedFinding]:
        if language not in ("c", "cpp") or not self.is_installed() or not file_path.exists():
            return []

        findings: List[NormalizedFinding] = []
        cmd = ["flawfinder", "--csv", "--context", str(file_path)] if shutil.which("flawfinder") else ["py", "-m", "flawfinder", "--csv", "--context", str(file_path)]
        res = self._safe_run(cmd, timeout=30)
        if res.returncode != 0 and not res.stdout:
            return []

        try:
            reader = csv.DictReader(io.StringIO(res.stdout))
            severity_map = {
                5: "critical",
                4: "high",
                3: "medium",
                2: "low",
                1: "low",
                0: "note"
            }
            for idx, row in enumerate(reader):
                level_str = row.get("Level", "1")
                level = int(level_str) if level_str.isdigit() else 1
                severity = severity_map.get(level, "medium")

                line_no = int(row.get("Line", 1)) if row.get("Line", "").isdigit() else 1
                col_no = int(row.get("Column", 0)) if row.get("Column", "").isdigit() else 0

                cwe_raw = row.get("CWEs", "")
                if cwe_raw:
                    cwe_clean = cwe_raw.split("!")[0].split("/")[0].strip()
                else:
                    cwe_clean = "CWE-Other"

                rule_name = row.get("Name", "flaw")
                category = row.get("Category", "security")
                warning = row.get("Warning", "Potential security flaw")
                context = row.get("Context", "").strip()
                if not context:
                    context = self._extract_snippet(file_path, line_no)

                finding = NormalizedFinding(
                    id=f"FF-{file_path.name}-{line_no}-{idx}-{uuid.uuid4().hex[:6]}",
                    file=file_path.name,
                    line=line_no,
                    column=col_no,
                    scanner="flawfinder",
                    rule=f"{category}/{rule_name}",
                    cwe=cwe_clean,
                    severity=severity,
                    title=f"Potential {category} risk: {rule_name}",
                    description=warning,
                    code_snippet=context
                )
                findings.append(finding)
        except Exception:
            pass

        return findings

flawfinder_scanner = FlawfinderScanner()
