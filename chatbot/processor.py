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
    'listar_asignaciones':    lambda user, p: tool_functions.listar_asignaciones(**p),
    'mis_asignaciones':       lambda user, p: tool_functions.mis_asignaciones(user, **p),
    'contar_rfqs_eliminados': lambda user, p: tool_functions.contar_rfqs_eliminados(**p),
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
    allowed_tools  = get_tools_for_role(user.role, user.is_admin)

    # ── Paso 1: el LLM planea qué acción tomar ───────────────────────────────
    try:
        plan_text = llm.chat(system_prompt, history, question, json_mode=True)
        plan      = _extract_json(plan_text)
    except (ValueError, json.JSONDecodeError):
        return {'answer': "I couldn't understand your question. Could you rephrase it?", 'sources': []}
    except Exception as e:
        logger.error('LLM chat error (plan step): %s', e, exc_info=True)
        return {'answer': 'The AI service is currently unavailable. Please try again later.', 'sources': []}

    action = plan.get('action')

    # ── Respuesta de acceso denegado (Guardrail 1 — el LLM lo detectó) ───────
    if action == 'access_denied':
        return {
            'answer':        plan.get('reason', 'You do not have access to that information.'),
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
                'answer':        'You do not have access to that information.',
                'sources':       [],
                'access_denied': True,
            }

        try:
            db_results = TOOL_MAP[tool_name](user, params)
        except PermissionError as e:
            return {'answer': str(e), 'sources': [], 'access_denied': True}
        except Exception as e:
            logger.error('DB tool error (tool=%s, params=%s): %s', tool_name, params, e, exc_info=True)
            return {'answer': 'An error occurred while querying the database. Please try again.', 'sources': []}

        # ── Paso 2: el LLM interpreta los resultados en lenguaje natural ──────
        interpretation_msg = (
            f"The user asked: '{question}'\n\n"
            f"Query results:\n"
            f"{json.dumps(db_results, ensure_ascii=False, default=str)}\n\n"
            f"Respond to the user concisely and naturally in English."
        )

        try:
            answer = llm.chat(_INTERPRET_SYSTEM, history, interpretation_msg)
        except Exception:
            answer = 'I retrieved the data but could not generate a response. Please try again.'

        return {'answer': answer, 'sources': [tool_name]}

    return {'answer': "I didn't understand your question. Could you rephrase it?", 'sources': []}
