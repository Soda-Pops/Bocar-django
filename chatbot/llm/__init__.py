from django.conf import settings

from .base import BaseLLM


def get_llm() -> BaseLLM:
    backend = getattr(settings, 'LLM_BACKEND', 'gemini')
    if backend == 'local':
        from .local import LocalLLM
        return LocalLLM()
    from .gemini import GeminiLLM
    return GeminiLLM()
