"""AI Provider manager - selects and manages available providers."""
from typing import Dict, Any
from backend.app.ai_providers.openai_provider import openai_provider
from backend.app.ai_providers.anthropic_provider import anthropic_provider

class ProviderManager:
    def __init__(self):
        self.providers = {"openai": openai_provider, "anthropic": anthropic_provider}

    def get_available_providers(self) -> Dict[str, Any]:
        return {n: p.get_status() for n, p in self.providers.items()}

    def get_best_provider(self):
        for n in ["openai", "anthropic"]:
            if self.providers[n].is_configured(): return self.providers[n]
        return None

    def analyze_code(self, code, language, provider="", model="") -> Dict[str, Any]:
        p = self.providers.get(provider) if provider else self.get_best_provider()
        if not p: return {"error": "No AI provider configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env",
                          "provider": "", "model": "", "raw_response": ""}
        return p.analyze_code(code, language, model)

    def repair_code(self, code, language, findings, provider="", model="") -> Dict[str, Any]:
        p = self.providers.get(provider) if provider else self.get_best_provider()
        if not p: return {"error": "No AI provider configured.", "provider": "", "model": "", "raw_response": ""}
        return p.repair_code(code, language, findings, model)

provider_manager = ProviderManager()
