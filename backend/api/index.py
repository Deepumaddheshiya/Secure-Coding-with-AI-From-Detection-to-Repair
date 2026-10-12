import sys
from pathlib import Path

# Add backend root directory to sys.path
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.main import app

__all__ = ["app"]
