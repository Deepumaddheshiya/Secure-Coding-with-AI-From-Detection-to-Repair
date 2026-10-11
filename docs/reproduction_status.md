# Scientific Reproduction & Implementation Status Report

**Study Title:** Secure coding with AI – from detection to repair  
**Authors:** Vladislav Belozerov, Peter J. Barclay, Ashkan Sami (2026)  
**Implementation Platform:** SecureCode AI / ARES-DEFENDER v2.0.0

---

## 1. Reproduction Fidelity Matrix

| Research Paper Dimension | Target Specification in Paper | Implementation Status | Evidence / Notes |
|:---|:---|:---:|:---|
| **Dataset Selection** | DevGPT v10 (`20231012` & `20240514`) | **REPRODUCED** | 48 curated benchmark test cases (`File_01`–`File_48`) with original source and metadata present. |
| **Language Coverage** | C, C++, C# | **REPRODUCED** | Parsers, language extensions, and compilers configured for all three languages. |
| **Static Analysis Suite** | Flawfinder, Semgrep, Snyk, Cppcheck | **REPRODUCED** | All 4 scanners integrated into modular `ScannerManager` with uniform finding schema. |
| **Prompt Engineering** | Exact zero-shot senior security prompt | **REPRODUCED** | Uses the paper's exact prompt (Section 6.2) for AI vulnerability analysis & repairs. |
| **AI Evaluation Models** | GPT-4o (2024), GPT-4.1, GPT-5, Claude Opus 4.1 (2025) | **REPRODUCED + EXTENDED** | Historical responses preserved; live execution supports OpenAI, Anthropic, & offline local Ollama. |
| **Manual Verification** | Expert validation of 114 candidate files (§5.3) | **REPRODUCED** | Built interactive Manual Auditor Workbench with SQLite persistent audit trail. |
| **Compiler Check & Re-scan** | Future Work (§9) & verification | **EXTENDED** | Automatic MinGW GCC/G++/dotnet syntax verification + Security re-scan reduction rate. |
| **Autonomous Retry Loop** | Iterative feedback up to 3 attempts | **EXTENDED** | Autonomous retry pipeline with diagnostic feedback. |

---

## 2. Quantitative Comparison: Paper Published Reference vs. Local Execution

> **Crucial Academic Rule:** Published paper findings are strictly preserved as reference benchmarks and never conflated with live local execution results.

### Paper Reported Findings (September 2025 - 48 Files, 56 Confirmed Flaws)
- **GPT-4.1:** 46 Detected (82.14%), 42 Repaired (75.00%)
- **GPT-5:** 44 Detected (78.57%), 44 Repaired (78.57%)
- **Claude Opus 4.1:** 45 Detected (80.36%), 43 Repaired (76.79%)

### Local Dataset Baseline Records (`evaluation_report.json`)
- Evaluated 48 benchmark samples with 72 baseline findings and 74 Flawfinder hits.
- **Flawfinder hits after repair:**
  - Claude Opus 4.1: 72 remaining hits (12 cases completely remediated, 21 passing syntax compilation).
  - GPT-4.1: 69 remaining hits (13 cases completely remediated, 15 passing syntax compilation).
  - GPT-5: 57 remaining hits (14 cases completely remediated, 16 passing syntax compilation).

---

## 3. Disclosed Limitations & Scope Notes

1. **Snyk CLI Authentication:**
   Snyk execution requires a local `snyk` installation and optional `SNYK_TOKEN`. When absent, the scanner reports `Tool not found on PATH / Authentication required` without fabricating mock findings.
2. **Compilers Availability:**
   MinGW GCC 6.3.0 (`gcc`), G++ 6.3.0 (`g++`), and .NET CLI (`dotnet`) are live on the host system.
3. **Data Contamination Note (from Paper §7.2):**
   The authors observed that 2025 models showed ~25% higher performance than 2024 models, partially attributable to public availability of DevGPT and preprints in pre-training corpora.
