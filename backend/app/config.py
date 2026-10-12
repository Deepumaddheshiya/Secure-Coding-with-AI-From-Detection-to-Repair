"""
AI-SecureCode Configuration
100% Offline, Privacy-Preserving Security Platform
"""
import os
import tempfile
from pathlib import Path

# Safe base directory resolution
CURRENT_FILE = Path(__file__).resolve()
if CURRENT_FILE.parent.parent.name == "backend":
    BASE_DIR = CURRENT_FILE.parent.parent.parent
else:
    BASE_DIR = CURRENT_FILE.parent.parent

IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

BENCHMARK_DIR = BASE_DIR / "MSc_DataEngineering_Results" / "DetectAndFix_Data" / "2025_09_24" / "DevGPT_v10_snapshot_20240514"

# Set up reports and sandbox directories safely (supporting read-only serverless filesystems)
if IS_SERVERLESS:
    TEMP_DIR = Path(tempfile.gettempdir())
    REPORTS_DIR = TEMP_DIR / "reports"
    SANDBOX_DIR = TEMP_DIR / "sandbox"
    DB_DIR = TEMP_DIR / "db"
else:
    REPORTS_DIR = BASE_DIR / "reports"
    SANDBOX_DIR = BASE_DIR / "backend" / "sandbox" if (BASE_DIR / "backend").exists() else BASE_DIR / "sandbox"
    DB_DIR = BASE_DIR / "backend" / "app" / "db" if (BASE_DIR / "backend").exists() else BASE_DIR / "app" / "db"

# Create directories with try/except fallback to /tmp if filesystem is read-only
for _dir_path in [REPORTS_DIR, SANDBOX_DIR, DB_DIR]:
    try:
        _dir_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

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

default_db_path = DB_DIR / "aisecurecode.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path.as_posix()}")

MAX_FILE_SIZE_BYTES = 512000
SUBPROCESS_TIMEOUT_SEC = 15

SUPPORTED_LANGUAGES = ["c", "cpp", "csharp", "python", "javascript"]
