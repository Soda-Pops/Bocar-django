# Guía de Usuario — Sistema Bocar (Backend)

<!-- Estructura conforme a IEEE Std 1063-2001: IEEE Standard for Software User Documentation -->

## Datos de identificación

| Campo | Valor |
|---|---|
| **Título del documento** | Guía de Usuario — Sistema Bocar (Backend) |
| **Versión del documento** | 2.0 |
| **Fecha de publicación** | 2026-06-11 |
| **Producto de software** | Bocar Backend (API REST) |
| **Versión del software** | 1.0.0 (ver `SPECTACULAR_SETTINGS` en `Bocar/settings.py`) |
| **Organización emisora** | Equipo Soda-Pops — Tecnológico de Monterrey, 6° semestre |
| **Entorno operativo** | Windows 10/11, macOS 12+, Ubuntu 20.04+ · Python 3.14 |

### Historial de cambios

| Versión | Fecha | Descripción |
|---|---|---|
| 1.0 | 2026-06-08 | Versión inicial de la guía |
| 2.0 | 2026-06-11 | Reestructuración conforme a IEEE Std 1063-2001; secciones de instalación por componente; endpoints actualizados (Evaluaciones, comparativa, cierre formal); mensajes de error y glosario |

---

## Índice

1. [Introducción](#1-introducción)
2. [Información para el uso de esta documentación](#2-información-para-el-uso-de-esta-documentación)
3. [Concepto de operaciones](#3-concepto-de-operaciones)
4. [Procedimientos de instalación y puesta en marcha](#4-procedimientos-de-instalación-y-puesta-en-marcha)
5. [Procedimientos de uso general](#5-procedimientos-de-uso-general)
6. [Referencia de endpoints](#6-referencia-de-endpoints)
7. [Mensajes de error y resolución de problemas](#7-mensajes-de-error-y-resolución-de-problemas)
8. [Glosario](#8-glosario)
9. [Fuentes de información relacionadas](#9-fuentes-de-información-relacionadas)

---

## 1. Introducción

### 1.1 Audiencia

Esta guía está dirigida a:

- **Desarrolladores frontend** que consumirán la API REST.
- **Desarrolladores backend** que instalarán y ejecutarán el proyecto localmente.
- **Personal de QA** que probará los endpoints.

Se asume familiaridad básica con la línea de comandos, Python y el concepto de API REST. No se requiere conocimiento previo del dominio de negocio (RFQs).

### 1.2 Alcance

Cubre la instalación, configuración, ejecución y uso de la API del backend Bocar. **No cubre** el diseño interno del sistema (ver [documentacion_tecnica.md](documentacion_tecnica.md)) ni el desarrollo de un frontend.

### 1.3 Propósito del software

Bocar es un backend REST que digitaliza el ciclo de vida de las solicitudes de cotización (RFQ) de herramental — moldes (*Mold*) y recortes (*Trimming*) — entre tres áreas: **Industrialización** (crea las RFQs), **Comercialización/Compras** (las revisa, asigna proveedores, evalúa entregas y cierra) y **Proveedores** (cotizan). Incluye auditoría completa, notificaciones por correo, evaluación de proveedores y un chatbot de consulta en lenguaje natural.

---

## 2. Información para el uso de esta documentación

### 2.1 Cómo usar esta guía

- Si vas a **instalar el proyecto por primera vez**, sigue la sección 4 en orden.
- Si el proyecto ya está instalado y quieres **consumir la API**, ve directo a las secciones 5 y 6.
- Si encuentras un **error**, consulta la sección 7.

### 2.2 Convenciones de notación

| Convención | Significado |
|---|---|
| `texto en monoespaciado` | Comandos, rutas, nombres de archivos o valores literales |
| `<valor>` | Valor variable que el usuario debe sustituir |
| `?tipo=mold\|trimming` | Query parameter con dos valores posibles: `mold` o `trimming` |
| > ⚠️ **Advertencia** | Acción que puede causar pérdida de datos o fallas |
| > 📝 **Nota** | Información complementaria |

### 2.3 Mapa del conjunto de documentos

| Documento | Uso previsto | Audiencia |
|---|---|---|
| **Esta guía** | Instalar, ejecutar y consumir la API | Desarrolladores, QA |
| [documentacion_tecnica.md](documentacion_tecnica.md) | Arquitectura, diseño de módulos, pruebas | Mantenedores del backend |
| [flujo_completo.md](flujo_completo.md) | Flujo de negocio end-to-end con ejemplos | Desarrolladores frontend |
| [evaluacion_proveedores.md](evaluacion_proveedores.md) | Detalle del módulo de evaluación | Desarrolladores |
| [historial.md](historial.md) | Detalle del módulo de auditoría | Desarrolladores |
| [chatbot.md](chatbot.md) | Detalle del módulo de chatbot | Desarrolladores |
| [security.md](security.md) | Issues de seguridad pendientes | Mantenedores |

---

## 3. Concepto de operaciones

### 3.1 Roles de usuario

| Rol | Código | Qué puede hacer |
|---|---|---|
| Industrialización | `Ind` | Crear RFQs, editarlas en `En_Ind`, enviarlas a Comercialización, solicitar regreso a edición |
| Comercialización (Compras) | `Com` | Revisar RFQs, asignar proveedores, resolver solicitudes, comparar precios, cerrar RFQs, evaluar proveedores |
| Proveedor | `Pro` | Ver sus asignaciones, cotizar (cost breakdown), solicitar extensiones de plazo |
| Sistemas | `IT` | Administración del sistema |
| Sin rol | `SinRol` | Sin acceso a funcionalidad de negocio |

### 3.2 Flujo de una RFQ

```
 Industrialización          Comercialización              Proveedores
 ┌──────────────┐  enviar  ┌──────────────┐  asignar    ┌──────────────┐
 │   En_Ind     │ ───────► │   En_Com     │ ──────────► │   En_Pro     │
 │ (borrador)   │ ◄─────── │ (revisión)   │             │ (cotizando)  │
 └──────────────┘ edición  └──────────────┘             └──────┬───────┘
                           aprobada                            │ todas las
                                                               │ asignaciones
                                                               ▼ cerradas
                                                        ┌──────────────┐
                                                        │ Cierre formal │
                                                        │ (complete=True)│
                                                        └──────────────┘
```

1. Industrialización crea la RFQ con sus especificaciones técnicas y archivos adjuntos.
2. La envía a Comercialización (`En_Ind → En_Com`).
3. Comercialización asigna proveedores con una fecha límite (`En_Com → En_Pro`).
4. Cada proveedor guarda un borrador de su cotización y la envía definitivamente.
5. Comercialización compara precios, cierra formalmente la RFQ y evalúa la entrega de cada proveedor.
6. Cada acción queda registrada en el historial de auditoría y dispara notificaciones por correo (si están habilitadas).

---

## 4. Procedimientos de instalación y puesta en marcha

### 4.1 Requisitos previos

Antes de comenzar verifica que tienes:

- [ ] Python 3.14 o superior (`python --version`)
- [ ] Git (`git --version`)
- [ ] Conda **o** el módulo `venv` de Python
- [ ] (Opcional) Docker, para levantar RabbitMQ fácilmente — solo necesario si activarás notificaciones

### 4.2 Sección Python — entorno virtual y dependencias

> 📝 **Nota:** las dependencias están fijadas en el `requirements.txt` de la raíz del proyecto; las versiones de abajo provienen de ese archivo.

**Librerías del núcleo (Django):**

| Librería | Versión | Para qué sirve |
|---|---|---|
| `Django` | 6.0.6 | Framework web principal: ORM, migraciones, admin |
| `djangorestframework` | 3.17.1 | Construcción de la API REST (serializers, vistas, permisos) |
| `djangorestframework-simplejwt` | 5.5.1 | Tokens JWT de acceso y refresh (con blacklist de rotación) |
| `djoser` | 2.3.3 | Endpoints de gestión de usuarios (registro) |
| `drf-spectacular` | 0.29.0 | Genera el esquema OpenAPI y la UI de Swagger/ReDoc |
| `django-cors-headers` | 4.9.0 | Permite peticiones del frontend (Vite en `localhost:5173`) |
| `django-countries` | 9.0.0 | Campo de país en el modelo `Proveedor` |
| `django-jazzmin` | 3.0.4 | Tema visual del panel de administración de Django |
| `PyJWT` | 2.13.0 | Codificación/validación de JWT (dependencia de simplejwt) |
| `python-dotenv` | 1.2.2 | Carga las variables del archivo `.env` |

**Librerías del chatbot (opcionales si no se usa):**

| Librería | Versión | Para qué sirve |
|---|---|---|
| `google-genai` | 2.8.0 | SDK oficial nuevo de Google para la API de Gemini (sustituyó a `google-generativeai`) |
| `requests` | 2.34.2 | Llamadas HTTP al backend local de Ollama |

**Procedimiento — opción A: Conda**

1. Clona el repositorio y entra a la carpeta:
   ```bash
   git clone <url-del-repositorio>
   cd Bocar-django
   ```
2. Crea y activa el entorno:
   ```bash
   conda create -n bocar_django python=3.14 -y
   conda activate bocar_django
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
   *Resultado esperado:* pip termina con `Successfully installed ...` sin errores.

**Procedimiento — opción B: venv**

1. Clona el repositorio y entra a la carpeta (igual que arriba).
2. Crea y activa el entorno virtual:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate
   ```
   *Resultado esperado:* el prompt muestra el prefijo `(.venv)`.
3. Instala las dependencias (mismo comando `pip install` de la opción A).

> 📝 **Nota:** la carpeta del entorno (`venv/`, `env/`, `.venv/`) está en `.gitignore` — nunca se versiona.

### 4.3 Sección configuración — variables de entorno

1. Copia la plantilla:
   ```bash
   # macOS / Linux:
   cp .env.example .env
   # Windows PowerShell:
   Copy-Item .env.example .env
   ```
2. Genera una clave secreta y colócala en `DJANGO_SECRET_KEY`:
   ```bash
   python -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits+'!@#%^&*(-_=+)') for _ in range(60)))"
   ```
3. Revisa el resto de las variables:

| Variable | Descripción | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django. **Obligatoria** — el servidor no arranca sin ella | — |
| `DEBUG` | Modo debug (`True`/`False`) | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma | `localhost,127.0.0.1` |
| `NOTIFICATIONS_ENABLED` | Activa el envío de correos (requiere RabbitMQ + Celery) | `False` |
| `EMAIL_BACKEND` | Backend de correo; en desarrollo los correos se imprimen en consola | consola |
| `BOCAR_EMAIL_USER` / `BOCAR_EMAIL_PASSWORD` | Credenciales SMTP (Microsoft 365) | — |
| `CELERY_BROKER_URL` | URL del broker RabbitMQ | `amqp://guest:guest@localhost:5672//` |
| `LLM_BACKEND` | Backend del chatbot: `gemini` o `local` (Ollama) | `gemini` |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | Credenciales y modelo de Gemini | — / `gemini-2.0-flash` |
| `LOCAL_LLM_URL` / `LOCAL_LLM_MODEL` | URL y modelo de Ollama | `http://localhost:11434` / `llama3.2` |
| `MAX_UPLOAD_SIZE_MB` / `MAX_FILES_PER_REQUEST` | Límites de subida de archivos | `100` / `10` |

> ⚠️ **Advertencia:** nunca subas el archivo `.env` al repositorio — contiene credenciales. Solo se versiona `.env.example`.

### 4.4 Sección base de datos — SQLite y Microsoft SQL Server

**Desarrollo (SQLite — default, sin configuración adicional):**

1. Aplica las migraciones:
   ```bash
   python manage.py migrate
   ```
   *Resultado esperado:* lista de migraciones con `OK` y se crea el archivo `db.sqlite3`.
2. Crea un superusuario para acceder al panel de administración:
   ```bash
   python manage.py createsuperuser
   ```

**Producción (Microsoft SQL Server — opcional):**

| Componente | Versión | Para qué sirve |
|---|---|---|
| `mssql-django` | 1.5 | Backend de Django para SQL Server |
| `pyodbc` | 5.x | Driver ODBC de Python |
| Microsoft ODBC Driver for SQL Server | 18 | Driver del sistema operativo |
| Microsoft SQL Server | 2019/2022 | Motor de base de datos |

1. Instala las dependencias: `pip install mssql-django pyodbc`.
2. Instala el ODBC Driver 18 en el sistema operativo.
3. En `Bocar/settings.py`, comenta el bloque `DATABASES` de SQLite y descomenta el bloque de `mssql`.
4. Define en `.env`: `DB_NAME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`.
5. Ejecuta `python manage.py migrate`.

> ⚠️ **Advertencia:** SQLite no soporta acceso concurrente de múltiples procesos. No lo uses en producción con Celery activo.

### 4.5 Sección RabbitMQ — broker de mensajes

Solo necesario si `NOTIFICATIONS_ENABLED=True`.

| Componente | Versión | Para qué sirve |
|---|---|---|
| RabbitMQ | 3.x | Broker: recibe las tareas de correo y las entrega al worker |
| `amqp` | 5.3.1 | Protocolo de mensajería (instalado con Celery) |

**Procedimiento (con Docker):**

1. Levanta el contenedor:
   ```bash
   docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management
   ```
2. Verifica que está corriendo abriendo la consola de administración en `http://localhost:15672` (usuario/contraseña por defecto: `guest`/`guest`).
   *Resultado esperado:* la página de login de RabbitMQ Management carga correctamente.

### 4.6 Sección Celery — worker de tareas asíncronas

| Componente | Versión | Para qué sirve |
|---|---|---|
| `celery` | 5.6.3 | Ejecuta en segundo plano el envío de correos de notificación |
| `kombu` | 5.6.2 | Capa de mensajería de Celery (se instala automáticamente) |

**Procedimiento:**

1. Con RabbitMQ corriendo, abre una **terminal separada** con el entorno virtual activado.
2. Inicia el worker:
   ```bash
   celery -A Bocar worker --loglevel=info
   ```
   *Resultado esperado:* el log muestra `celery@<host> ready.` y la lista de tareas registradas (`notificar_comercializacion`, `notificar_proveedores`, etc.).

> 📝 **Nota:** no se requiere Celery Beat. Las asignaciones vencidas se cierran de forma automática (lazy) cuando se consultan o al cerrar formalmente una RFQ.

### 4.7 Datos de prueba (opcional)

El script `seed_chatbot_data.py` (raíz del proyecto) llena la base de datos con datos sintéticos: 5 RFQ Mold, 3 RFQ Trimming, un perfil de proveedor y 2 asignaciones.

1. Crea primero estos usuarios desde `/admin/` con su rol correspondiente:
   - `ind.usuario@bocar-test.mx` (rol `Ind`)
   - `com.usuario@bocar-test.mx` (rol `Com`)
   - `prov.alpha@bocar-test.mx` (rol `Pro`)
2. Ejecuta el script:
   ```bash
   python seed_chatbot_data.py
   ```
   *Resultado esperado:* mensaje de confirmación con los registros creados.

### 4.8 Ejecución del servidor

1. Con el entorno activado y el `.env` configurado, inicia el servidor:
   ```bash
   python manage.py runserver
   ```
   *Resultado esperado:* `Starting development server at http://127.0.0.1:8000/`.
2. Verifica la instalación abriendo `http://localhost:8000/schema/swagger/`.
   *Resultado esperado:* carga la interfaz Swagger UI con todos los endpoints. **Este es el último paso de la instalación.**

---

## 5. Procedimientos de uso general

### 5.1 Autenticación (inicio de sesión)

La API usa JWT en **cookies HttpOnly**: tras el login, el navegador/cliente envía las cookies automáticamente; el frontend nunca manipula el token.

1. Envía las credenciales:
   ```
   POST /auth/login/
   Content-Type: application/json

   { "email": "usuario@dominio.com", "password": "su-contraseña" }
   ```
   *Resultado esperado:* `200 OK` con los datos del usuario en el body; las cookies `access_token` (15 min) y `refresh_token` (10 h) se establecen automáticamente.
2. Realiza cualquier petición a la API — las cookies viajan solas (en `fetch`/`axios` usa `credentials: 'include'` / `withCredentials: true`).
3. Cuando el access token expire (respuesta `401`), renueva con:
   ```
   POST /auth/refresh/
   ```
4. Para cerrar sesión:
   ```
   POST /auth/logout/
   ```
   *Resultado esperado:* `200 OK`; las cookies quedan invalidadas. **Fin del procedimiento.**

> 📝 **Nota:** el login tiene límite de **5 intentos por minuto**. Al excederlo la API responde `429 Too Many Requests`.

### 5.2 Operaciones con parámetro de tipo

La mayoría de los endpoints de negocio operan sobre RFQs de tipo *Mold* o *Trimming* y **requieren** el query parameter `?tipo=mold` o `?tipo=trimming`. Si se omite o es inválido, la API responde `400` con el mensaje `"El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."`

### 5.3 Carga de archivos

La creación/edición de RFQs y la respuesta de los proveedores (cost breakdown, campo `archivos`) aceptan archivos adjuntos vía `multipart/form-data`. Límites por defecto: **100 MB por request** y **10 archivos máximo** (configurables con `MAX_UPLOAD_SIZE_MB` y `MAX_FILES_PER_REQUEST`).

---

## 6. Referencia de endpoints

> Documentación interactiva siempre actualizada: **Swagger UI** en `/schema/swagger/` y **ReDoc** en `/schema/redoc/`. Todos los endpoints requieren autenticación excepto `POST /auth/login/`.

### 6.1 Autenticación — `/auth/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `POST` | `/auth/login/` | público | Autentica con email y contraseña; establece cookies HttpOnly con los tokens |
| `POST` | `/auth/logout/` | cualquiera | Cierra sesión e invalida el refresh token |
| `POST` | `/auth/refresh/` | cualquiera | Emite un nuevo access token usando la cookie de refresh |
| `GET` | `/auth/me/` | cualquiera | Devuelve los datos del usuario autenticado (id, email, rol, is_admin) |

### 6.2 RFQ Mold — `/api_mold/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfq-molds/` | autenticado | Lista los RFQ Mold activos con campos resumidos |
| `GET` | `/rfq-molds/<id>/` | autenticado | Detalle completo de un RFQ Mold |
| `PATCH` | `/rfq-molds/<id>/delete/` | `Com` admin | Borrado lógico del RFQ |

### 6.3 RFQ Trimming — `/api_trimming/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfq-trimmings/` | autenticado | Lista los RFQ Trimming activos con campos resumidos |
| `GET` | `/rfq-trimmings/<id>/` | autenticado | Detalle completo de un RFQ Trimming |
| `PATCH` | `/rfq-trimmings/<id>/delete/` | `Com` admin | Borrado lógico del RFQ |

### 6.4 General — `/api_general/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfq-count/` | autenticado | Conteo de RFQs (Mold + Trimming) por estado; acepta `?user_id=<id>` |
| `PATCH` | `/rfq/<id>/delete/?tipo=mold\|trimming` | admin | Borrado lógico unificado por tipo |
| `DELETE` | `/rfq/<id>/borrador/?tipo=mold\|trimming` | `Ind` | Elimina físicamente un borrador propio en `En_Ind` |

### 6.5 Industrialización — `/api_industrializacion/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfqs/` | `Ind` | Lista RFQs: borradores propios (`En_Ind`) y todos los demás estados |
| `POST` | `/rfq/?tipo=mold\|trimming` | `Ind` | Crea una RFQ; acepta archivos en `multipart/form-data` |
| `PATCH` | `/rfq/<id>/?tipo=mold\|trimming` | `Ind` | Edita una RFQ (solo en estado `En_Ind`) |
| `POST` | `/rfq/<id>/enviar/?tipo=mold\|trimming` | `Ind` | Envía la RFQ a Comercialización (`En_Ind → En_Com`) |
| `POST` | `/edit-requests/?tipo=mold\|trimming` | `Ind` | Solicita regresar una RFQ de `En_Com` a `En_Ind` |

### 6.6 Comercialización — `/api_comercializacion/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfqs/` | `Com` | Lista todos los RFQs activos con progreso de respuesta de proveedores |
| `GET` | `/solicitudes/` | `Com` | Solicitudes pendientes: de edición (Ind) y de extensión (Pro) |
| `POST` | `/asignaciones/crear/?tipo=mold\|trimming` | `Com` | Asigna proveedores a una RFQ y la mueve a `En_Pro`; omite duplicados |
| `PATCH` | `/edit-requests/<id>/aprobar/?tipo=mold\|trimming` | `Com` admin | Aprueba la solicitud de edición; la RFQ vuelve a `En_Ind` |
| `PATCH` | `/edit-requests/<id>/rechazar/?tipo=mold\|trimming` | `Com` admin | Rechaza la solicitud; la RFQ permanece en `En_Com` |
| `PATCH` | `/extension/<id>/resolver/?tipo=mold\|trimming` | `Com` | Aprueba/rechaza una extensión de plazo; si aprueba, actualiza el `due_date` |
| `GET` | `/rfq/<id>/comparativa/?tipo=mold\|trimming` | `Com` | Comparativa de precios de los proveedores que ya respondieron (desglose + total) |
| `POST` | `/rfq/<id>/cerrar/?tipo=mold\|trimming` | `Com` | Cierre formal de la RFQ con motivo (`closure_reason`); requiere asignaciones cerradas/vencidas |
| `PATCH` | `/rfq/<id>/deadline/?tipo=mold\|trimming` | `Com` | Extiende el deadline de una RFQ expirada (la nueva fecha debe ser futura) y reabre las asignaciones pendientes |

### 6.7 Proveedores — `/api_proveedores/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/proveedores/` | `Com` | Lista todos los proveedores registrados (incluye su `rating`) |

### 6.8 Asignaciones — `/api_proveedores/v1/asginaciones/`

> 📝 **Nota:** el prefijo contiene un error tipográfico histórico (`asginaciones`) que se conserva por compatibilidad con el frontend.

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/mis-asignaciones/` | `Pro` | Asignaciones propias, separadas en pendientes y contestadas |
| `GET` | `/detalle/<id>/?tipo=mold\|trimming` | `Pro` | Detalle completo de la RFQ de una asignación propia |
| `POST` | `/responder/<id>/?tipo=mold\|trimming` | `Pro` | Guarda el cost breakdown como **borrador** (no marca respondida); acepta archivos adjuntos (`archivos`, multipart) |
| `GET` | `/responder/<id>/detalle/?tipo=mold\|trimming` | `Pro` | Devuelve el borrador o la respuesta enviada |
| `PATCH` | `/responder/<id>/actualizar/?tipo=mold\|trimming` | `Pro` | Actualiza el borrador (solo si sigue en `draft`) |
| `POST` | `/responder/<id>/enviar/?tipo=mold\|trimming` | `Pro` | Envío definitivo (`draft → submitted`); irreversible |
| `POST` | `/extension/solicitar/<id>/?tipo=mold\|trimming` | `Pro` | Solicita extensión de plazo (una pendiente a la vez) |
| `PATCH` | `/extension/resolver/<id>/?tipo=mold\|trimming` | `Com` | (Legacy) Resuelve una extensión — preferir el endpoint de Comercialización |

### 6.9 Evaluaciones — `/api_evaluaciones/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `POST` | `/crear/?tipo=mold\|trimming` | `Com` | Evalúa la entrega de una asignación. Body: `asignacion_id`, `calidad_cotizacion` (1–5), `comunicacion` (1–5), `comentarios`. Las métricas de puntualidad/extensiones/envío se calculan solas. Devuelve el `score` y el nuevo rating del proveedor |
| `GET` | `/proveedor/<id>/` | `Com` | Historial de evaluaciones + resumen: rating, % puntualidad, % sin extensiones, promedios |

### 6.10 Historial — `/api_historial/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/<tipo>/<rfq_id>/` | autenticado | Timeline de eventos de una RFQ. Filtros: `?evento=`, `?actor=`, `?desde=`, `?hasta=`. Paginación: `?page=`, `?page_size=` (máx. 100) |

### 6.11 Chatbot — `/api_chatbot/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `POST` | `/query/` | con rol asignado | Pregunta en lenguaje natural; responde solo con datos accesibles para el rol del usuario |

### 6.12 Módulo IA — `/modulo-ia/` y `/api_ia/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET`/`POST` | `/modulo-ia/` | autenticado | Panel HTML para solicitar reentrenamiento del módulo de IA (no es API REST) |
| `POST` | `/api_ia/v1/predictions/` | autenticado | Proxy hacia el servicio externo de predicciones de IA. Reenvía el body JSON tal cual. Responde `504` si el servicio externo no contesta en 30 s y `502` si no está disponible |

### 6.13 Documentación y administración

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/schema/swagger/` | Swagger UI interactivo |
| `GET` | `/schema/redoc/` | Documentación ReDoc |
| `GET` | `/api/schema/` | Esquema OpenAPI (YAML/JSON) |
| `GET` | `/admin/` | Panel de administración de Django (requiere `is_staff=True`) |

---

## 7. Mensajes de error y resolución de problemas

### 7.1 Códigos de respuesta de la API

| Código | Causa | Acción correctiva |
|---|---|---|
| `400 Bad Request` | Falta `?tipo=` o body inválido. Mensaje típico: `"El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."` | Agrega el query param o corrige los campos indicados en el detalle del error |
| `401 Unauthorized` | Cookie `access_token` ausente o expirada | Llama a `POST /auth/refresh/`; si también falla, vuelve a hacer login |
| `403 Forbidden` | Rol sin permiso, o plazo vencido: `"El plazo de esta asignación ha vencido. Solicita una extensión de tiempo."` | Verifica el rol del usuario; el proveedor puede solicitar extensión |
| `404 Not Found` | Recurso inexistente o no pertenece al usuario: `"Asignación no encontrada o no pertenece a este proveedor."` | Verifica el id y que el recurso pertenezca al usuario autenticado |
| `409 Conflict` | Recurso duplicado: `"Ya existe un borrador o respuesta para esta asignación."` / `"Esta respuesta ya fue enviada."` | Usa el endpoint de actualización (`PATCH`) en lugar de crear de nuevo |
| `429 Too Many Requests` | Más de 5 intentos de login por minuto | Espera un minuto y reintenta |

### 7.2 Problemas de instalación y arranque

| Síntoma | Causa probable | Solución |
|---|---|---|
| `KeyError: 'DJANGO_SECRET_KEY'` al arrancar | Falta el archivo `.env` o la variable | Sigue el procedimiento 4.3 |
| `ModuleNotFoundError: No module named 'corsheaders'` (u otro) | Entorno virtual sin activar o dependencias sin instalar | Activa el entorno y repite el `pip install` de la sección 4.2 |
| `ConnectionRefusedError` en el worker de Celery | RabbitMQ no está corriendo | Levanta RabbitMQ (sección 4.5) o pon `NOTIFICATIONS_ENABLED=False` |
| Los correos no llegan | `NOTIFICATIONS_ENABLED=False` o backend de consola | Activa el flag y configura `EMAIL_BACKEND` SMTP con credenciales reales |
| Error CORS en el navegador | El frontend corre en un origen no listado | Agrega el origen a `CORS_ALLOWED_ORIGINS` en `settings.py` |
| El chatbot responde error de API | `GEMINI_API_KEY` ausente/inválida, u Ollama apagado | Revisa las variables de la sección 4.3 según el `LLM_BACKEND` elegido |

### 7.3 Reporte de problemas

Reporta bugs o sugerencias abriendo un **issue** en el repositorio de GitHub del equipo (Soda-Pops), incluyendo: endpoint llamado, body enviado, respuesta recibida y comportamiento esperado.

---

## 8. Glosario

| Término | Definición |
|---|---|
| **RFQ** | *Request for Quotation* — solicitud de cotización de herramental (Mold o Trimming) |
| **Mold** | Tipo de RFQ para moldes de fundición a presión |
| **Trimming** | Tipo de RFQ para herramental de recorte |
| **Asignación** | Vínculo entre una RFQ y un proveedor, con fecha límite para cotizar |
| **Cost breakdown** | Desglose de costos que el proveedor llena como cotización |
| **Borrador (draft)** | Cost breakdown guardado pero aún no enviado; es editable |
| **Extensión** | Solicitud del proveedor para ampliar su fecha límite |
| **Cierre formal** | Acción de Comercialización que marca la RFQ como completada, con motivo y registro de quién y cuándo |
| **Evaluación** | Calificación de la entrega de un proveedor (score 0–5) que alimenta su rating |
| **Rating** | Promedio histórico de los scores de un proveedor |
| **Borrado lógico** | Marca `logical_delete=True` sin eliminar el registro físicamente |
| **Access / Refresh token** | JWT de corta (15 min) y larga (10 h) duración, en cookies HttpOnly |
| **Broker** | Servicio (RabbitMQ) que entrega las tareas de correo al worker de Celery |
| **Worker** | Proceso de Celery que ejecuta las tareas en segundo plano |

---

## 9. Fuentes de información relacionadas

- **Swagger UI** (`/schema/swagger/`) — referencia interactiva generada del código; siempre refleja la versión desplegada.
- [documentacion_tecnica.md](documentacion_tecnica.md) — arquitectura y diseño (informativo).
- [flujo_completo.md](flujo_completo.md), [flujo_industrializacion.md](flujo_industrializacion.md), [flujo_comercializacion.md](flujo_comercializacion.md), [flujo_proveedor.md](flujo_proveedor.md) — flujos de negocio por área (informativo).
- [evaluacion_proveedores.md](evaluacion_proveedores.md), [historial.md](historial.md), [chatbot.md](chatbot.md) — detalle por módulo (informativo).
- [security.md](security.md) — issues de seguridad pendientes (normativo para mantenedores).
- [plan_de_pruebas.md](plan_de_pruebas.md) — plan de pruebas del sistema (informativo).
