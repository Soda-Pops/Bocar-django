TOOLS_IND = {
    'contar_rfqs': {
        'descripcion': 'Cuenta los RFQs propios del usuario, opcionalmente filtrados por tipo y status.',
        'params':      {'tipo': 'mold|trimming|ambos', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
    },
    'listar_rfqs': {
        'descripcion': 'Lista los RFQs propios del usuario con id, descripción, status y fechas.',
        'params':      {'tipo': 'mold|trimming|ambos', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
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
        'params':      {'tipo': 'mold|trimming|ambos', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
    },
    'listar_rfqs_todos': {
        'descripcion': 'Lista todos los RFQs del sistema con creador incluido.',
        'params':      {'tipo': 'mold|trimming|ambos', 'status': '(opcional) En_Ind|En_Com|En_Pro'},
    },
    'rfqs_por_status': {
        'descripcion': 'Devuelve la distribución de RFQs agrupada por status.',
        'params':      {'tipo': 'mold|trimming|ambos'},
    },
    'listar_proveedores': {
        'descripcion': 'Lista todos los proveedores registrados con empresa, país y rating.',
        'params':      {},
    },
    'listar_asignaciones': {
        'descripcion': 'Lista las asignaciones de proveedores a RFQs.',
        'params':      {'tipo': 'mold|trimming|ambos', 'is_answered': '(opcional) true|false'},
    },
}

TOOLS_PRO = {
    'mis_asignaciones': {
        'descripcion': 'Lista las asignaciones propias del proveedor autenticado.',
        'params':      {'tipo': 'mold|trimming|ambos', 'is_answered': '(opcional) true|false'},
    },
}

TOOLS_COM_ADMIN = {
    **TOOLS_COM,
    'contar_rfqs_eliminados': {
        'descripcion': 'Cuenta los RFQs eliminados del sistema.',
        'params':      {'tipo': 'mold|trimming|ambos'},
    },
}

_ROLE_DESCRIPTIONS = {
    'Ind':       'Industrialización — solo puede consultar sus propios RFQs',
    'Ind_admin': 'Industrialización Super User — acceso completo a todos los RFQs',
    'Com':       'Comercialización — acceso completo a RFQs, asignaciones y proveedores',
    'Com_admin': 'Comercialización Super User — acceso completo incluyendo RFQs eliminados',
    'Pro':       'Proveedor — solo puede consultar sus propias asignaciones',
}


def get_tools_for_role(role: str, is_admin: bool = False) -> dict:
    if role == 'Ind':
        return TOOLS_COM if is_admin else TOOLS_IND
    if role == 'Com':
        return TOOLS_COM_ADMIN if is_admin else TOOLS_COM
    if role == 'Pro':
        return TOOLS_PRO
    return {}


def _get_status_mapping() -> str:
    from RFQ_Mold.models import RFQ_Mold
    lines = []
    for value, label in RFQ_Mold.Status.choices:
        lines.append(f'- "{label.lower()}" / "{value.lower()}" → {value}')
    return '\n'.join(lines)


def build_system_prompt(user) -> str:
    tools = get_tools_for_role(user.role, user.is_admin)

    tools_str = ''
    for name, meta in tools.items():
        params_str = ', '.join(f'{k}: {v}' for k, v in meta['params'].items()) or 'sin parámetros'
        tools_str += f'\n- {name}({params_str}): {meta["descripcion"]}'

    role_key = f'{user.role}_admin' if user.is_admin else user.role
    role_desc = _ROLE_DESCRIPTIONS.get(role_key, user.role)
    status_mapping = _get_status_mapping()

    return f"""You are a query assistant for the Bocar RFQ (Request for Quotation) management system.
Always respond in English, regardless of the language the user writes in.

Current user: {user.username} (role: {role_desc})

AVAILABLE TOOLS for this user:{tools_str}

STATUS MAPPING (always translate before using the status parameter):
{status_mapping}
- "draft" / "drafts" / "in industrialization" → En_Ind
- "awaiting authorization" / "under review" / "in commercialization" → En_Com
- "active" / "quoting" / "quoting process" / "with supplier" / "in supplier" → En_Pro

INSTRUCTIONS:
Analyze the question and respond ONLY with a valid JSON in one of these three formats:

1. If you need to query the database:
{{"action": "query", "tool": "<name>", "params": {{<parameters>}}}}

2. If the question requests information outside the user's access:
{{"action": "access_denied", "reason": "<friendly explanation in English>"}}

3. If you can answer without the database (general system questions):
{{"action": "direct", "answer": "<response in English>"}}

RULES:
- Only use tools from the list above. Never invent tools.
- The JSON must be the only content of your response, with no additional text.
- Values for 'tipo' always in lowercase: 'mold' or 'trimming'.
- Always translate status terms using the mapping above before passing them as parameters.
- If the user asks something that requires a role they don't have, use access_denied."""
