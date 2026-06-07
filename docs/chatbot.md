# Chatbot — Documentación técnica

> Módulo de consulta en lenguaje natural para el sistema Bocar.
> Endpoint principal: `POST /api_chatbot/v1/query/`

---

## Índice

1. [Propósito](#1-propósito)
2. [Arquitectura general](#2-arquitectura-general)
3. [Flujo de una petición](#3-flujo-de-una-petición)
4. [Control de acceso por rol](#4-control-de-acceso-por-rol)
5. [Doble guardrail de seguridad](#5-doble-guardrail-de-seguridad)
6. [Estructura de archivos](#6-estructura-de-archivos)
7. [Descripción de cada módulo](#7-descripción-de-cada-módulo)
8. [Herramientas disponibles por rol](#8-herramientas-disponibles-por-rol)
9. [API Reference](#9-api-reference)
10. [Configuración y variables de entorno](#10-configuración-y-variables-de-entorno)
11. [Cambiar de backend LLM](#11-cambiar-de-backend-llm)
12. [Instalación](#12-instalación)

---

## 1. Propósito

El chatbot permite a los usuarios del sistema hacer preguntas en lenguaje natural sobre los datos de RFQs, asignaciones y proveedores, sin necesidad de navegar por pantallas específicas. El sistema traduce la pregunta a una consulta a la base de datos, ejecuta la consulta y devuelve una respuesta en español natural.

El acceso a los datos está restringido por el rol del usuario autenticado: cada rol solo puede preguntar sobre la información que le corresponde.

---

## 2. Arquitectura general

```
Cliente (frontend)
        │
        │ POST /api_chatbot/v1/query/
        │ { "pregunta": "...", "historial": [...] }
        ▼
┌─────────────────────────────────────────────────────┐
│                  ChatbotQueryView                   │
│  • CookieJWTAuthentication (JWT en cookie HttpOnly) │
│  • IsAuthenticated                                  │
│  • IsChatbotAllowed (bloquea SinRol)                │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│               RoleContextBuilder                    │
│  Lee user.role y construye:                         │
│  • allowed_tools: herramientas permitidas           │
│  • system_prompt: instrucciones + scope al LLM      │
└───────────────────┬─────────────────────────────────┘
                    │
          ┌─────────┴─────────┐
          │   Llamada 1 LLM   │  ← system_prompt + historial + pregunta
          │  (planificación)  │
          └─────────┬─────────┘
                    │
             ┌──────┴──────┐
             │  JSON plan  │
             └──────┬──────┘
                    │
        ┌───────────┼────────────┐
        │           │            │
   access_denied  direct       query
        │           │            │
      403 ◄──────   │     Guardrail 2:
                  200 ◄──  validar tool
                            contra allowed_tools
                                 │
                           ejecutar tool()
                           (query ORM)
                                 │
                       ┌─────────┴─────────┐
                       │   Llamada 2 LLM   │  ← resultados DB
                       │  (interpretación) │
                       └─────────┬─────────┘
                                 │
                               200
                    { answer, sources }
```

---

## 3. Flujo de una petición

### Paso 1 — Autenticación y permisos

La view aplica `CookieJWTAuthentication` (JWT en cookie HttpOnly, mismo mecanismo que el resto del proyecto). Si el usuario no está autenticado devuelve `401`. Si tiene `role='SinRol'` devuelve `403`.

### Paso 2 — Construcción del contexto

`RoleContextBuilder` (`context.py`) lee `user.role` y genera:

- **`allowed_tools`**: diccionario de herramientas disponibles para ese rol.
- **`system_prompt`**: instrucciones al LLM que incluyen el rol del usuario, las herramientas disponibles con sus parámetros, y el formato de respuesta esperado (JSON).

### Paso 3 — Llamada 1 al LLM (planificación)

Se llama al LLM con el `system_prompt`, el `historial` de conversación y la `pregunta`. El LLM devuelve un JSON con una de tres acciones:

```json
// Opción A — necesita consultar la DB
{ "action": "query", "tool": "listar_rfqs", "params": { "tipo": "mold", "status": "En_Com" } }

// Opción B — pregunta fuera del acceso del usuario
{ "action": "access_denied", "reason": "No tienes acceso a la información de proveedores." }

// Opción C — puede responder sin DB
{ "action": "direct", "answer": "El estado En_Com significa que el RFQ está en Comercialización." }
```

### Paso 4 — Guardrail 2 (validación del plan)

Antes de ejecutar, `processor.py` verifica que el `tool` solicitado esté en `allowed_tools` del rol. Si no lo está, devuelve `403` sin tocar la base de datos.

### Paso 5 — Ejecución del tool

Se llama a la función correspondiente en `tools.py`. Cada función aplica sus propios filtros de ownership (ej: `created_by=user` para Ind).

### Paso 6 — Llamada 2 al LLM (interpretación)

Se envía al LLM la pregunta original y los resultados de la consulta. El LLM genera una respuesta en lenguaje natural en español.

### Paso 7 — Respuesta

```json
{
  "answer": "Tienes 3 RFQs en estado En_Com y 1 en En_Pro.",
  "sources": ["listar_rfqs"]
}
```

---

## 4. Control de acceso por rol

| Rol | Puede preguntar sobre |
|---|---|
| `Ind` | Sus propios RFQs (Mold y Trimming) e historial de sus RFQs |
| `Com` | Todos los RFQs, asignaciones de proveedores, listado de proveedores |
| `Pro` | Sus propias asignaciones (Mold y Trimming) |
| `SinRol` | Nada — bloqueado con `403` antes de llegar al LLM |

---

## 5. Doble guardrail de seguridad

El sistema aplica dos capas de control de acceso independientes:

### Guardrail 1 — Inyección de contexto (soft)

El `system_prompt` que se envía al LLM incluye explícitamente qué herramientas puede usar el usuario y cuál es su rol. Si la pregunta pide información fuera del scope, el LLM devuelve `access_denied` con una explicación amigable en español.

**Propósito:** experiencia de usuario — el LLM puede explicar por qué no tiene acceso.

### Guardrail 2 — Validación de código (hard)

Antes de ejecutar cualquier tool, `processor.py` verifica que el nombre del tool generado por el LLM esté en el diccionario `allowed_tools` del rol del usuario. Si no está, se bloquea con `403` sin tocar la DB, independientemente de lo que el LLM haya devuelto.

**Propósito:** seguridad real — garantiza que ningún dato prohibido se consulta, incluso si el LLM falla o es manipulado.

### Guardrail adicional en tools.py

Las funciones que aceptan un `rfq_id` (como `historial_rfq`) validan adicionalmente que el recurso pertenece al usuario antes de consultar, cuando el rol es `Ind`. Esto protege contra el caso en que el LLM sugiera un ID de un RFQ ajeno.

---

## 6. Estructura de archivos

```
chatbot/
├── llm/
│   ├── __init__.py      ← factory get_llm() — selecciona backend por settings
│   ├── base.py          ← BaseLLM (clase abstracta, define la interfaz)
│   ├── gemini.py        ← GeminiLLM (Google Gemini API)
│   └── local.py         ← LocalLLM (Ollama en localhost)
├── context.py           ← Definición de tools por rol + build_system_prompt()
├── tools.py             ← Funciones de consulta ORM (una por herramienta)
├── processor.py         ← Orquesta el flujo completo
├── permissions.py       ← IsChatbotAllowed (bloquea SinRol)
├── serializers.py       ← ChatbotQuerySerializer
├── views.py             ← ChatbotQueryView
└── urls.py              ← POST query/
```

---

## 7. Descripción de cada módulo

### `llm/base.py`
Define `BaseLLM`, clase abstracta con un único método `chat(system_prompt, history, message) -> str`. Todo backend debe implementarlo.

### `llm/gemini.py`
Implementa `BaseLLM` usando `google-generativeai`. Crea una sesión de chat con el historial en el formato que espera Gemini (`role: user | model`). El `system_prompt` se pasa como `system_instruction` al modelo.

### `llm/local.py`
Implementa `BaseLLM` usando la API REST de Ollama (`POST /api/chat`). Compatible con cualquier modelo servido localmente (Llama, Mistral, etc.). El historial se pasa en formato OpenAI-compatible.

### `llm/__init__.py`
Factory `get_llm()` que lee `settings.LLM_BACKEND` y devuelve la instancia correcta. Cambiar de backend es solo cambiar la variable de entorno.

### `context.py`
Define los diccionarios de herramientas por rol (`TOOLS_IND`, `TOOLS_COM`, `TOOLS_PRO`) y la función `build_system_prompt(user)` que genera el prompt de sistema personalizado con el scope del usuario.

### `tools.py`
Funciones Python que ejecutan queries ORM contra la base de datos. Cada función corresponde a una herramienta que el LLM puede solicitar. Los filtros de ownership se aplican aquí, no en el processor.

### `processor.py`
Orquesta el flujo completo: construye el contexto, llama al LLM dos veces (planificación e interpretación), valida el plan (Guardrail 2), ejecuta el tool y devuelve la respuesta final.

### `permissions.py`
`IsChatbotAllowed` — extiende la autorización básica de DRF para bloquear usuarios con `role='SinRol'` antes de que la petición llegue al processor.

### `serializers.py`
Valida el body del request: `pregunta` (string, requerido, max 1000 chars) e `historial` (lista de `{role, content}`, opcional).

### `views.py`
`ChatbotQueryView` — aplica permisos, valida input, llama a `process_query()` y devuelve la respuesta con el status HTTP correcto (`200` o `403`).

---

## 8. Herramientas disponibles por rol

### Rol `Ind`

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `contar_rfqs` | `tipo`, `status` (opc.) | Cuenta los propios RFQs |
| `listar_rfqs` | `tipo`, `status` (opc.) | Lista los propios RFQs |
| `historial_rfq` | `tipo`, `rfq_id` | Historial de un RFQ propio |

### Rol `Com` (incluye las de Ind + las siguientes)

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `contar_rfqs_todos` | `tipo`, `status` (opc.) | Cuenta todos los RFQs del sistema |
| `listar_rfqs_todos` | `tipo`, `status` (opc.) | Lista todos los RFQs con creador |
| `rfqs_por_status` | `tipo` | Distribución de RFQs por status |
| `listar_proveedores` | — | Lista todos los proveedores |
| `listar_asignaciones` | `tipo`, `is_answered` (opc.) | Lista asignaciones |

### Rol `Pro`

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `mis_asignaciones` | `tipo`, `is_answered` (opc.) | Lista las asignaciones propias |

**Valores válidos:**
- `tipo`: `mold` | `trimming`
- `status`: `En_Ind` | `En_Com` | `En_Pro`
- `is_answered`: `true` | `false`

---

## 9. API Reference

### `POST /api_chatbot/v1/query/`

**Autenticación:** JWT en cookie HttpOnly (`access_token`)

**Request body:**

```json
{
  "pregunta": "¿Cuántos RFQs tengo en proceso?",
  "historial": [
    { "role": "user",      "content": "Hola" },
    { "role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?" }
  ]
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `pregunta` | string (max 1000) | Sí | Pregunta en lenguaje natural |
| `historial` | array | No | Mensajes previos de la conversación |

**Respuesta exitosa `200`:**

```json
{
  "answer": "Tienes 3 RFQs: 2 en En_Com y 1 en En_Pro.",
  "sources": ["listar_rfqs"]
}
```

**Respuesta denegada `403`:**

```json
{
  "answer": "No tienes acceso a la información de proveedores.",
  "access_denied": true,
  "sources": []
}
```

**Errores estándar:**
- `401` — no autenticado
- `403` — usuario con `SinRol` o acceso denegado por rol
- `400` — body inválido (falta `pregunta`)

---

## 10. Configuración y variables de entorno

Variables relevantes en `.env`:

```bash
# Backend LLM: 'gemini' (default) o 'local'
LLM_BACKEND=gemini

# Gemini — requerida si LLM_BACKEND=gemini
GEMINI_API_KEY=tu-api-key-aqui
GEMINI_MODEL=gemini-2.0-flash

# Local (Ollama) — requeridas si LLM_BACKEND=local
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3.2
```

Variables en `settings.py`:

```python
LLM_BACKEND    = os.environ.get('LLM_BACKEND', 'gemini')
GEMINI_API_KEY  = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL    = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
LOCAL_LLM_URL   = os.environ.get('LOCAL_LLM_URL', 'http://localhost:11434')
LOCAL_LLM_MODEL = os.environ.get('LOCAL_LLM_MODEL', 'llama3.2')
```

---

## 11. Cambiar de backend LLM

El sistema usa el patrón adaptador. Todos los backends implementan `BaseLLM`:

```
BaseLLM (base.py)
    ├── GeminiLLM (gemini.py)   ← Google Gemini API
    └── LocalLLM (local.py)     ← Ollama (Llama, Mistral, etc.)
```

**Para cambiar a un modelo local:**

1. Instalar Ollama: https://ollama.com
2. Descargar un modelo: `ollama pull llama3.2`
3. Cambiar en `.env`:

```bash
LLM_BACKEND=local
LOCAL_LLM_MODEL=llama3.2
```

**Para agregar un backend nuevo** (ej: OpenAI):

```python
# chatbot/llm/openai_llm.py
from .base import BaseLLM

class OpenAILLM(BaseLLM):
    def chat(self, system_prompt, history, message):
        # implementación con openai SDK
        ...
```

```python
# chatbot/llm/__init__.py
def get_llm():
    if settings.LLM_BACKEND == 'openai':
        from .openai_llm import OpenAILLM
        return OpenAILLM()
    ...
```

El resto del sistema (processor, views, tools) no requiere ningún cambio.

---

## 12. Instalación

```bash
pip install google-generativeai
```

Verificar que `chatbot` esté en `INSTALLED_APPS` de `settings.py` y que la ruta esté registrada en `urls.py`:

```python
# Bocar/urls.py
path('api_chatbot/v1/', include('chatbot.urls')),
```
