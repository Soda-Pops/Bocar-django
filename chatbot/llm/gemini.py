from google import genai
from google.genai import types
from django.conf import settings

from .base import BaseLLM


class GeminiLLM(BaseLLM):

    def __init__(self):
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')

    def chat(self, system_prompt: str, history: list[dict], message: str, json_mode: bool = False) -> str:
        gemini_history = []
        for msg in history:
            role = 'user' if msg['role'] == 'user' else 'model'
            gemini_history.append(types.Content(role=role, parts=[types.Part(text=msg['content'])]))

        gemini_history.append(types.Content(role='user', parts=[types.Part(text=message)]))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type='application/json' if json_mode else 'text/plain',
        )
        response = self._client.models.generate_content(
            model=self._model_name,
            contents=gemini_history,
            config=config,
        )
        return response.text
