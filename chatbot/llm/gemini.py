import google.generativeai as genai
from django.conf import settings

from .base import BaseLLM


class GeminiLLM(BaseLLM):

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')

    def chat(self, system_prompt: str, history: list[dict], message: str) -> str:
        model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_prompt,
        )

        gemini_history = []
        for msg in history:
            role = 'user' if msg['role'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [msg['content']]})

        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(message)
        return response.text
