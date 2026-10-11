"""
Compiler and Syntax Verification Engine
Validates C (gcc), C++ (g++), and C# (dotnet / csc).
Strictly adheres to verification rules:
Statuses: PASS, FAIL, UNAVAILABLE.
Never marks PASS if the compiler was not actually executed.
"""

import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List
from backend.app.models.schemas import CompilerVerificationResult, CompilerStatus

class CompilerEngine:
    def __init__(self):
        pass

    def get_compiler_statuses(self) -> List[CompilerStatus]:
        """Check availability of each language compiler/syntax-checker."""
        results = []
        # C (gcc)
        gcc_path = shutil.which("gcc")
        results.append(CompilerStatus(
            language="c",
            tool_name="gcc",
            installed=gcc_path is not None,
            version=self._get_tool_version("gcc") if gcc_path else None
        ))
        # C++ (g++)
        gpp_path = shutil.which("g++")
        results.append(CompilerStatus(
            language="cpp",
            tool_name="g++",
            installed=gpp_path is not None,
            version=self._get_tool_version("g++") if gpp_path else None
        ))
        # C# (dotnet / csc)
        csc_path = shutil.which("csc")
        dotnet_path = shutil.which("dotnet")
        csharp_installed = (csc_path is not None) or (dotnet_path is not None)
        csharp_tool = "csc" if csc_path else ("dotnet" if dotnet_path else "csc/dotnet")
        results.append(CompilerStatus(
            language="csharp",
            tool_name=csharp_tool,
            installed=csharp_installed,
            version=self._get_tool_version(csharp_tool) if csharp_installed else None
        ))
        return results

    def _get_tool_version(self, tool_name: str) -> Optional[str]:
        try:
            res = subprocess.run([tool_name, "--version"], capture_output=True, text=True, errors="ignore", timeout=4)
            if res.stdout.strip():
                return res.stdout.strip().splitlines()[0]
        except Exception:
            pass
        return None

    def verify_syntax(self, file_path: Path, language: str) -> CompilerVerificationResult:
        """
        Run syntax-only or compile verification on a code file.
        Returns CompilerVerificationResult with status PASS, FAIL, or UNAVAILABLE.
        Rule: Never mark PASS if the compiler was not actually executed.
        """
        lang = language.lower()

        if lang == "c":
            if not shutil.which("gcc"):
                return CompilerVerificationResult(
                    language="c",
                    compiler="gcc",
                    compiled=None,
                    exit_code=-1,
                    output="gcc compiler is not installed or not found in system PATH.",
                    status="UNAVAILABLE"
                )
            return self._run_compiler(["gcc", "-fsyntax-only", str(file_path)], "c", "gcc")

        elif lang == "cpp":
            if not shutil.which("g++"):
                return CompilerVerificationResult(
                    language="cpp",
                    compiler="g++",
                    compiled=None,
                    exit_code=-1,
                    output="g++ compiler is not installed or not found in system PATH.",
                    status="UNAVAILABLE"
                )
            return self._run_compiler(["g++", "-fsyntax-only", str(file_path)], "cpp", "g++")

        elif lang in ["csharp", "cs"]:
            # Check for csc (Roslyn C# compiler)
            if shutil.which("csc"):
                return self._run_compiler(["csc", "/t:module", f"/out:{file_path.with_suffix('.netmodule')}", str(file_path)], "csharp", "csc")
            
            # Check for dotnet
            if shutil.which("dotnet"):
                # Standalone .cs files without .csproj cannot be compiled by 'dotnet build'.
                # Test with 'dotnet exec' or report accurate status.
                # Never mark PASS without execution.
                return CompilerVerificationResult(
                    language="csharp",
                    compiler="dotnet",
                    compiled=None,
                    exit_code=-1,
                    output="dotnet SDK is present, but compiling standalone .cs files requires a .csproj project or 'csc' Roslyn compiler.",
                    status="UNAVAILABLE"
                )

            return CompilerVerificationResult(
                language="csharp",
                compiler="csc/dotnet",
                compiled=None,
                exit_code=-1,
                output="Neither csc nor dotnet compiler is installed in system PATH.",
                status="UNAVAILABLE"
            )

        return CompilerVerificationResult(
            language=lang,
            compiler="unknown",
            compiled=None,
            exit_code=-1,
            output=f"No compiler configured for language: {lang}",
            status="UNAVAILABLE"
        )

    def _run_compiler(self, cmd: list[str], language: str, compiler_name: str) -> CompilerVerificationResult:
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=12
            )
            is_ok = (res.returncode == 0)
            err_msg = res.stderr.strip() or res.stdout.strip()
            return CompilerVerificationResult(
                language=language,
                compiler=compiler_name,
                compiled=is_ok,
                exit_code=res.returncode,
                output="Compilation / Syntax Verification Passed Cleanly." if is_ok else err_msg,
                status="PASS" if is_ok else "FAIL"
            )
        except subprocess.TimeoutExpired:
            return CompilerVerificationResult(
                language=language,
                compiler=compiler_name,
                compiled=False,
                exit_code=-2,
                output="Compilation timed out after 12 seconds.",
                status="FAIL"
            )
        except Exception as e:
            return CompilerVerificationResult(
                language=language,
                compiler=compiler_name,
                compiled=False,
                exit_code=-3,
                output=f"Execution error: {str(e)}",
                status="FAIL"
            )

compiler_engine = CompilerEngine()
