"""
Manual Verification & Auditor Workbench Module
Stores human reviewer decisions with persistent SQLite audit trails.
Complying strictly with Section 5 of the research specification:
- Confirmed vulnerability
- False positive
- Uncertain / requires further review
- Detected by the model
- Not detected by the model
- Successfully repaired
- Not successfully repaired
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.config import BASE_DIR

DB_PATH = BASE_DIR / "backend" / "app" / "db" / "manual_audit.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_audit_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manual_audit_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            finding_id TEXT,
            cwe TEXT,
            file_name TEXT,
            line_no INTEGER,
            verdict TEXT NOT NULL, 
            model_detected TEXT DEFAULT 'unspecified',
            repair_verified TEXT DEFAULT 'unspecified',
            reviewer TEXT DEFAULT 'auditor',
            notes TEXT,
            evidence TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_audit_db()

class ManualAuditService:
    def record_decision(
        self,
        case_id: str,
        verdict: str,
        finding_id: Optional[str] = None,
        cwe: Optional[str] = None,
        file_name: Optional[str] = None,
        line_no: Optional[int] = None,
        model_detected: str = "unspecified",
        repair_verified: str = "unspecified",
        reviewer: str = "research_auditor",
        notes: str = "",
        evidence: str = ""
    ) -> Dict[str, Any]:
        """Record a human verification decision with audit trail."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        cursor.execute("""
            INSERT INTO manual_audit_decisions 
            (case_id, finding_id, cwe, file_name, line_no, verdict, model_detected, repair_verified, reviewer, notes, evidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (case_id, finding_id or "", cwe or "", file_name or "", line_no or 0,
              verdict, model_detected, repair_verified, reviewer, notes, evidence, now))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "id": record_id,
            "case_id": case_id,
            "verdict": verdict,
            "model_detected": model_detected,
            "repair_verified": repair_verified,
            "timestamp": now
        }

    def get_decisions(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve audit decisions, optionally filtered by case_id."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if case_id:
            cursor.execute("SELECT * FROM manual_audit_decisions WHERE case_id = ? ORDER BY id DESC", (case_id,))
        else:
            cursor.execute("SELECT * FROM manual_audit_decisions ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "case_id": r[1],
                "finding_id": r[2],
                "cwe": r[3],
                "file_name": r[4],
                "line_no": r[5],
                "verdict": r[6],
                "model_detected": r[7],
                "repair_verified": r[8],
                "reviewer": r[9],
                "notes": r[10],
                "evidence": r[11],
                "timestamp": r[12]
            })
        return results

    def get_audit_summary(self) -> Dict[str, Any]:
        """Aggregate reviewer stats."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT verdict, COUNT(*) FROM manual_audit_decisions GROUP BY verdict")
        verdict_counts = dict(cursor.fetchall())
        cursor.execute("SELECT model_detected, COUNT(*) FROM manual_audit_decisions GROUP BY model_detected")
        detected_counts = dict(cursor.fetchall())
        cursor.execute("SELECT repair_verified, COUNT(*) FROM manual_audit_decisions GROUP BY repair_verified")
        repair_counts = dict(cursor.fetchall())
        cursor.execute("SELECT COUNT(DISTINCT case_id) FROM manual_audit_decisions")
        distinct_cases = cursor.fetchone()[0]
        conn.close()

        return {
            "total_decisions_logged": sum(verdict_counts.values()),
            "distinct_cases_reviewed": distinct_cases,
            "verdicts": verdict_counts,
            "model_detection_labels": detected_counts,
            "repair_verification_labels": repair_counts
        }

manual_audit_service = ManualAuditService()
