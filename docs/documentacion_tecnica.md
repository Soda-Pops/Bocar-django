# Documentación Técnica — Sistema Bocar

## Datos de identificación

| Campo | Valor |
|---|---|
| **Título del documento** | Documentación Técnica — Sistema Bocar |
| **Versión del documento** | 2.0 |
| **Fecha de publicación** | 2026-06-11 |
| **Producto de software** | Bocar Backend (API REST), versión 1.0.0 |
| **Organización emisora** | Equipo Soda-Pops — Tecnológico de Monterrey (TEC), 6° semestre |

### Historial de cambios

| Versión | Fecha | Descripción |
|---|---|---|
| 1.0 | 2026-06-08 | Versión inicial |
| 2.0 | 2026-06-11 | Requisitos reorganizados por componente (Python, Celery, RabbitMQ, MSSQL, LLM); módulos Evaluaciones y modulo_IA; rol IT; cierre formal de RFQ; tabla de pruebas corregida; SDK del chatbot actualizado a `google-genai`; recomendaciones alineadas a `security.md` |

---

## Índice

1. [Resumen general](#1-resumen-general)
2. [Introducción](#2-introducción)
3. [Objetivo del sistema](#3-objetivo-del-sistema)
4. [Requisitos del sistema](#4-requisitos-del-sistema)
5. [Arquitectura del sistema](#5-arquitectura-del-sistema)
6. [Diseño de módulos](#6-diseño-de-módulos)
7. [Diseño de interfaces y algoritmos](#7-diseño-de-interfaces-y-algoritmos)
8. [Problemas encontrados](#8-problemas-encontrados)
9. [Pruebas del software](#9-pruebas-del-software)
10. [Recomendaciones](#10-recomendaciones)
11. [Siglas, acrónimos y glosario](#11-siglas-acrónimos-y-glosario)

---

## 1. Resumen general

Bocar es un sistema de gestión de RFQs (Request for Quotation — Solicitud de Cotización) desarrollado como proyecto académico del Tecnológico de Monterrey (TEC), 6° semestre, por el equipo Soda-Pops.

El sistema es un **backend REST** construido con Django y Django REST Framework. Su propósito es digitalizar y controlar el flujo de cotizaciones de herramental entre tres áreas: Industrialización, Comercialización y Proveedores. Cada área tiene un conjunto de permisos y acciones definidas que el sistema hace cumplir automáticamente.

El sistema es únicamente backend — no incluye frontend. Está diseñado para consumirse desde una aplicación web o móvil externa a través de su API REST.

---

## 2. Introducción

En entornos de manufactura, el proceso de solicitar cotizaciones a proveedores externos de herramental (moldes y recortes) involucra múltiples áreas y documentos. Sin un sistema centralizado, este proceso se gestiona por correo electrónico y hojas de cálculo, lo que dificulta el seguimiento, genera pérdida de información y no deja registro de auditoría.

Bocar resuelve este problema proveyendo una plataforma donde:

- El área de **Industrialización** crea y gestiona las solicitudes de cotización.
- El área de **Comercialización** las revisa, asigna proveedores, coordina el flujo, compara precios, cierra formalmente las RFQs y evalúa la entrega de cada proveedor.
- Los **Proveedores** reciben sus asignaciones, envían cotizaciones y solicitan extensiones de tiempo.

Cada acción queda registrada en un historial de auditoría. Las notificaciones relevantes se envían automáticamente por correo electrónico de forma asíncrona. El sistema incluye un chatbot inteligente que permite a cada usuario consultar la información a la que tiene acceso usando lenguaje natural.

---

## 3. Objetivo del sistema

**Objetivo general:**
Proveer una plataforma centralizada para gestionar el ciclo de vida completo de las solicitudes de cotización de herramental (Mold y Trimming), garantizando control de acceso por rol, trazabilidad completa y comunicación automatizada entre las partes involucradas.

**Objetivos específicos:**

- Controlar el flujo de estados de un RFQ (`En_Ind → En_Com → En_Pro → cierre formal`) y hacer cumplir las transiciones válidas.
- Implementar control de acceso granular por rol de usuario (`Ind`, `Com`, `Pro`, `IT`, `SinRol`).
- Registrar automáticamente cada evento del ciclo de vida en un historial de auditoría inmutable.
- Enviar notificaciones por correo electrónico de forma asíncrona cuando ocurren eventos relevantes.
- Evaluar objetivamente el desempeño de los proveedores y mantener un rating histórico por proveedor.
- Proveer un chatbot conversacional que respete el nivel de acceso de cada usuario al consultar datos.
- Documentar y corregir vulnerabilidades de seguridad identificadas durante el desarrollo.

---

## 4. Requisitos del sistema

Los requisitos de software se presentan **por componente**, indicando cada librería, su versión y su rol dentro del sistema.

> 📝 **Estado del lock de dependencias:** las dependencias están fijadas en el `requirements.txt` de la raíz (codificado en UTF-8), lo que resuelve el issue B de [security.md](security.md). El entorno virtual (`venv/`) correctamente **no** se versiona (`.gitignore`). Las versiones de abajo provienen de ese archivo.

### 4.1 Sección Python — lenguaje y framework

| Componente | Versión | Rol |
|---|---|---|
| Python | 3.14.x | Lenguaje de programación principal |
| Django | 6.0.6 | Framework web: ORM, sistema de migraciones, panel admin, enrutamiento |
| Django REST Framework (DRF) | 3.17.1 | Capa de API REST: serializers, vistas basadas en clases, permisos, throttling |
| djangorestframework-simplejwt | 5.5.1 | Emisión y validación de JWT (access/refresh) con blacklist de rotación |
| PyJWT | 2.13.0 | Codificación/firma de tokens (dependencia de simplejwt) |
| djoser | 2.3.3 | Endpoints de gestión de usuarios (creación restringida a administradores) |
| drf-spectacular | 0.29.0 | Generación del esquema OpenAPI 3 y las UIs de Swagger/ReDoc |
| django-cors-headers | 4.9.0 | Política CORS para el frontend (Vite en `localhost:5173`) con credenciales |
| django-countries | 9.0.0 | Campo de país ISO en el modelo `Proveedor` |
| django-jazzmin | 3.0.4 | Tema visual del panel de administración de Django |
| python-dotenv | 1.2.2 | Carga de variables de entorno desde `.env` al arrancar `settings.py` |

El `requirements.txt` incluye además dependencias transitivas (kombu, billiard, vine, cryptography, jsonschema, social-auth-*, etc.) que se instalan automáticamente.

### 4.2 Sección Celery — tareas asíncronas

| Componente | Versión | Rol |
|---|---|---|
| Celery | 5.6.3 | Cola de tareas: ejecuta el envío de correos de notificación fuera del ciclo request/response, con reintentos (máx. 3, delay 60 s) |
| Kombu | 5.6.2 | Capa de mensajería de Celery (se instala como dependencia) |
| amqp | 5.3.1 | Implementación del protocolo AMQP hacia RabbitMQ |

Configuración relevante (en `Bocar/settings.py`): serialización JSON, result backend `rpc://`, broker tomado de `CELERY_BROKER_URL`.

> 📝 **No se usa Celery Beat.** La tarea periódica que cerraba asignaciones vencidas fue eliminada; ahora el cierre es *lazy* — ocurre al consultar las asignaciones o al cerrar formalmente una RFQ (`Asignaciones/services.py`).

### 4.3 Sección RabbitMQ — broker de mensajes

| Componente | Versión | Rol |
|---|---|---|
| RabbitMQ | 3.x (recomendado) | Broker AMQP: recibe las tareas encoladas por Django y las entrega a los workers de Celery |

- URL por defecto: `amqp://guest:guest@localhost:5672//` (variable `CELERY_BROKER_URL`).
- Solo es necesario cuando `NOTIFICATIONS_ENABLED=True`; con el flag apagado no se encolan tareas y el sistema funciona sin broker.
- Consola de administración: puerto `15672` (imagen Docker `rabbitmq:management`).

### 4.4 Sección correo — SMTP Microsoft 365

| Componente | Rol |
|---|---|
| Cuenta Microsoft 365 con SMTP habilitado | Remitente de las notificaciones (host `smtp.office365.com`, puerto 587, TLS) |

En desarrollo el backend por defecto es el de consola (los correos se imprimen, no se envían).

### 4.5 Sección base de datos — SQLite y Microsoft SQL Server

| Componente | Versión | Rol |
|---|---|---|
| SQLite | incluido en Python | Base de datos de **desarrollo** (archivo `db.sqlite3`) |
| Microsoft SQL Server | 2019 / 2022 | Base de datos de **producción** (bloque preparado y comentado en `settings.py`) |
| mssql-django | 1.5 | Backend de Django para SQL Server |
| pyodbc | 5.x | Driver ODBC de Python requerido por mssql-django |
| Microsoft ODBC Driver for SQL Server | 18 | Driver del sistema operativo |

La conexión a SQL Server se configura con variables de entorno: `DB_NAME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_DRIVER`, `DB_TRUST_SERVER_CERT`.

### 4.6 Sección LLM — chatbot

| Componente | Versión | Rol |
|---|---|---|
| google-genai | 2.8.0 | SDK oficial **nuevo** de Google para Gemini (`from google import genai`). Sustituyó a `google-generativeai` |
| requests | 2.34.2 | Cliente HTTP hacia el backend local de Ollama |
| Ollama (opcional) | — | Servidor LLM local en `localhost:11434` cuando `LLM_BACKEND=local` |

El backend se selecciona con `LLM_BACKEND` (`gemini` | `local`); el modelo con `GEMINI_MODEL` (default `gemini-2.0-flash`) o `LOCAL_LLM_MODEL` (default `llama3.2`).

### 4.7 Requisitos de hardware (mínimos para desarrollo)

| Recurso | Mínimo |
|---|---|
| RAM | 4 GB |
| Almacenamiento | 2 GB libres |
| CPU | 2 núcleos |
| Sistema operativo | Windows 10/11, macOS 12+, Ubuntu 20.04+ |

### 4.8 Requisitos de red / servicios externos

- **RabbitMQ** activo en `localhost:5672` solo si `NOTIFICATIONS_ENABLED=True`.
- **Cuenta de correo Microsoft 365** con SMTP habilitado para notificaciones en producción.
- **API Key de Google Gemini** si se usa el chatbot con backend `gemini`.
- **Ollama** corriendo en `localhost:11434` si se usa el chatbot con backend `local`.
- **Servicio de predicciones de IA** (instancia EC2 externa) para el endpoint `/api_ia/v1/predictions/`. La URL está actualmente *hardcodeada* en `modulo_IA/views.py` (`PREDICTIONS_ENDPOINT`) — ver recomendaciones.

---

## 5. Arquitectura del sistema

### 5.1 Visión general

```
┌─────────────────────────────────────────────────────────┐
│                     Cliente (frontend)                  │
│             Cualquier app que consuma la API REST        │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS · JSON
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Django Backend (Bocar)                  │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │   users/   │  │  Bocar/    │  │   drf-spectacular  │ │
│  │ Auth JWT   │  │ settings + │  │  Swagger / ReDoc   │ │
│  │ Cookies    │  │   urls     │  └────────────────────┘ │
│  └────────────┘  └────────────┘                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │Industrializ. │  │Comercializ.  │  │  Proveedores  │  │
│  │  (Ind)       │  │  (Com)       │  │  (Pro)        │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  RFQ_Mold   │  │RFQ_Trimming  │  │  Asignaciones │  │
│  │  (modelos)  │  │  (modelos)   │  │  (modelos)    │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  historial  │  │notificaciones│  │   chatbot     │  │
│  │  (auditoría)│  │(Celery+SMTP) │  │ (LLM+guardr.) │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Evaluaciones│  │ General_RFQs │  │ Prov_RFQ_*    │  │
│  │(rating prov.)│  │(transversal) │  │(cost breakd.) │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                          │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐        ┌───────▼──────┐
│ SQLite │        │  RabbitMQ    │
│  (BD)  │        │  (broker)    │
└────────┘        └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │    Celery    │
                  │   Worker     │
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │  SMTP / M365 │
                  └──────────────┘
```

### 5.2 Patrón de autenticación

La autenticación usa JWT almacenados en **cookies HttpOnly** — el token nunca es accesible desde JavaScript, lo que mitiga ataques XSS. El flujo es:

1. El cliente hace `POST /auth/login/` con email y contraseña.
2. El servidor valida, genera un access token (15 min) y un refresh token (10 h).
3. Ambos tokens se envían como cookies HttpOnly en la respuesta — el body solo contiene datos del usuario.
4. En cada petición, `CookieJWTAuthentication` lee el access token de la cookie automáticamente.
5. Cuando el access token expira, el cliente llama a `POST /auth/refresh/` — el servidor emite un nuevo access token usando el refresh token.

Además, `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES` está fijado a `IsAuthenticated`: todo endpoint exige autenticación salvo que declare lo contrario explícitamente.

### 5.3 Flujo de estados de un RFQ

```
[En_Ind]  ──enviar──►  [En_Com]  ──asignar proveedores──►  [En_Pro]
                          ▲                                     │
                          │                                     │
               solicitud edición (Ind)            cotizaciones recibidas /
               aprobada por Com                   asignaciones cerradas
                          └─────────────────────────────┐      │
                                                        ▼      ▼
                                              [Cierre formal: complete=True,
                                               closed_at, closed_by, closure_reason]
```

Un RFQ también puede ser cancelado lógicamente (`logical_delete=True`) por un administrador en cualquier estado.

---

## 6. Diseño de módulos

| App | Prefijo de URL | Responsabilidad |
|---|---|---|
| `users` | `/auth/` | Autenticación JWT, modelo de usuario personalizado, roles y permisos |
| `RFQ_Mold` | `/api_mold/v1/` | Modelo, serializers y vistas de solo lectura / borrado lógico para RFQs tipo Mold |
| `RFQ_Trimming` | `/api_trimming/v1/` | Mismo rol que RFQ_Mold para el tipo Trimming |
| `Industrializacion` | `/api_industrializacion/v1/` | Creación, edición y envío de RFQs; solicitudes de regreso a edición |
| `Comercializacion` | `/api_comercializacion/v1/` | Listado de RFQs, asignación de proveedores, resolución de solicitudes, comparativa de precios y cierre formal |
| `Proveedores` | `/api_proveedores/v1/` | Listado de proveedores registrados (con rating) |
| `Asignaciones` | `/api_proveedores/v1/asginaciones/` | Respuesta de proveedores a asignaciones, borradores, extensiones de tiempo, cierre lazy de vencidas |
| `Prov_RFQ_Mold` | — | Modelos de cost breakdown completados por proveedores (tipo Mold), con archivos adjuntos (`Cost_Breakdown_Mold_File`) |
| `Prov_RFQ_Trimming` | — | Modelos de cost breakdown completados por proveedores (tipo Trimming), con archivos adjuntos (`Cost_Breakdown_Trimming_File`) |
| `General_RFQs` | `/api_general/v1/` | Conteo global de RFQs, borrado lógico y eliminación de borradores propios |
| `historial` | `/api_historial/v1/` | Consulta del historial de auditoría de cada RFQ |
| `notificaciones` | — | Tareas Celery que envían correos HTML en los eventos del flujo |
| `chatbot` | `/api_chatbot/v1/` | Endpoint de consulta en lenguaje natural con control de acceso por rol |
| `Evaluaciones` | `/api_evaluaciones/v1/` | Evaluación de proveedores por Compras: métricas automáticas + calificación manual → score ponderado que actualiza `Proveedor.rating` |
| `modulo_IA` | `/modulo-ia/` y `/api_ia/v1/` | Panel HTML de reentrenamiento y proxy REST (`/api_ia/v1/predictions/`) hacia el servicio externo de predicciones de IA |

### 6.1 Modelo de usuario (`users`)

El sistema usa un modelo personalizado `CustomUser` que extiende `AbstractUser` de Django. Los campos adicionales son:

- `email` — campo de login (reemplaza al `username` de Django).
- `role` — rol del usuario: `Ind`, `Com`, `Pro`, `IT` (Sistemas), o `SinRol`.
- `is_admin` — flag booleano independiente de `is_staff`. Define privilegios de administración dentro del dominio del negocio.

### 6.2 Módulo de notificaciones

Las notificaciones se envían de forma asíncrona usando Celery + RabbitMQ. El flag `NOTIFICATIONS_ENABLED` en las variables de entorno permite deshabilitar el envío sin modificar código. Las tareas definidas son:

1. `notificar_comercializacion` — RFQ enviado a Comercialización
2. `notificar_proveedores` — proveedores asignados a un RFQ
3. `notificar_cotizacion_recibida` — cotización recibida de un proveedor
4. `notificar_modificacion_rfq` — RFQ modificado / regreso a Ind
5. `notificar_cancelacion_solicitada` — solicitud de cancelación
6. `notificar_cancelacion_confirmada` — cancelación confirmada

Todas con reintentos automáticos (máx. 3, delay 60 s).

### 6.3 Módulo chatbot

El chatbot usa un patrón adaptador para el LLM, lo que permite cambiar entre Google Gemini (API externa, SDK `google-genai`) y Ollama (modelo local) con solo modificar una variable de entorno. El control de acceso se implementa con un doble guardrail:

- **Guardrail 1 (soft):** el system prompt inyecta el scope del usuario al LLM antes de procesar la pregunta.
- **Guardrail 2 (hard):** el processor valida en código que el tool solicitado por el LLM esté en la lista de herramientas permitidas para el rol del usuario, antes de ejecutar cualquier consulta a la base de datos.

### 6.4 Módulo de evaluación de proveedores

La app `Evaluaciones` permite a Comercialización calificar la entrega de cada proveedor
por asignación. Combina métricas calculadas automáticamente a partir de datos existentes
con una calificación manual, y produce un score ponderado (0–5):

| Criterio | Peso | Origen |
|---|---|---|
| Puntualidad | 40 % | Automático — `due_date` vs fecha de envío del cost breakdown (−0.5 pts por día de retraso; 0 si no envió) |
| Calidad de cotización | 30 % | Manual — Compras (1–5) |
| Comunicación | 20 % | Manual — Compras (1–5) |
| Sin solicitudes de extensión | 10 % | Automático — existencia de `SolicitudExtension` |

Cada evaluación es única por asignación (`unique_together`). Al guardarla,
`Proveedor.rating` se recalcula como el promedio de todos los scores del proveedor y
se registra el evento `EVALUACION_PROVEEDOR` en el historial. Detalle completo en
[evaluacion_proveedores.md](evaluacion_proveedores.md).

---

## 7. Diseño de interfaces y algoritmos

### 7.1 Interfaz REST

Todos los endpoints siguen la convención:

- **Prefijo de versión:** `/api_<area>/v1/<recurso>/`
- **Formato:** JSON en request y response.
- **Autenticación:** JWT en cookie HttpOnly (`access_token`). Sin este cookie, el servidor devuelve `401 Unauthorized`.
- **Parámetro de tipo:** Muchos endpoints requieren `?tipo=mold|trimming` como query parameter para operar sobre el modelo correcto.

La lista completa de endpoints con descripciones está en la [Guía de Usuario, sección 6](Guia_Usuario.md#6-referencia-de-endpoints). La documentación interactiva está disponible en:
- Swagger UI: `GET /schema/swagger/`
- ReDoc: `GET /schema/redoc/`

### 7.2 Algoritmo de control de acceso del chatbot

```
1. Request llega con cookie access_token
2. CookieJWTAuthentication extrae y valida el token
3. IsChatbotAllowed verifica que user.role != 'SinRol'
4. RoleContextBuilder construye allowed_tools según user.role:
      Ind  → {contar_rfqs, listar_rfqs, historial_rfq}
      Com  → {todo lo de Ind + contar/listar todos, proveedores, asignaciones}
      Pro  → {mis_asignaciones}
5. Se construye system_prompt con el scope del usuario
6. LLM recibe (system_prompt + historial + pregunta) → devuelve JSON plan
7. processor valida: plan.tool ∈ allowed_tools   ← Guardrail 2
8. Si válido: ejecuta tool() con filtros de ownership
9. LLM recibe resultados → genera respuesta en lenguaje natural
10. Response { answer, sources } devuelta al cliente
```

### 7.3 Máquina de estados del RFQ

Las transiciones válidas son:

| Estado actual | Acción | Estado siguiente | Quién puede hacerlo |
|---|---|---|---|
| `En_Ind` | Enviar a Comercialización | `En_Com` | `Ind` |
| `En_Com` | Asignar proveedores | `En_Pro` | `Com` |
| `En_Com` | Aprobar solicitud de edición | `En_Ind` | `Com` (Admin) |
| `En_Com` | Rechazar solicitud de edición | `En_Com` | `Com` (Admin) |
| `En_Pro` | Cierre formal (`complete=True`, con `closed_at`, `closed_by` y `closure_reason`) | `En_Pro` (cerrado) | `Com` |
| `En_Pro` (expirado) | Extender deadline (`PATCH /rfq/<id>/deadline/`); reabre asignaciones pendientes | `En_Pro` | `Com` |
| Cualquiera | Borrado lógico | `logical_delete=True` | `Ind` Admin o `Com` Admin |

El cierre formal requiere que todas las asignaciones activas del RFQ estén cerradas o
vencidas (las vencidas se cierran de forma lazy en ese momento) y registra el evento
`CIERRE_RFQ` en el historial.

Las transiciones se validan en las vistas correspondientes. No existe una máquina de estados formal en código; la lógica está en los serializers y views de `Industrializacion` y `Comercializacion`.

### 7.4 Algoritmo de cierre lazy de asignaciones

No existe tarea programada; el cierre de asignaciones vencidas ocurre en tres puntos (`Asignaciones/services.py`):

1. `close_expired_assignments()` — al listar `mis-asignaciones`, cierra en lote todas las vencidas no respondidas.
2. `close_if_expired(asignacion)` — al consultar el detalle de una asignación.
3. En `CerrarRFQView` — antes de validar el cierre formal de la RFQ.

Una extensión de plazo aprobada reabre la asignación (`reopen_assignment_for_extension`).

---

## 8. Problemas encontrados

> Esta sección será completada por el equipo con los problemas reales encontrados durante el desarrollo.

| # | Descripción del problema | Cómo se resolvió |
|---|---|---|
| 1 | _Por definir_ | _Por definir_ |
| 2 | _Por definir_ | _Por definir_ |

---

## 9. Pruebas del software

El proyecto incluye pruebas automatizadas en los módulos más críticos. Todas usan `APITestCase` de Django REST Framework, que levanta una base de datos en memoria para cada ejecución.

### 9.1 Módulos con pruebas

| App | Archivo | Qué cubre |
|---|---|---|
| `historial` | `historial/tests.py` | Registro correcto de eventos en el ciclo de vida de RFQs (creación, envío, asignación, edición, extensión, cancelación) |
| `notificaciones` | `notificaciones/tests.py` | Envío de correos en cada evento, comportamiento con `NOTIFICATIONS_ENABLED=False`, listas BCC, casos de destinatarios vacíos |
| `Industrializacion` | `Industrializacion/tests.py` | Creación, edición y envío de RFQs; validaciones de estado y permisos |
| `Asignaciones` | `Asignaciones/tests.py` | Cierre lazy de asignaciones vencidas, validación de cotizaciones sobre asignaciones cerradas y reapertura por extensión |
| `Comercializacion` | `Comercializacion/tests.py` | Visibilidad de RFQs con borrado lógico (admin vs usuario normal), extensión de deadline de RFQ expirada con reapertura de asignaciones, y validaciones (rol, fecha futura) |
| `Proveedores` | `Proveedores/tests.py` | Listado de proveedores y permisos de acceso |

> Las apps `users`, `chatbot`, `General_RFQs`, `RFQ_Mold`, `RFQ_Trimming`, `Evaluaciones` y
> `modulo_IA` tienen el archivo `tests.py` vacío (stub); agregar pruebas en estos módulos
> está listado en las recomendaciones.

### 9.2 Cómo ejecutar las pruebas

```bash
# Ejecutar todas las pruebas
python manage.py test

# Ejecutar pruebas de un módulo específico
python manage.py test historial
python manage.py test notificaciones
python manage.py test Asignaciones

# Con output detallado
python manage.py test --verbosity=2
```

### 9.3 Cobertura

No se usa una herramienta de medición de cobertura formal (como `coverage.py`). Se recomienda integrarla en trabajos futuros.

---

## 10. Recomendaciones

Las siguientes recomendaciones están dirigidas al equipo o persona que tome el mantenimiento del proyecto:

**Dependencias:**
El `requirements.txt` está versionado en la raíz, en UTF-8 y con versiones fijadas (issue B de `docs/security.md` resuelto). Al modificarlo, regenerarlo siempre en UTF-8 (en PowerShell: `pip freeze | Out-File requirements.txt -Encoding utf8`) para que git y Dependabot puedan leerlo. `mssql-django` y `pyodbc` se instalan aparte, solo en producción. La carpeta del entorno virtual (`venv/`) debe seguir fuera del repo (ya está en `.gitignore`).

**Base de datos:**
Migrar de SQLite a un motor cliente-servidor antes de cualquier despliegue en producción. El proyecto ya tiene preparado el bloque de configuración para Microsoft SQL Server en `settings.py` (comentado); PostgreSQL es una alternativa válida. SQLite no soporta acceso concurrente entre múltiples procesos, lo que genera conflictos cuando Celery y Django corren simultáneamente bajo carga.

**Variables de entorno:**
Nunca subir el archivo `.env` al repositorio. Usar el `.env.example` como referencia y configurar las variables directamente en el servidor o en el sistema de secrets del proveedor de nube.

**Seguridad pendiente:**
Los issues pendientes están catalogados en `docs/security.md` (IDs A–H, con severidad y archivos a revisar). Priorizar el A (race condition en creación de asignaciones — falta un `UniqueConstraint` en base de datos) y el C (falta CSRF explícito en endpoints mutantes con cookies).

**Typo en URL:**
La ruta `/api_proveedores/v1/asginaciones/` contiene un error tipográfico (`asginaciones` en lugar de `asignaciones`). Corregirlo requiere coordinar con el frontend para no romper la integración existente.

**Servicio de predicciones de IA:**
La URL del servicio externo de predicciones está *hardcodeada* en `modulo_IA/views.py` (`PREDICTIONS_ENDPOINT`, instancia EC2). Moverla a una variable de entorno (p. ej. `PREDICTIONS_ENDPOINT` en `.env`) para poder cambiarla sin tocar código y evitar exponer infraestructura en el repositorio.

**Chatbot en producción:**
Si se usa el chatbot con Google Gemini, monitorear el uso de la API Key para evitar cargos inesperados. Implementar un límite de rate en el endpoint `/api_chatbot/v1/query/` usando `ScopedRateThrottle` (igual que se hizo para el login).

**Notificaciones:**
Verificar que la cuenta Microsoft 365 tenga SMTP habilitado por el administrador del tenant antes de activar `NOTIFICATIONS_ENABLED=True` en producción.

**Pruebas:**
Agregar pruebas para los módulos `users`, `Comercializacion`, `chatbot` y `Evaluaciones`. Integrar `coverage.py` para medir cobertura y establecer un umbral mínimo en CI.

**Documentación de la API:**
El esquema Swagger (`/schema/swagger/`) se genera automáticamente con `drf-spectacular`. Mantener los decoradores `@extend_schema` en las vistas actualizados al modificar endpoints.

---

## 11. Siglas, acrónimos y glosario

### Siglas y acrónimos

| Término | Significado |
|---|---|
| **RFQ** | Request for Quotation — Solicitud de Cotización |
| **API** | Application Programming Interface — Interfaz de Programación de Aplicaciones |
| **REST** | Representational State Transfer — estilo arquitectónico para APIs sobre HTTP |
| **JWT** | JSON Web Token — formato estándar para tokens de autenticación firmados digitalmente |
| **DRF** | Django REST Framework — librería para construir APIs REST con Django |
| **ORM** | Object-Relational Mapper — capa de abstracción que traduce objetos Python a consultas SQL |
| **CORS** | Cross-Origin Resource Sharing — mecanismo que controla qué orígenes web pueden llamar a la API |
| **AMQP** | Advanced Message Queuing Protocol — protocolo del broker RabbitMQ |
| **SMTP** | Simple Mail Transfer Protocol — protocolo de envío de correos |
| **HTTP/HTTPS** | Hypertext Transfer Protocol (Secure) — protocolo de comunicación web (cifrado con TLS) |
| **XSS** | Cross-Site Scripting — ataque que inyecta scripts maliciosos en páginas web |
| **IDOR** | Insecure Direct Object Reference — vulnerabilidad que permite acceder a objetos de otros usuarios por ID |
| **CSRF** | Cross-Site Request Forgery — ataque que fuerza a un usuario autenticado a ejecutar acciones no deseadas |
| **LLM** | Large Language Model — modelo de lenguaje grande (ej: Gemini, Llama) |
| **ODBC** | Open Database Connectivity — estándar de conexión a bases de datos (usado para SQL Server) |
| **BCC** | Blind Carbon Copy — destinatario oculto en un correo electrónico |
| **CI/CD** | Continuous Integration / Continuous Deployment — automatización de pruebas y despliegue |
| **TEC** | Tecnológico de Monterrey |
| **Ind** | Industrialización — rol de usuario del área de Industrialización |
| **Com** | Comercialización — rol de usuario del área de Comercialización |
| **Pro** | Proveedor — rol de usuario externo proveedor de herramental |
| **IT** | Sistemas — rol de usuario para administración del sistema |

### Glosario

| Término | Definición |
|---|---|
| **Access token** | Token JWT de vida corta (15 minutos) que autoriza cada petición a la API. |
| **Refresh token** | Token JWT de vida larga (10 horas) que permite obtener un nuevo access token sin hacer login de nuevo. |
| **Cookie HttpOnly** | Cookie que el navegador envía automáticamente en cada petición pero que el código JavaScript no puede leer, protegiendo el token de ataques XSS. |
| **Borrado lógico** | Técnica de "eliminación" que marca un registro como inactivo (`logical_delete=True`) sin borrarlo físicamente de la base de datos, preservando el historial. |
| **Broker** | Servicio intermediario (RabbitMQ) que recibe tareas de Celery y las distribuye a los workers. |
| **Worker** | Proceso de Celery que ejecuta las tareas en segundo plano (ej: enviar correos). |
| **Cierre lazy** | Estrategia que cierra las asignaciones vencidas al momento de consultarlas, en lugar de usar una tarea programada. |
| **Cost breakdown** | Desglose detallado de costos que un proveedor completa como respuesta a una asignación de RFQ. |
| **Score** | Calificación ponderada (0–5) de la entrega de un proveedor en una asignación, calculada por el módulo de Evaluaciones. |
| **Rating** | Promedio histórico de los scores de un proveedor, almacenado en `Proveedor.rating`. |
| **Cierre formal** | Acción de Comercialización que marca un RFQ como completado (`complete=True`) registrando fecha, usuario y motivo de cierre. |
| **Guardrail** | Mecanismo de control que restringe o valida el comportamiento del sistema; en el chatbot, impide que el LLM acceda a datos fuera del scope del usuario. |
| **System prompt** | Instrucciones que se envían al LLM antes de la conversación para definir su comportamiento y contexto. |
| **Endpoint** | URL específica de la API que acepta peticiones HTTP de un tipo determinado (GET, POST, PATCH, DELETE). |
| **Serializer** | Componente de DRF que valida los datos de entrada y convierte objetos Python a JSON (y viceversa). |
| **Middleware** | Capa de software que intercepta todas las peticiones y respuestas HTTP para aplicar lógica transversal (ej: autenticación, CORS). |
| **Query parameter** | Parámetro incluido en la URL después de `?` (ej: `?tipo=mold`). |
| **Mold** | Tipo de RFQ relacionado con moldes de fundición a presión (die casting molds). |
| **Trimming** | Tipo de RFQ relacionado con herramental de recorte (trim dies). |
| **SameSite** | Atributo de cookie que controla en qué contextos cross-site el navegador la envía. `Lax` permite navegaciones de nivel superior; `Strict` la bloquea completamente en contextos externos. |
| **Rate limiting** | Mecanismo que limita el número de peticiones que un cliente puede hacer en un período de tiempo (ej: 5 intentos de login por minuto). |
| **Ollama** | Herramienta de código abierto que permite correr modelos LLM localmente y expone una API REST compatible. |
