"""
Research Paper Ground Truth & Published Reference Results
Extracted directly from 'Secure coding with AI - from detection to repair'
(Belozerov, Barclay & Sami, Empirical Software Engineering 2026, 31:93)

Contains:
- Table 8: CWE Distribution (23 CWE types, 66 total occurrences)
- Table 9: Language Statistics across 2,315 files (C, C++, C#)
- Table 12: Comparison of Detection & Repair across LLMs (Sep 2025)
- Table 13 & 14: Confirmed issues matrix for snapshots 20231012 & 20240514
- Table 17 & 18: Code origin comparison (User-provided vs GPT-generated)
"""

from typing import Dict, Any, List

# Published Reference Data - Table 8
PAPER_CWE_DISTRIBUTION = [
    {"cwe": "CWE-20", "description": "Improper Input Validation", "count": 16, "top_25_rank": 12},
    {"cwe": "CWE-120", "description": "Classic Buffer Overflow", "count": 11, "top_25_rank": None},
    {"cwe": "CWE-362", "description": "Race Condition", "count": 7, "top_25_rank": None},
    {"cwe": "CWE-119", "description": "Bounds of a Memory Buffer", "count": 4, "top_25_rank": 20},
    {"cwe": "CWE-22", "description": "Improper Pathname Validation", "count": 3, "top_25_rank": 5},
    {"cwe": "CWE-665", "description": "Improper Initialization", "count": 3, "top_25_rank": None},
    {"cwe": "CWE-190", "description": "Integer Overflow", "count": 2, "top_25_rank": 23},
    {"cwe": "CWE-129", "description": "Improper Validation of Array Index", "count": 2, "top_25_rank": None},
    {"cwe": "CWE-252", "description": "Unchecked Return Value", "count": 2, "top_25_rank": None},
    {"cwe": "CWE-327", "description": "Broken Cryptographic Algorithm", "count": 2, "top_25_rank": None},
    {"cwe": "CWE-686", "description": "Function Call With Incorrect Argument Type", "count": 2, "top_25_rank": None},
    {"cwe": "CWE-78", "description": "OS Command Injection", "count": 1, "top_25_rank": 7},
    {"cwe": "CWE-61", "description": "Symlink Following", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-126", "description": "Buffer Over-read", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-203", "description": "Observable Discrepancy", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-319", "description": "Cleartext HTTP Usage", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-328", "description": "Use of Weak Hash", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-385", "description": "Covert Timing Channel", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-401", "description": "Missing Release of Memory", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-561", "description": "Dead Code", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-663", "description": "Non-reentrant Function in Concurrent Context", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-772", "description": "Missing Release of Resource", "count": 1, "top_25_rank": None},
    {"cwe": "CWE-1164", "description": "Irrelevant Code", "count": 1, "top_25_rank": None},
]

# Published Reference Data - Table 9
PAPER_LANGUAGE_STATS = {
    "C": {
        "files_scanned": 325,
        "loc": 7449,
        "total_scanner_detects": 716,
        "loc_per_detect": 10.4,
        "snyk_detects": 126,
        "semgrep_detects": 49,
        "flawfinder_detects": 528,
        "cppcheck_detects": 13
    },
    "C++": {
        "files_scanned": 990,
        "loc": 19869,
        "total_scanner_detects": 237,
        "loc_per_detect": 83.8,
        "snyk_detects": 25,
        "semgrep_detects": 3,
        "flawfinder_detects": 151,
        "cppcheck_detects": 58
    },
    "C#": {
        "files_scanned": 1000,
        "loc": 17625,
        "total_scanner_detects": 6,
        "loc_per_detect": 2937.5,
        "snyk_detects": 2,
        "semgrep_detects": 4,
        "flawfinder_detects": 0,
        "cppcheck_detects": 0
    }
}

# Published Reference Data - Table 12 & Table 17 & Table 18
PAPER_MODEL_COMPARISON = {
    "October 2024 Experiment (GPT-4o)": {
        "dataset_snapshot": "snapshot_20231012",
        "files_evaluated": 26,
        "confirmed_vulnerabilities": 32,
        "models": {
            "GPT-4o (Oct 2024)": {
                "detected": 18,
                "detected_pct": 56.25,
                "fixed": 17,
                "fixed_pct": 53.13,
                "user_code_detection_pct": 80.0,
                "user_code_fixing_pct": 70.0,
                "gpt_code_detection_pct": 45.0,
                "gpt_code_fixing_pct": 45.0
            }
        }
    },
    "September 2025 Experiment (GPT-4.1, GPT-5, Claude Opus 4.1)": {
        "dataset_snapshot": "snapshot_20231012 + snapshot_20240514",
        "files_evaluated": 48,
        "confirmed_vulnerabilities": 56,
        "models": {
            "GPT-4.1 (2025-04-14)": {
                "detected": 46,
                "detected_pct": 82.14,
                "fixed": 42,
                "fixed_pct": 75.00,
                "user_code_detected": 22,
                "user_code_detected_pct": 88.0,
                "user_code_fixed": 22,
                "user_code_fixed_pct": 88.0,
                "gpt_code_detected": 26,
                "gpt_code_detected_pct": 83.87,
                "gpt_code_fixed": 23,
                "gpt_code_fixed_pct": 74.19
            },
            "GPT-5 (2025-08-07)": {
                "detected": 44,
                "detected_pct": 78.57,
                "fixed": 44,
                "fixed_pct": 78.57,
                "user_code_detected": 21,
                "user_code_detected_pct": 84.0,
                "user_code_fixed": 21,
                "user_code_fixed_pct": 84.0,
                "gpt_code_detected": 23,
                "gpt_code_detected_pct": 74.19,
                "gpt_code_fixed": 23,
                "gpt_code_fixed_pct": 74.19
            },
            "Claude Opus 4.1 (2025-08-05)": {
                "detected": 45,
                "detected_pct": 80.36,
                "fixed": 43,
                "fixed_pct": 76.79,
                "user_code_detected": 19,
                "user_code_detected_pct": 76.0,
                "user_code_fixed": 19,
                "user_code_fixed_pct": 76.0,
                "gpt_code_detected": 26,
                "gpt_code_detected_pct": 83.87,
                "gpt_code_fixed": 25,
                "gpt_code_fixed_pct": 80.65
            }
        }
    }
}

# RQ3 Breakdown Summary (Tables 17 & 18)
PAPER_RQ3_ORIGIN_SUMMARY = {
    "total_confirmed_issues": 56,
    "user_provided_code": {
        "files_count": 23,
        "confirmed_issues": 25,
        "percentage": 44.64
    },
    "gpt_generated_code": {
        "files_count": 25,
        "confirmed_issues": 31,
        "percentage": 55.36
    },
    "conclusion": (
        "Vulnerabilities occurred in both user prompts (25) and GPT responses (31). "
        "LLMs performed slightly better on human-written code than on AI-generated code."
    )
}
