"""
Local Ollama Client for AI-SecureCode
Connects strictly to local Ollama runtime without any API keys or external servers.
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from backend.app.config import OLLAMA_BASE_URL, OLLAMA_TIMEOUT, SUPPORTED_LOCAL_MODELS
from backend.app.models.schemas import OllamaModelInfo

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.timeout = OLLAMA_TIMEOUT

    def is_running(self) -> bool:
        """Check if local Ollama daemon is reachable on localhost."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", headers={"User-Agent": "AI-SecureCode"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def get_installed_models(self) -> List[OllamaModelInfo]:
        """Fetch list of local models installed in Ollama."""
        if not self.is_running():
            return []
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", headers={"User-Agent": "AI-SecureCode"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = []
                for m in data.get("models", []):
                    models.append(OllamaModelInfo(
                        name=m.get("name", ""),
                        size=m.get("size", 0),
                        modified_at=m.get("modified_at", ""),
                        parameter_size=m.get("details", {}).get("parameter_size", "")
                    ))
                return models
        except Exception:
            return []

    def get_best_model(self) -> Optional[str]:
        """Auto-detect and pick the best installed coding model."""
        installed = [m.name for m in self.get_installed_models()]
        if not installed:
            return None
        # Check priority list
        for preferred in SUPPORTED_LOCAL_MODELS:
            for inst in installed:
                if preferred in inst.lower():
                    return inst
        return installed[0]

    def generate(self, prompt: str, model: str = None, system_prompt: str = None) -> Dict[str, Any]:
        """Generate response from local Ollama model without streaming."""
        if not self.is_running():
            return {
                "success": False,
                "error": "Local AI unavailable. Start Ollama and load a supported model (e.g., ollama run qwen2.5-coder)."
            }

        target_model = model or self.get_best_model()
        if not target_model:
            return {
                "success": False,
                "error": "No local Ollama model found. Please run 'ollama pull qwen2.5-coder' or another coding model."
            }

        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.95
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=data_bytes,
                headers={"Content-Type": "application/json", "User-Agent": "AI-SecureCode"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return {
                    "success": True,
                    "model": target_model,
                    "response": result.get("response", "").strip()
                }
        except urllib.error.URLError as e:
            return {"success": False, "error": f"Ollama connection error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Local AI execution error: {str(e)}"}

# Global Ollama client singleton
ollama_client = OllamaClient()
