TOOLS_IND = {
    'contar_rfqs': {
        'descripcion': 'Cuenta los RFQs propios del usuario, opcionalmente filtrados por tipo y status.',
        'params':      {'tipo': 'mold|trimming', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
    },
    'listar_rfqs': {
        'descripcion': 'Lista los RFQs propios del usuario con id, descripción, status y fechas.',
        'params':      {'tipo': 'mold|trimming', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
    },
    'historial_rfq': {
        'descripcion': 'Muestra el historial de eventos de un RFQ propio.',
        'params':      {'tipo': 'mold|trimming', 'rfq_id': 'entero'},
    },
}

TOOLS_COM = {
    **TOOLS_IND,
    'contar_rfqs_todos': {
        'descripcion': 'Cuenta todos los RFQs del sistema (no solo los propios).',
        'params':      {'tipo': 'mold|trimming', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
    },
    'listar_rfqs_todos': {
        'descripcion': 'Lista todos los RFQs del sistema con creador incluido.',
        'params':      {'tipo': 'mold|trimming', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
    },
    'rfqs_por_status': {
        'descripcion': 'Devuelve la distribución de RFQs agrupada por status.',
        'params':      {'tipo': 'mold|trimming'},
    },
    'listar_proveedores': {
        'descripcion': 'Lista todos los proveedores registrados con empresa, país y rating.',
        'params':      {},
    },
    'listar_asignaciones': {
        'descripcion': 'Lista las asignaciones de proveedores a RFQs.',
        'params':      {'tipo': 'mold|trimming', 'is_answered': '(opcional) true|false'},
    },
}

TOOLS_PRO = {
    'mis_asignaciones': {
        'descripcion': 'Lista las asignaciones propias del proveedor autenticado.',
        'params':      {'tipo': 'mold|trimming', 'is_answered': '(opcional) true|false'},
    },
}

_ROLE_DESCRIPTIONS = {
    'Ind': 'Industrialización — solo puede consultar sus propios RFQs',
    'Com': 'Comercialización — acceso completo a RFQs, asignaciones y proveedores',
    'Pro': 'Proveedor — solo puede consultar sus propias asignaciones',
}


def get_tools_for_role(role: str) -> dict:
    return {'Ind': TOOLS_IND, 'Com': TOOLS_COM, 'Pro': TOOLS_PRO}.get(role, {})


def build_system_prompt(user) -> str:
    tools = get_tools_for_role(user.role)

    tools_str = ''
    for name, meta in tools.items():
        params_str = ', '.join(f'{k}: {v}' for k, v in meta['params'].items()) or 'sin parámetros'
        tools_str += f'\n- {name}({params_str}): {meta["descripcion"]}'

    role_desc = _ROLE_DESCRIPTIONS.get(user.role, user.role)

    return f"""Eres un asistente de consulta para el sistema Bocar de gestión de RFQs (Request for Quotation).

Usuario actual: {user.username} (rol: {role_desc})

HERRAMIENTAS DISPONIBLES para este usuario:{tools_str}

INSTRUCCIONES:
Analiza la pregunta y responde ÚNICAMENTE con un JSON válido en uno de estos tres formatos:

1. Si necesitas consultar la base de datos:
{{"action": "query", "tool": "<nombre>", "params": {{<parámetros>}}}}

2. Si la pregunta pide información fuera del acceso del usuario:
{{"action": "access_denied", "reason": "<explicación amigable en español>"}}

3. Si puedes responder sin base de datos (preguntas generales del sistema):
{{"action": "direct", "answer": "<respuesta en español>"}}

REGLAS:
- Solo usa herramientas de la lista anterior. Jamás inventes herramientas.
- El JSON debe ser el único contenido de tu respuesta, sin texto adicional.
- Los valores de 'tipo' siempre en minúsculas: 'mold' o 'trimming'.
- Si el usuario pregunta algo que requiere un rol que no tiene, usa access_denied."""
