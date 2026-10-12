# package init
import sys
import types
from pathlib import Path

# Ensure backend directory and repo root are in sys.path
_current_file = Path(__file__).resolve()
_backend_dir = _current_file.parent.parent
_repo_dir = _backend_dir.parent

for _p in [str(_backend_dir), str(_repo_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# If 'backend' is not in sys.modules (e.g. deployed with root directory as backend on Vercel),
# create a virtual module mapping to _backend_dir so 'from backend.app...' works
if "backend" not in sys.modules:
    _backend_pkg = types.ModuleType("backend")
    _backend_pkg.__path__ = [str(_backend_dir)]
    sys.modules["backend"] = _backend_pkg

