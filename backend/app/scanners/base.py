"""
Base Scanner Interface for AI-SecureCode
Abstract base class and standardized execution helpers for static analysis tools.
"""

import sys
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from backend.app.models.schemas import NormalizedFinding

class BaseScanner(ABC):
    def __init__(self, name: str, supported_languages: List[str]):
        self.name = name
        self.supported_languages = supported_languages

    def is_installed(self) -> bool:
        return False

    def get_version(self) -> Optional[str]:
        return None

    def scan_file(self, file_path: Path, language: str) -> List[NormalizedFinding]:
        return []

    def _extract_snippet(self, file_path: Path, line_no: int, context_lines: int = 2) -> str:
        """Extract lines surrounding the vulnerable finding line."""
        if not file_path.exists():
            return ""
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            total = len(lines)
            if total == 0:
                return ""
            target_idx = max(0, min(line_no - 1, total - 1))
            start_idx = max(0, target_idx - context_lines)
            end_idx = min(total, target_idx + context_lines + 1)
            snippet_lines = []
            for idx in range(start_idx, end_idx):
                prefix = "-> " if idx == target_idx else "   "
                snippet_lines.append(f"{prefix}{idx + 1:4d} | {lines[idx]}")
            return "\n".join(snippet_lines)
        except Exception:
            return ""

    def _safe_run(self, cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        """Execute subprocess safely without shell=True."""
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout
        )
