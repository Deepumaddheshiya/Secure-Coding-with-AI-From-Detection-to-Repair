"""Anthropic Claude integration for vulnerability analysis and repair."""
from typing import Dict, Any
from backend.app.config import ANTHROPIC_API_KEY, AI_REQUEST_TIMEOUT

PROMPT_TEMPLATE = """I would like to ask you to behave like senior software developer with expertise in software security to answer the next question. You must find security issues in the code snippet below in this message. Give me your analysis and the way how to fix the code if possible. Try to identify CWE number or any other number for formal classifications. Please write code where detected security issue is fixed, please write all code in one fragment.

Source code ({language}):
```{language}
{code}
```"""

class AnthropicProvider:
    name = "anthropic"

    def is_configured(self) -> bool:
        return bool(ANTHROPIC_API_KEY) and "your-" not in ANTHROPIC_API_KEY

    def get_available_models(self) -> list:
        return ["claude-sonnet-4-20250514", "claude-haiku-4-20250414"]

    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "configured": self.is_configured(),
                "status": "ready" if self.is_configured() else "not_configured",
                "models": self.get_available_models() if self.is_configured() else []}

    def analyze_code(self, code: str, language: str, model: str = "") -> Dict[str, Any]:
        if not self.is_configured():
            return {"error": "Anthropic API key not configured. Set ANTHROPIC_API_KEY in .env",
                    "provider": self.name, "model": "", "raw_response": ""}
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            target = model or "claude-sonnet-4-20250514"
            prompt = PROMPT_TEMPLATE.format(language=language, code=code)
            resp = client.messages.create(model=target, max_tokens=4096, temperature=0.1,
                messages=[{"role": "user", "content": prompt}])
            content = resp.content[0].text if resp.content else ""
            return {"provider": self.name, "model": target, "raw_response": content,
                    "usage": {"input_tokens": resp.usage.input_tokens if resp.usage else 0,
                              "output_tokens": resp.usage.output_tokens if resp.usage else 0},
                    "error": ""}
        except Exception as e:
            return {"error": str(e), "provider": self.name, "model": model, "raw_response": ""}

    def repair_code(self, code: str, language: str, findings: list, model: str = "") -> Dict[str, Any]:
        return self.analyze_code(code, language, model)

anthropic_provider = AnthropicProvider()
