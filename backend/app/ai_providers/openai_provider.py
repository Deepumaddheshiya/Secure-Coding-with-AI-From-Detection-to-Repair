"""OpenAI GPT integration for vulnerability analysis and repair."""
from typing import Dict, Any
from backend.app.config import OPENAI_API_KEY, AI_REQUEST_TIMEOUT

PROMPT_TEMPLATE = """I would like to ask you to behave like senior software developer with expertise in software security to answer the next question. You must find security issues in the code snippet below in this message. Give me your analysis and the way how to fix the code if possible. Try to identify CWE number or any other number for formal classifications. Please write code where detected security issue is fixed, please write all code in one fragment.

Source code ({language}):
```{language}
{code}
```"""

class OpenAIProvider:
    name = "openai"

    def is_configured(self) -> bool:
        return bool(OPENAI_API_KEY) and "your-" not in OPENAI_API_KEY

    def get_available_models(self) -> list:
        return ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-3.5-turbo"]

    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "configured": self.is_configured(),
                "status": "ready" if self.is_configured() else "not_configured",
                "models": self.get_available_models() if self.is_configured() else []}

    def analyze_code(self, code: str, language: str, model: str = "") -> Dict[str, Any]:
        if not self.is_configured():
            return {"error": "OpenAI API key not configured. Set OPENAI_API_KEY in .env",
                    "provider": self.name, "model": "", "raw_response": ""}
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, timeout=AI_REQUEST_TIMEOUT)
            target = model or "gpt-4.1-mini"
            prompt = PROMPT_TEMPLATE.format(language=language, code=code)
            resp = client.chat.completions.create(model=target,
                messages=[{"role": "user", "content": prompt}], temperature=0.1, max_tokens=4096)
            content = resp.choices[0].message.content or ""
            return {"provider": self.name, "model": target, "raw_response": content,
                    "usage": {"prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                              "completion_tokens": resp.usage.completion_tokens if resp.usage else 0},
                    "error": ""}
        except Exception as e:
            return {"error": str(e), "provider": self.name, "model": model, "raw_response": ""}

    def repair_code(self, code: str, language: str, findings: list, model: str = "") -> Dict[str, Any]:
        return self.analyze_code(code, language, model)

openai_provider = OpenAIProvider()
