# Guía de Usuario — Sistema Bocar

> Esta guía explica cómo instalar y ejecutar el proyecto, qué contiene cada módulo y qué hace cada endpoint disponible.

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Instalación con Conda](#2-instalación-con-conda)
3. [Instalación con virtualenv](#3-instalación-con-virtualenv)
4. [Configuración del entorno](#4-configuración-del-entorno)
5. [Ejecución del proyecto](#5-ejecución-del-proyecto)
6. [Descripción de módulos](#6-descripción-de-módulos)
7. [Endpoints disponibles](#7-endpoints-disponibles)

---

## 1. Requisitos previos

- Python 3.14 o superior instalado en el sistema.
- RabbitMQ instalado y corriendo (solo necesario si `NOTIFICATIONS_ENABLED=True`).
- Git para clonar el repositorio.
- Conda o pip disponibles en el sistema.

---

## 2. Instalación con Conda

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd Bocar-django

# 2. Crear un entorno conda con Python 3.14
conda create -n bocar_django python=3.14 -y

# 3. Activar el entorno
conda activate bocar_django

# 4. Instalar las dependencias principales
pip install django==6.0.4
pip install djangorestframework==3.17.1
pip install djangorestframework-simplejwt==5.5.1
pip install djoser==2.3.3
pip install drf-spectacular==0.29.0
pip install django-cors-headers==4.9.0
pip install django-countries==8.2.0
pip install celery==5.6.3
pip install python-dotenv==1.2.2
pip install requests==2.34.2

# 5. Instalar dependencia del chatbot (solo si se usa)
pip install google-generativeai==0.8.6

# 6. Configurar variables de entorno (ver sección 4)
cp .env.example .env
# Editar .env con los valores reales

# 7. Aplicar migraciones
python manage.py migrate

# 8. Crear superusuario (opcional, para acceder al admin)
python manage.py createsuperuser
```

Para desactivar el entorno cuando termines:
```bash
conda deactivate
```

---

## 3. Instalación con virtualenv

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd Bocar-django

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activar el entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS / Linux:
source .venv/bin/activate

# 4. Instalar las dependencias
pip install django==6.0.4
pip install djangorestframework==3.17.1
pip install djangorestframework-simplejwt==5.5.1
pip install djoser==2.3.3
pip install drf-spectacular==0.29.0
pip install django-cors-headers==4.9.0
pip install django-countries==8.2.0
pip install celery==5.6.3
pip install python-dotenv==1.2.2
pip install requests==2.34.2

# 5. Instalar dependencia del chatbot (solo si se usa)
pip install google-generativeai==0.8.6

# 6. Configurar variables de entorno (ver sección 4)
cp .env.example .env
# Editar .env con los valores reales

# 7. Aplicar migraciones
python manage.py migrate

# 8. Crear superusuario (opcional)
python manage.py createsuperuser
```

Para desactivar el entorno cuando termines:
```bash
deactivate
```

---

## 4. Configuración del entorno

Copia `.env.example` a `.env` y rellena los valores:

```bash
# Django
DJANGO_SECRET_KEY=genera-una-clave-aleatoria-larga
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Notificaciones por correo
NOTIFICATIONS_ENABLED=False
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
BOCAR_EMAIL_USER=correo@dominio.com
BOCAR_EMAIL_PASSWORD=

# Celery / RabbitMQ
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Chatbot
LLM_BACKEND=gemini
GEMINI_API_KEY=tu-api-key-de-google
GEMINI_MODEL=gemini-2.0-flash
```

Para generar una `DJANGO_SECRET_KEY` segura:
```bash
python -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits+'!@#%^&*(-_=+)') for _ in range(60)))"
```

---

## 5. Ejecución del proyecto

### Servidor de desarrollo

```bash
python manage.py runserver
```

El servidor queda disponible en `http://localhost:8000`.

### Worker de Celery (notificaciones)

Necesario solo si `NOTIFICATIONS_ENABLED=True`. Abrir una terminal separada:

```bash
celery -A Bocar worker --loglevel=info
```

### Celery Beat (tareas programadas)

Necesario para la tarea que cierra automáticamente asignaciones vencidas:

```bash
celery -A Bocar beat --loglevel=info
```

### Documentación interactiva

Con el servidor corriendo, acceder a:
- Swagger UI: `http://localhost:8000/schema/swagger/`
- ReDoc: `http://localhost:8000/schema/redoc/`
- Panel de administración: `http://localhost:8000/admin/`

---

## 6. Descripción de módulos

| Módulo | Descripción |
|---|---|
| `Bocar/` | Configuración central del proyecto: settings, URLs principales, configuración de Celery. |
| `users/` | Modelo de usuario personalizado con campo `role` e `is_admin`. Autenticación JWT en cookies HttpOnly. Endpoints de login, logout, refresh y perfil propio. |
| `Industrializacion/` | Lógica del área de Industrialización: crear RFQs (Mold y Trimming), editarlos mientras están en estado `En_Ind`, enviarlos a Comercialización, y solicitar su regreso para edición. |
| `Comercializacion/` | Lógica del área de Comercialización: ver todos los RFQs activos, asignar proveedores (transición a `En_Pro`), aprobar o rechazar solicitudes de edición, y resolver solicitudes de extensión de tiempo. |
| `RFQ_Mold/` | Modelo de base de datos del RFQ tipo Mold y sus archivos adjuntos. Endpoints de solo lectura y borrado lógico. |
| `RFQ_Trimming/` | Modelo de base de datos del RFQ tipo Trimming. Misma estructura que RFQ_Mold pero con campos propios del proceso de recorte. |
| `Proveedores/` | Modelo del proveedor externo (empresa, país, rating). Endpoint de listado. |
| `Asignaciones/` | Modelos de asignación de proveedores a RFQs. Endpoints para que los proveedores vean sus asignaciones, guarden borradores de respuesta, envíen cotizaciones definitivas y soliciten extensiones de tiempo. |
| `Prov_RFQ_Mold/` | Modelo de cost breakdown que el proveedor completa para una asignación de tipo Mold. |
| `Prov_RFQ_Trimming/` | Modelo de cost breakdown para asignaciones de tipo Trimming. |
| `General_RFQs/` | Vistas transversales: conteo global de RFQs por estado, borrado lógico unificado y eliminación de borradores propios. |
| `historial/` | Modelo de auditoría `RFQHistorial` y servicio `registrar_historial()`. Registra cada evento del ciclo de vida de un RFQ. Endpoint de consulta por tipo e ID de RFQ. |
| `notificaciones/` | Tareas Celery que envían correos HTML a los destinatarios correspondientes en cada evento del flujo. No tiene endpoints propios. |
| `chatbot/` | Endpoint de consulta en lenguaje natural. Verifica el rol del usuario, construye un contexto de acceso, llama al LLM dos veces (planificación e interpretación) y valida el acceso a datos con un doble guardrail antes de consultar la base de datos. |

---

## 7. Endpoints disponibles

### Autenticación — prefijo `/auth/`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/auth/login/` | Autentica al usuario con email y contraseña. Devuelve el access token y refresh token en cookies HttpOnly. |
| `POST` | `/auth/logout/` | Cierra la sesión del usuario eliminando las cookies de autenticación. |
| `POST` | `/auth/refresh/` | Emite un nuevo access token usando el refresh token almacenado en cookie. |
| `GET` | `/auth/me/` | Devuelve los datos del usuario actualmente autenticado. |

---

### RFQ Mold — prefijo `/api_mold/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_mold/v1/rfq-molds/` | Lista todos los RFQ Mold activos con campos resumidos. |
| `GET` | `/api_mold/v1/rfq-molds/<id>/` | Devuelve el detalle completo de un RFQ Mold por ID. |
| `PATCH` | `/api_mold/v1/rfq-molds/<id>/delete/` | Aplica borrado lógico a un RFQ Mold. Solo administradores. |

---

### RFQ Trimming — prefijo `/api_trimming/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_trimming/v1/rfq-trimmings/` | Lista todos los RFQ Trimming activos con campos resumidos. |
| `GET` | `/api_trimming/v1/rfq-trimmings/<id>/` | Devuelve el detalle completo de un RFQ Trimming por ID. |
| `PATCH` | `/api_trimming/v1/rfq-trimmings/<id>/delete/` | Aplica borrado lógico a un RFQ Trimming. Solo administradores. |

---

### General — prefijo `/api_general/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_general/v1/rfq-count/` | Devuelve el conteo de RFQs (Mold + Trimming) agrupados por estado para el usuario autenticado. Acepta `?user_id=<id>` para consultar por otro usuario. |
| `PATCH` | `/api_general/v1/rfq/<id>/delete/?tipo=mold\|trimming` | Borrado lógico unificado de un RFQ por tipo. |
| `DELETE` | `/api_general/v1/rfq/<id>/borrador/?tipo=mold\|trimming` | Elimina físicamente un RFQ en estado `En_Ind` creado por el usuario autenticado. |

---

### Proveedores — prefijo `/api_proveedores/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_proveedores/v1/proveedores/` | Lista todos los proveedores registrados en el sistema. |

---

### Asignaciones — prefijo `/api_proveedores/v1/asginaciones/`

> Nota: el prefijo contiene un error tipográfico (`asginaciones`) que se mantiene por compatibilidad.

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_proveedores/v1/asginaciones/mis-asignaciones/` | Devuelve las asignaciones propias del proveedor autenticado, separadas en pendientes y contestadas. |
| `GET` | `/api_proveedores/v1/asginaciones/detalle/<id>/?tipo=mold\|trimming` | Devuelve el detalle completo del RFQ asociado a una asignación específica. |
| `POST` | `/api_proveedores/v1/asginaciones/responder/<id>/?tipo=mold\|trimming` | Guarda un borrador del cost breakdown para una asignación. No marca la asignación como respondida. |
| `GET` | `/api_proveedores/v1/asginaciones/responder/<id>/detalle/?tipo=mold\|trimming` | Devuelve el borrador o la respuesta definitiva guardada para una asignación. |
| `PATCH` | `/api_proveedores/v1/asginaciones/responder/<id>/actualizar/?tipo=mold\|trimming` | Actualiza el borrador del cost breakdown. Solo disponible si aún está en estado borrador. |
| `POST` | `/api_proveedores/v1/asginaciones/responder/<id>/enviar/?tipo=mold\|trimming` | Convierte el borrador en respuesta definitiva y marca la asignación como respondida. |
| `POST` | `/api_proveedores/v1/asginaciones/extension/solicitar/<id>/?tipo=mold\|trimming` | El proveedor solicita una extensión de plazo para responder una asignación. |
| `PATCH` | `/api_proveedores/v1/asginaciones/extension/resolver/<id>/?tipo=mold\|trimming` | Comercialización aprueba o rechaza una solicitud de extensión de tiempo. |

---

### Comercialización — prefijo `/api_comercializacion/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_comercializacion/v1/rfqs/` | Lista todos los RFQs activos (Mold y Trimming) con el progreso de respuesta de cada proveedor asignado. |
| `GET` | `/api_comercializacion/v1/solicitudes/` | Lista las solicitudes pendientes de edición (de Industrialización) y las solicitudes de extensión de tiempo (de Proveedores). |
| `POST` | `/api_comercializacion/v1/asignaciones/crear/?tipo=mold\|trimming` | Asigna uno o varios proveedores a un RFQ y lo mueve al estado `En_Pro`. Ignora asignaciones duplicadas. |
| `PATCH` | `/api_comercializacion/v1/edit-requests/<id>/aprobar/?tipo=mold\|trimming` | Aprueba una solicitud de edición, regresando el RFQ al estado `En_Ind`. |
| `PATCH` | `/api_comercializacion/v1/edit-requests/<id>/rechazar/?tipo=mold\|trimming` | Rechaza una solicitud de edición, manteniendo el RFQ en `En_Com`. |
| `PATCH` | `/api_comercializacion/v1/extension/<id>/resolver/?tipo=mold\|trimming` | Aprueba o rechaza una solicitud de extensión de tiempo de un proveedor. |

---

### Industrialización — prefijo `/api_industrializacion/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_industrializacion/v1/rfqs/` | Lista los RFQs del área: borradores propios (En_Ind) y todos los demás estados. |
| `POST` | `/api_industrializacion/v1/rfq/?tipo=mold\|trimming` | Crea un nuevo RFQ del tipo indicado. Acepta archivos adjuntos como `multipart/form-data`. |
| `PATCH` | `/api_industrializacion/v1/rfq/<id>/?tipo=mold\|trimming` | Edita un RFQ existente. Solo disponible mientras el RFQ esté en estado `En_Ind`. |
| `POST` | `/api_industrializacion/v1/rfq/<id>/enviar/?tipo=mold\|trimming` | Envía el RFQ a Comercialización, cambiando su estado de `En_Ind` a `En_Com`. |
| `POST` | `/api_industrializacion/v1/edit-requests/?tipo=mold\|trimming` | Solicita regresar un RFQ de `En_Com` a `En_Ind` para hacer correcciones. |

---

### Historial — prefijo `/api_historial/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api_historial/v1/<tipo>/<rfq_id>/` | Devuelve el historial completo de eventos de un RFQ. `tipo` puede ser `mold` o `trimming`. |

---

### Chatbot — prefijo `/api_chatbot/v1/`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api_chatbot/v1/query/` | Recibe una pregunta en lenguaje natural y devuelve una respuesta basada en los datos accesibles según el rol del usuario autenticado. Acepta historial de conversación opcional. |

---

### Documentación y esquema

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/schema/swagger/` | Interfaz Swagger UI con todos los endpoints documentados y formularios de prueba interactivos. |
| `GET` | `/schema/redoc/` | Documentación ReDoc — alternativa más legible a Swagger. |
| `GET` | `/api/schema/` | Esquema OpenAPI en formato YAML/JSON para herramientas externas. |
| `GET` | `/admin/` | Panel de administración de Django. Requiere cuenta con `is_staff=True`. |
