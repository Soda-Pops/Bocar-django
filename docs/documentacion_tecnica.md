# Documentación Técnica — Sistema Bocar

> Versión del documento: 1.0  
> Fecha: 2026-06-08  
> Equipo: Soda-Pops — Proyecto académico TEC, 6° semestre

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

El sistema es un **backend REST** construido con Django y Django REST Framework. Su propósito es digitalizar y controlar el flujo de cotizaciones de herramental entre tres áreas internas: Industrialización, Comercialización y Proveedores. Cada área tiene un conjunto de permisos y acciones definidas que el sistema hace cumplir automáticamente.

El sistema es únicamente backend — no incluye frontend. Está diseñado para consumirse desde una aplicación web o móvil externa a través de su API REST.

---

## 2. Introducción

En entornos de manufactura, el proceso de solicitar cotizaciones a proveedores externos de herramental (moldes y recortes) involucra múltiples áreas y documentos. Sin un sistema centralizado, este proceso se gestiona por correo electrónico y hojas de cálculo, lo que dificulta el seguimiento, genera pérdida de información y no deja registro de auditoría.

Bocar resuelve este problema proveyendo una plataforma donde:

- El área de **Industrialización** crea y gestiona las solicitudes de cotización.
- El área de **Comercialización** las revisa, asigna proveedores y coordina el flujo.
- Los **Proveedores** reciben sus asignaciones, envían cotizaciones y solicitan extensiones de tiempo.

Cada acción queda registrada en un historial de auditoría. Las notificaciones relevantes se envían automáticamente por correo electrónico de forma asíncrona. El sistema incluye un chatbot inteligente que permite a cada usuario consultar la información a la que tiene acceso usando lenguaje natural.

---

## 3. Objetivo del sistema

**Objetivo general:**  
Proveer una plataforma centralizada para gestionar el ciclo de vida completo de las solicitudes de cotización de herramental (Mold y Trimming), garantizando control de acceso por rol, trazabilidad completa y comunicación automatizada entre las partes involucradas.

**Objetivos específicos:**

- Controlar el flujo de estados de un RFQ (`En_Ind → En_Com → En_Pro → Completado`) y hacer cumplir las transiciones válidas.
- Implementar control de acceso granular por rol de usuario (`Ind`, `Com`, `Pro`, `SinRol`).
- Registrar automáticamente cada evento del ciclo de vida en un historial de auditoría inmutable.
- Enviar notificaciones por correo electrónico de forma asíncrona cuando ocurren eventos relevantes.
- Proveer un chatbot conversacional que respete el nivel de acceso de cada usuario al consultar datos.
- Documentar y corregir vulnerabilidades de seguridad identificadas durante el desarrollo.

---

## 4. Requisitos del sistema

### 4.1 Requisitos de software

| Componente | Versión | Rol |
|---|---|---|
| Python | 3.14.4 | Lenguaje de programación principal |
| Django | 6.0.4 | Framework web |
| Django REST Framework (DRF) | 3.17.1 | API REST |
| djangorestframework-simplejwt | 5.5.1 | Autenticación JWT |
| djoser | 2.3.3 | Gestión de usuarios (registro, endpoints) |
| drf-spectacular | 0.29.0 | Generación de esquema OpenAPI / Swagger |
| django-cors-headers | 4.9.0 | Manejo de política CORS |
| django-countries | 8.2.0 | Campo de país en modelo Proveedor |
| Celery | 5.6.3 | Cola de tareas asíncronas (notificaciones) |
| Kombu | 5.6.2 | Capa de mensajería de Celery |
| amqp | 5.3.1 | Protocolo de mensajería para RabbitMQ |
| RabbitMQ | 3.x (recomendado) | Broker de mensajes para Celery |
| PyJWT | 2.12.1 | Codificación y validación de tokens JWT |
| python-dotenv | 1.2.2 | Carga de variables de entorno desde `.env` |
| requests | 2.34.2 | Peticiones HTTP (usado por LocalLLM/Ollama) |
| google-generativeai | 0.8.6 | Integración con la API de Google Gemini (chatbot) |
| SQLite | (incluido en Python) | Base de datos en desarrollo |
| mssql-django | 1.5 (recomendado) | Backend de Django para Microsoft SQL Server (producción) |
| pyodbc | 5.x (recomendado) | Driver ODBC de Python requerido por mssql-django |
| Microsoft ODBC Driver for SQL Server | 18 (recomendado) | Driver del sistema operativo para conectar con SQL Server |
| Microsoft SQL Server | 2019 / 2022 | Base de datos en producción (pendiente de implementar) |

### 4.2 Requisitos de hardware (mínimos para desarrollo)

