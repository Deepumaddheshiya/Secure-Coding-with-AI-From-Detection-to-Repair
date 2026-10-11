"""
Scientific Evaluation Metrics Engine
Calculates standard security and verification metrics:
- True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN)
- Precision, Recall, F1-Score
- Vulnerability Detection Rate & Repair Success Rate
- Finding Reduction Rate
- RQ1, RQ2, RQ3 distributions (per-CWE, per-language, user-provided vs AI-generated origin)
Formula explanations:
- Precision = TP / (TP + FP): Fraction of flagged vulnerabilities that are genuine.
- Recall = TP / (TP + FN): Fraction of confirmed vulnerabilities that were detected.
- F1-Score = 2 * (Precision * Recall) / (Precision + Recall): Harmonic mean of precision and recall.
- Detection Rate = Detected Vulnerabilities / Total Confirmed Vulnerabilities.
- Repair Success Rate = Verified Repaired Vulnerabilities / Total Confirmed Vulnerabilities.
- Reduction Rate = (Baseline Findings - Remaining Findings) / Baseline Findings * 100%.
"""

from typing import Dict, Any, List, Optional

def compute_classification_metrics(tp: int, fp: int, fn: int, tn: int = 0) -> Dict[str, float]:
    """Compute precision, recall, f1-score, and accuracy."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total > 0 else 0.0

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4),
    }

def compute_detection_rate(detected: int, total_confirmed: int) -> float:
    """Detection Rate = Detected / Total Confirmed (in percentage)."""
    return round((detected / total_confirmed) * 100.0, 2) if total_confirmed > 0 else 0.0

def compute_repair_rate(repaired: int, total_confirmed: int) -> float:
    """Repair Rate = Repaired / Total Confirmed (in percentage)."""
    return round((repaired / total_confirmed) * 100.0, 2) if total_confirmed > 0 else 0.0

def compute_reduction_rate(baseline: int, remaining: int) -> float:
    """Quantitative finding reduction rate: (baseline - remaining) / baseline * 100%."""
    if baseline <= 0:
        return 0.0
    diff = max(0, baseline - remaining)
    return round((diff / baseline) * 100.0, 2)
