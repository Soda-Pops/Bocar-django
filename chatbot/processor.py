import json
import logging
import re

from chatbot.context import build_system_prompt, get_tools_for_role
from chatbot.llm import get_llm
import chatbot.tools as tool_functions

logger = logging.getLogger(__name__)


# Mapea nombre de herramienta → función ejecutora.
# Cada lambda recibe (user, params_dict) para poder aplicar filtros de ownership.
TOOL_MAP = {
    'contar_rfqs':        lambda user, p: tool_functions.contar_rfqs(user, **p),
    'listar_rfqs':        lambda user, p: tool_functions.listar_rfqs(user, **p),
    'historial_rfq':      lambda user, p: tool_functions.historial_rfq(user, **p),
    'contar_rfqs_todos':  lambda user, p: tool_functions.contar_rfqs_todos(**p),
    'listar_rfqs_todos':  lambda user, p: tool_functions.listar_rfqs_todos(**p),
    'rfqs_por_status':    lambda user, p: tool_functions.rfqs_por_status(**p),
    'listar_proveedores': lambda user, p: tool_functions.listar_proveedores(),
    'listar_asignaciones':lambda user, p: tool_functions.listar_asignaciones(**p),
    'mis_asignaciones':   lambda user, p: tool_functions.mis_asignaciones(user, **p),
}

_INTERPRET_SYSTEM = (
    'You are a friendly assistant for the Bocar system. '
    'You are given data from a query. Interpret it and respond to the user '
    'in clear, natural English. Do not mention technical tool names, '
    'JSON, or internal system details. Always respond in English.'
)


def _extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError(f'No se encontró JSON en la respuesta del LLM: {text}')
    return json.loads(match.group())


def process_query(user, question: str, history: list[dict]) -> dict:
    llm            = get_llm()
    system_prompt  = build_system_prompt(user)
    allowed_tools  = get_tools_for_role(user.role)

    # ── Paso 1: el LLM planea qué acción tomar ───────────────────────────────
    try:
        plan_text = llm.chat(system_prompt, history, question, json_mode=True)
        plan      = _extract_json(plan_text)
    except (ValueError, json.JSONDecodeError):
        return {'answer': 'No pude interpretar tu pregunta. ¿Puedes reformularla?', 'sources': []}
    except Exception as e:
        logger.error('LLM chat error (plan step): %s', e, exc_info=True)
        return {'answer': 'El servicio de IA no está disponible en este momento.', 'sources': []}

    action = plan.get('action')

    # ── Respuesta de acceso denegado (Guardrail 1 — el LLM lo detectó) ───────
    if action == 'access_denied':
        return {
            'answer':        plan.get('reason', 'No tienes acceso a esa información.'),
            'sources':       [],
            'access_denied': True,
        }

    # ── Respuesta directa (sin consulta a DB) ─────────────────────────────────
    if action == 'direct':
        return {'answer': plan.get('answer', ''), 'sources': []}

    # ── Consulta a la base de datos ───────────────────────────────────────────
    if action == 'query':
        tool_name = plan.get('tool', '')
        params    = plan.get('params', {})

        # Guardrail 2: el tool debe estar en la lista permitida para el rol
        if tool_name not in allowed_tools or tool_name not in TOOL_MAP:
            return {
                'answer':        'No tienes acceso a esa información.',
                'sources':       [],
                'access_denied': True,
            }

        try:
            db_results = TOOL_MAP[tool_name](user, params)
        except PermissionError as e:
            return {'answer': str(e), 'sources': [], 'access_denied': True}
        except Exception:
            return {'answer': 'Ocurrió un error al consultar la base de datos.', 'sources': []}

        # ── Paso 2: el LLM interpreta los resultados en lenguaje natural ──────
        interpretation_msg = (
            f"El usuario preguntó: '{question}'\n\n"
            f"Resultados de la consulta:\n"
            f"{json.dumps(db_results, ensure_ascii=False, default=str)}\n\n"
            f"Responde al usuario de forma concisa y natural."
        )

        try:
            answer = llm.chat(_INTERPRET_SYSTEM, history, interpretation_msg)
        except Exception:
            answer = 'Obtuve los datos pero no pude generar una respuesta. Intenta de nuevo.'

        return {'answer': answer, 'sources': [tool_name]}

    return {'answer': 'No entendí tu pregunta. ¿Puedes reformularla?', 'sources': []}