| Recurso | Mínimo |
|---|---|
| RAM | 4 GB |
| Almacenamiento | 2 GB libres |
| CPU | 2 núcleos |
| Sistema operativo | Windows 10/11, macOS 12+, Ubuntu 20.04+ |

### 4.3 Requisitos de red / servicios externos

- **RabbitMQ** activo en `localhost:5672` para que funcione el envío de notificaciones por correo. Si no está disponible y `NOTIFICATIONS_ENABLED=False`, el sistema funciona sin él.
- **Cuenta de correo Microsoft 365** con SMTP habilitado para el envío de notificaciones.
- **API Key de Google Gemini** si se usa el chatbot con backend `gemini`.
- **Ollama** instalado y corriendo en `localhost:11434` si se usa el chatbot con backend `local`.

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

### 5.3 Flujo de estados de un RFQ

```
[En_Ind]  ──enviar──►  [En_Com]  ──asignar proveedores──►  [En_Pro]
                          ▲                                     │
                          │                                     │
               solicitud edición (Ind)            cotizaciones recibidas
               aprobada por Com                         │
                          └─────────────────────────────┘
                                        │
                               [Completado / Cerrado]
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
| `Comercializacion` | `/api_comercializacion/v1/` | Listado de RFQs, asignación de proveedores, aprobación/rechazo de solicitudes |
| `Proveedores` | `/api_proveedores/v1/` | Listado de proveedores registrados |
| `Asignaciones` | `/api_proveedores/v1/asginaciones/` | Respuesta de proveedores a asignaciones, borradores, extensiones de tiempo |
| `Prov_RFQ_Mold` | — | Modelos de cost breakdown completados por proveedores (tipo Mold) |
| `Prov_RFQ_Trimming` | — | Modelos de cost breakdown completados por proveedores (tipo Trimming) |
| `General_RFQs` | `/api_general/v1/` | Conteo global de RFQs, borrado lógico y eliminación de borradores propios |
| `historial` | `/api_historial/v1/` | Consulta del historial de auditoría de cada RFQ |
| `notificaciones` | — | Tareas Celery que envían correos HTML en los eventos del flujo |
| `chatbot` | `/api_chatbot/v1/` | Endpoint de consulta en lenguaje natural con control de acceso por rol |

### 6.1 Modelo de usuario (`users`)

El sistema usa un modelo personalizado `CustomUser` que extiende `AbstractUser` de Django. Los campos adicionales son:

- `email` — campo de login (reemplaza al `username` de Django).
- `role` — rol del usuario: `Ind`, `Com`, `Pro`, o `SinRol`.
- `is_admin` — flag booleano independiente de `is_staff`. Define privilegios de administración dentro del dominio del negocio.

### 6.2 Módulo de notificaciones

Las notificaciones se envían de forma asíncrona usando Celery + RabbitMQ. El flag `NOTIFICATIONS_ENABLED` en las variables de entorno permite deshabilitar el envío sin modificar código. Los eventos cubiertos son:

1. RFQ enviado a Comercialización
2. Proveedores asignados a un RFQ
3. Cotización recibida de un proveedor
4. RFQ modificado (regreso a Ind)
5. Solicitud de cancelación
6. Cancelación confirmada

### 6.3 Módulo chatbot

El chatbot usa un patrón adaptador para el LLM, lo que permite cambiar entre Google Gemini (API externa) y Ollama (modelo local) con solo modificar una variable de entorno. El control de acceso se implementa con un doble guardrail:

- **Guardrail 1 (soft):** el system prompt inyecta el scope del usuario al LLM antes de procesar la pregunta.
- **Guardrail 2 (hard):** el processor valida en código que el tool solicitado por el LLM esté en la lista de herramientas permitidas para el rol del usuario, antes de ejecutar cualquier consulta a la base de datos.

---

## 7. Diseño de interfaces y algoritmos

### 7.1 Interfaz REST

Todos los endpoints siguen la convención:

- **Prefijo de versión:** `/api_<area>/v1/<recurso>/`
- **Formato:** JSON en request y response.
- **Autenticación:** JWT en cookie HttpOnly (`access_token`). Sin este cookie, el servidor devuelve `401 Unauthorized`.
- **Parámetro de tipo:** Muchos endpoints requieren `?tipo=mold|trimming` como query parameter para operar sobre el modelo correcto.

La documentación interactiva completa está disponible en:
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
| Cualquiera | Borrado lógico | `logical_delete=True` | `Ind` Admin o `Com` Admin |

Las transiciones se validan en las vistas correspondientes. No existe una máquina de estados formal en código; la lógica está en los serializers y views de `Industrializacion` y `Comercializacion`.

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
| `users` | `users/tests.py` | Autenticación, login, logout, refresh de token |

### 9.2 Cómo ejecutar las pruebas

```bash
# Ejecutar todas las pruebas
python manage.py test

