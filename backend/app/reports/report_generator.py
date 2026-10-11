"""
Multi-Format Report Generator for AI-SecureCode
Produces structured JSON, tabular CSV, and formatted HTML/PDF-ready audit reports.
"""

import json
import csv
import io
import datetime
from pathlib import Path
from typing import Dict, Any, List
from backend.app.config import REPORTS_DIR

class ReportGenerator:
    def generate_json_report(self, data: Dict[str, Any], report_id: str = None) -> Path:
        """Serialize audit report to JSON format."""
        rid = report_id or f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = REPORTS_DIR / f"{rid}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return file_path

    def generate_csv_report(self, findings: List[Dict[str, Any]], report_id: str = None) -> Path:
        """Export findings to tabular CSV format."""
        rid = report_id or f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = REPORTS_DIR / f"{rid}.csv"
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "File", "Line", "Column", "Scanner", "Rule", "CWE", "Severity", "Title", "Description"])
            for item in findings:
                writer.writerow([
                    item.get("id", ""),
                    item.get("file", ""),
                    item.get("line", 1),
                    item.get("column", 0),
                    item.get("scanner", ""),
                    item.get("rule", ""),
                    item.get("cwe", ""),
                    item.get("severity", ""),
                    item.get("title", ""),
                    item.get("description", "")
                ])
        return file_path

    def generate_html_report(self, data: Dict[str, Any], report_id: str = None) -> Path:
        """Create a professional printable cybersecurity audit report in HTML/PDF format."""
        rid = report_id or f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = REPORTS_DIR / f"{rid}.html"

        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ARES Defender AI Audit Report - {rid}</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #1e293b; background: #fff; }}
        .header {{ border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ color: #1e3a8a; margin: 0 0 10px 0; font-size: 26px; }}
        .meta {{ color: #64748b; font-size: 14px; margin-bottom: 20px; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; display: inline-block; }}
        .badge-danger {{ background: #dc2626; }}
        .badge-success {{ background: #16a34a; }}
        .badge-warning {{ background: #d97706; }}
        .badge-info {{ background: #2563eb; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
        th {{ background: #f1f5f9; color: #334155; }}
        pre {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 6px; font-size: 12px; overflow-x: auto; }}
        .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
        @media print {{ body {{ margin: 15mm; }} .no-print {{ display: none; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ARES Defender AI — Vulnerability Audit & Program Repair Report</h1>
        <div class="meta">
            <strong>Project:</strong> {data.get('project_name', 'AI-SecureCode Audit')} | 
            <strong>Date:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            <strong>Environment:</strong> 100% Offline Local Sandbox
        </div>
    </div>

    <div class="card">
        <h3>Verification & Reduction Summary</h3>
        <p><strong>Baseline Findings:</strong> {data.get('baseline_count', 0)}</p>
        <p><strong>Remaining Findings:</strong> {data.get('remaining_count', 0)}</p>
        <p><strong>Findings Reduced:</strong> {data.get('reduced_count', 0)}</p>
        <p><strong>Reduction Rate:</strong> {data.get('reduction_rate', 0)}%</p>
        <p><strong>Compiler Verification:</strong> <span class="badge badge-success">{data.get('compiler_status', 'N/A')}</span></p>
    </div>

    <h3>Detected Findings</h3>
    <table>
        <thead>
            <tr>
                <th>Scanner</th>
                <th>Line</th>
                <th>Severity</th>
                <th>CWE</th>
                <th>Title & Description</th>
            </tr>
        </thead>
        <tbody>
"""
        for f in data.get("findings", []):
            sev = f.get("severity", "medium").lower()
            badge_cls = "badge-danger" if sev in ["critical", "high"] else ("badge-warning" if sev == "medium" else "badge-info")
            html_template += f"""
            <tr>
                <td><strong>{f.get('scanner')}</strong></td>
                <td>{f.get('line')}</td>
                <td><span class="badge {badge_cls}">{sev.upper()}</span></td>
                <td><code>{f.get('cwe')}</code></td>
                <td><strong>{f.get('title')}</strong><br><small>{f.get('description')}</small></td>
            </tr>
"""

        html_template += """
        </tbody>
    </table>

    <div style="margin-top: 30px;" class="no-print">
        <button onclick="window.print()" style="padding: 10px 20px; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: bold;">
            Print / Save as PDF
        </button>
    </div>
</body>
</html>
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        return file_path

report_generator = ReportGenerator()
