import sys
from pathlib import Path

# Add project root directory to sys.path so backend imports work seamlessly
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