# Ejecutar pruebas de un módulo específico
python manage.py test historial
python manage.py test notificaciones
python manage.py test Industrializacion

# Con output detallado
python manage.py test --verbosity=2
```

### 9.3 Cobertura

No se usa una herramienta de medición de cobertura formal (como `coverage.py`). Se recomienda integrarla en trabajos futuros.

---

## 10. Recomendaciones

Las siguientes recomendaciones están dirigidas al equipo o persona que tome el mantenimiento del proyecto:

**Base de datos:**  
Migrar de SQLite a PostgreSQL antes de cualquier despliegue en producción. SQLite no soporta acceso concurrente entre múltiples procesos, lo que genera conflictos cuando Celery y Django corren simultáneamente bajo carga.

**Variables de entorno:**  
Nunca subir el archivo `.env` al repositorio. Usar el `.env.example` como referencia y configurar las variables directamente en el servidor o en el sistema de secrets del proveedor de nube.

**Seguridad pendiente:**  
Los ítems 5, 6, 9 y 12 del archivo `docs/security_issues.md` siguen pendientes de corrección. Priorizar el ítem 5 (`DEFAULT_PERMISSION_CLASSES`) ya que un error en él puede dejar endpoints sin protección sin ningún aviso en el código.

**Typo en URL:**  
La ruta `/api_proveedores/v1/asginaciones/` contiene un error tipográfico (`asginaciones` en lugar de `asignaciones`). Corregirlo requiere coordinar con el frontend para no romper la integración existente.

**Chatbot en producción:**  
Si se usa el chatbot con Google Gemini, monitorear el uso de la API Key para evitar cargos inesperados. Implementar un límite de rate en el endpoint `/api_chatbot/v1/query/` usando `ScopedRateThrottle` (igual que se hizo para el login).

**Notificaciones:**  
Verificar que la cuenta Microsoft 365 tenga SMTP habilitado por el administrador del tenant antes de activar `NOTIFICATIONS_ENABLED=True` en producción.

**Pruebas:**  
Agregar pruebas para los módulos `Comercializacion`, `Asignaciones` y `chatbot`. Integrar `coverage.py` para medir cobertura y establecer un umbral mínimo en CI.

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
| **SMTP** | Simple Mail Transfer Protocol — protocolo de envío de correos |
| **HTTP** | Hypertext Transfer Protocol — protocolo de comunicación web |
| **HTTPS** | HTTP Secure — HTTP cifrado con TLS |
| **XSS** | Cross-Site Scripting — ataque que inyecta scripts maliciosos en páginas web |
| **IDOR** | Insecure Direct Object Reference — vulnerabilidad que permite acceder a objetos de otros usuarios por ID |
| **CSRF** | Cross-Site Request Forgery — ataque que fuerza a un usuario autenticado a ejecutar acciones no deseadas |
| **LLM** | Large Language Model — modelo de lenguaje grande (ej: Gemini, Llama) |
| **BCC** | Blind Carbon Copy — destinatario oculto en un correo electrónico |
| **CI/CD** | Continuous Integration / Continuous Deployment — automatización de pruebas y despliegue |
| **TEC** | Tecnológico de Monterrey |
| **Ind** | Industrialización — rol de usuario del área de Industrialización |
| **Com** | Comercialización — rol de usuario del área de Comercialización |
| **Pro** | Proveedor — rol de usuario externo proveedor de herramental |

### Glosario

| Término | Definición |
|---|---|
| **Access token** | Token JWT de vida corta (15 minutos) que autoriza cada petición a la API. |
| **Refresh token** | Token JWT de vida larga (10 horas) que permite obtener un nuevo access token sin hacer login de nuevo. |
| **Cookie HttpOnly** | Cookie que el navegador envía automáticamente en cada petición pero que el código JavaScript no puede leer, protegiendo el token de ataques XSS. |
| **Borrado lógico** | Técnica de "eliminación" que marca un registro como inactivo (`logical_delete=True`) sin borrarlo físicamente de la base de datos, preservando el historial. |
| **Broker** | Servicio intermediario (RabbitMQ) que recibe tareas de Celery y las distribuye a los workers. |
| **Worker** | Proceso de Celery que ejecuta las tareas en segundo plano (ej: enviar correos). |
| **Cost breakdown** | Desglose detallado de costos que un proveedor completa como respuesta a una asignación de RFQ. |
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
