"""
Cppcheck Static Security Scanner for C/C++
"""

import sys
import shutil
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional
from backend.app.scanners.base import BaseScanner
from backend.app.models.schemas import NormalizedFinding

class CppcheckScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="cppcheck", supported_languages=["c", "cpp"])

    def is_installed(self) -> bool:
        return shutil.which("cppcheck") is not None

    def get_version(self) -> Optional[str]:
        if not self.is_installed():
            return None
        try:
            res = self._safe_run(["cppcheck", "--version"], timeout=5)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass
        return None

    def scan_file(self, file_path: Path, language: str) -> List[NormalizedFinding]:
        if language not in ("c", "cpp") or not self.is_installed() or not file_path.exists():
            return []

        findings: List[NormalizedFinding] = []
        lang_flag = "--language=c" if language == "c" else "--language=c++"
        cmd = [
            "cppcheck",
            "--enable=all",
            "--inconclusive",
            "--xml",
            "--xml-version=2",
            lang_flag,
            str(file_path)
        ]
        res = self._safe_run(cmd, timeout=30)
        xml_content = res.stderr or res.stdout
        if not xml_content or "<results" not in xml_content:
            return []

        try:
            root = ET.fromstring(xml_content)
            errors_elem = root.find("errors")
            if errors_elem is None:
                return []

            for idx, err in enumerate(errors_elem.findall("error")):
                err_id = err.get("id", "cppcheck_error")
                severity_raw = err.get("severity", "style")
                if severity_raw in ("error", "high"):
                    severity = "critical"
                elif severity_raw == "warning":
                    severity = "medium"
                else:
                    severity = "low"

                msg = err.get("msg", "Cppcheck warning")
                cwe_attr = err.get("cwe")
                cwe = f"CWE-{cwe_attr}" if cwe_attr else "CWE-General"

                location = err.find("location")
                line_no = 1
                col_no = 0
                if location is not None:
                    line_str = location.get("line", "")
                    if line_str.isdigit():
                        line_no = int(line_str)
                    col_str = location.get("column", "")
                    if col_str.isdigit():
                        col_no = int(col_str)

                snippet = self._extract_snippet(file_path, line_no)

                finding = NormalizedFinding(
                    id=f"CPPCHECK-{file_path.name}-{line_no}-{idx}-{uuid.uuid4().hex[:6]}",
                    file=file_path.name,
                    line=line_no,
                    column=col_no,
                    scanner="cppcheck",
                    rule=err_id,
                    cwe=cwe,
                    severity=severity,
                    title=f"Cppcheck Finding: {err_id}",
                    description=msg,
                    code_snippet=snippet
                )
                findings.append(finding)
        except Exception:
            pass

        return findings

cppcheck_scanner = CppcheckScanner()
