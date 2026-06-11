from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def chat(self, system_prompt: str, history: list[dict], message: str, json_mode: bool = False) -> str:
        """Envía un mensaje al modelo y devuelve su respuesta como string."""
        ...
