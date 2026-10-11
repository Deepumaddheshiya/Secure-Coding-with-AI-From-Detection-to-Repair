# Methodology & Architecture: SecureCode AI

## 1. Multi-Stage Pipeline Overview

Following Belozerov et al. (2026), the platform implements an evidence-based, privacy-preserving security pipeline:

```
+-----------------------------------------------------------------------------------+
| 1. DATASET & SOURCE CODE                                                          |
|    - DevGPT v10 Benchmark Files (File_01 to File_48) or User-Supplied Source      |
|    - Languages: C (.c), C++ (.cpp), C# (.cs)                                      |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| 2. STATIC SECURITY ANALYSIS (Triangulation)                                       |
|    - Flawfinder: Lexical buffer/format checks                                     |
|    - Cppcheck: AST-based bounds & syntax flaws                                    |
|    - Semgrep: Semantic pattern-based AST rules                                    |
|    - Snyk: Deep vulnerability and security scanning                               |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| 3. NORMALIZATION & DEDUPLICATION                                                  |
|    - Standardized schema: file, line, column, scanner, rule, CWE, severity,        |
|      confidence, title, description, and source snippet                           |
|    - Deduplication: Overlapping detections clustered by line proximity and CWE   |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| 4. AI-ASSISTED VULNERABILITY REPAIR                                               |
|    - Paper Prompt Template: Zero-shot senior security developer persona           |
|    - Configurable Provider: Local Ollama / Hosted OpenAI / Anthropic              |
|    - Output: Targeted minimal patch preserving core functionality                |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| 5. COMPILER VERIFICATION & SECURITY RE-SCAN (Future Work §9 of Paper)             |
|    - Syntax Check: gcc / g++ -fsyntax-only, dotnet / csc                          |
|    - Re-scan: Re-run applicable scanners on repaired sandbox copy                 |
|    - Reduction Rate Calculation: (baseline - remaining) / baseline * 100%         |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| 6. AUTONOMOUS RETRY LOOP (Max 3 Attempts)                                         |
|    - If compilation fails or security flaw remains unresolved:                    |
|      Diagnostic compiler error / remaining scanner hit passed back to LLM         |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| 7. HUMAN AUDITOR WORKBENCH (Section 5 Mandatory Requirement)                      |
|    - Manual review & persistent audit logging (Confirmed / False Positive)       |
|    - Evidence & rationale preservation                                            |
+-----------------------------------------------------------------------------------+
```

---

## 2. Decision Logic for Verification Status

The verifier executes according to strict deterministic rules:
- **`VERIFIED`**: Code compiles without errors AND targeted vulnerability is resolved (reduction rate > 0%, remaining findings for rule = 0).
- **`PARTIAL_FIX`**: Code compiles, some findings resolved, but residual issues remain.
- **`FAILED_SECURITY_RESCAN`**: Code compiles, but targeted security flaw was not remediated.
- **`COMPILATION_FAILED`**: The proposed code modifications broke syntactical validity.
- **`UNAVAILABLE`**: Scanner or compiler tool was not installed on host environment.
