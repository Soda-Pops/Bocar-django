import requests
from django.conf import settings

from .base import BaseLLM


class LocalLLM(BaseLLM):
    """Adaptador para modelos locales servidos via Ollama (localhost:11434)."""

    def chat(self, system_prompt: str, history: list[dict], message: str, json_mode: bool = False) -> str:
        url   = getattr(settings, 'LOCAL_LLM_URL',   'http://localhost:11434')
        model = getattr(settings, 'LOCAL_LLM_MODEL', 'llama3.2')

        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend(history)
        messages.append({'role': 'user', 'content': message})

        response = requests.post(
            f'{url}/api/chat',
            json={'model': model, 'messages': messages, 'stream': False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()['message']['content']
