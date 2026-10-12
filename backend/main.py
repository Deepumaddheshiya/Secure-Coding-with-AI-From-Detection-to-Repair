"""
Entrypoint for Vercel Zero-Config Deployment
Exposes the FastAPI 'app' from app.main
"""
import sys
from pathlib import Path

_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from app.main import app

__all__ = ["app"]
