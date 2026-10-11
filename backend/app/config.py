"""
AI-SecureCode Configuration
100% Offline, Privacy-Preserving Security Platform
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BENCHMARK_DIR = BASE_DIR / "MSc_DataEngineering_Results" / "DetectAndFix_Data" / "2025_09_24" / "DevGPT_v10_snapshot_20240514"
REPORTS_DIR = BASE_DIR / "reports"
SANDBOX_DIR = BASE_DIR / "backend" / "sandbox"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))

SUPPORTED_LOCAL_MODELS = [
    "qwen2.5-coder",
    "deepseek-coder",
    "codellama",
    "starcoder2",
    "llama3",
    "mistral"
]

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/backend/app/db/aisecurecode.db")

MAX_FILE_SIZE_BYTES = 512000
SUBPROCESS_TIMEOUT_SEC = 15

SUPPORTED_LANGUAGES = ["c", "cpp", "csharp", "python", "javascript"]
