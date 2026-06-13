# Guía de Usuario — Cómo correr el proyecto Bocar

> **Versión 3.0 · 2026-06-12 · Equipo Soda-Pops**
> Guía práctica para instalar, configurar y ejecutar el backend.
> Para arquitectura y diseño ver [documentacion_tecnica.md](documentacion_tecnica.md); para la lista de endpoints ver [endpoints.md](endpoints.md).

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Clonar el proyecto](#2-clonar-el-proyecto)
3. [Crear y activar el ambiente virtual](#3-crear-y-activar-el-ambiente-virtual)
4. [Instalar dependencias](#4-instalar-dependencias)
5. [Configurar variables de entorno](#5-configurar-variables-de-entorno)
6. [Migraciones y base de datos](#6-migraciones-y-base-de-datos)
7. [Correr el servidor](#7-correr-el-servidor)
8. [Datos de prueba (opcional)](#8-datos-de-prueba-opcional)
9. [Notificaciones: RabbitMQ + Celery (opcional)](#9-notificaciones-rabbitmq--celery-opcional)
10. [Comandos frecuentes](#10-comandos-frecuentes)
11. [Problemas comunes](#11-problemas-comunes)

---

## 1. Requisitos previos

- Python 3.14+ → verificar con `python --version`
- Git
- Conda **o** el módulo `venv` de Python
- (Opcional) Docker — solo si vas a activar las notificaciones por correo

---

## 2. Clonar el proyecto

```bash
git clone <url-del-repositorio>
cd Bocar-django
```

---

## 3. Crear y activar el ambiente virtual

**Opción A — Conda:**

```bash
conda create -n bocar_django python=3.14 -y
conda activate bocar_django
```

**Opción B — venv:**

```bash
python -m venv .venv

# Activar en Windows (PowerShell):
.venv\Scripts\activate

# Activar en macOS / Linux:
source .venv/bin/activate
```

El prompt debe mostrar el prefijo `(bocar_django)` o `(.venv)`.

> Para salir del ambiente cuando termines: `conda deactivate` o `deactivate`.

---

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

Debe terminar con `Successfully installed ...` sin errores.

---

## 5. Configurar variables de entorno

```bash
# macOS / Linux:
cp .env.example .env

# Windows PowerShell:
Copy-Item .env.example .env
```

Edita `.env` y coloca una clave en `DJANGO_SECRET_KEY` (sin ella el servidor **no arranca**). Para generar una:

```bash
python -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits+'!@#%^&*(-_=+)') for _ in range(60)))"
```

El resto de las variables tienen defaults que funcionan para desarrollo (notificaciones apagadas, SQLite, correos a consola). Solo tócalas si vas a usar esa función:

| Variable | Tócala si... |
|---|---|
| `NOTIFICATIONS_ENABLED`, `EMAIL_BACKEND`, `BOCAR_EMAIL_*`, `CELERY_BROKER_URL` | ...vas a enviar correos reales (ver sección 9) |
| `LLM_BACKEND`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `LOCAL_LLM_*` | ...vas a usar el chatbot |
| `MAX_UPLOAD_SIZE_MB`, `MAX_FILES_PER_REQUEST` | ...necesitas cambiar los límites de archivos (default: 100 MB / 10 archivos) |

> ⚠️ Nunca subas el `.env` al repositorio — solo se versiona `.env.example`.

---

## 6. Migraciones y base de datos

```bash
# Aplicar las migraciones (crea db.sqlite3 la primera vez)
python manage.py migrate

# Crear un usuario administrador para entrar a /admin/
python manage.py createsuperuser
```

Si modificaste algún modelo y necesitas **generar** migraciones nuevas:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 7. Correr el servidor

```bash
python manage.py runserver
```

Debe mostrar `Starting development server at http://127.0.0.1:8000/`.

**URLs útiles:**

| URL | Qué es |
|---|---|
| `http://localhost:8000/schema/swagger/` | Swagger — probar todos los endpoints |
| `http://localhost:8000/schema/redoc/` | ReDoc — documentación de la API |
| `http://localhost:8000/admin/` | Panel de administración (crear usuarios y asignar roles) |

Para correr en otro puerto: `python manage.py runserver 8080`.

---

## 8. Datos de prueba (opcional)

El script `seed_chatbot_data.py` llena la BD con datos sintéticos (5 RFQ Mold, 3 Trimming, 1 proveedor, 2 asignaciones).

1. Primero crea estos usuarios desde `/admin/` con su rol:
   - `ind.usuario@bocar-test.mx` → rol `Ind`
   - `com.usuario@bocar-test.mx` → rol `Com`
   - `prov.alpha@bocar-test.mx` → rol `Pro`
2. Ejecuta:
   ```bash
   python seed_chatbot_data.py
   ```

---

## 9. Notificaciones: RabbitMQ + Celery (opcional)

Solo si pusiste `NOTIFICATIONS_ENABLED=True` en el `.env`.

```bash
# 1. Levantar RabbitMQ (consola de administración en http://localhost:15672, guest/guest)
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management

# 2. En una TERMINAL SEPARADA (con el ambiente activado), correr el worker
celery -A Bocar worker --loglevel=info
```

El worker debe mostrar `celery@<host> ready.`

> No se necesita Celery Beat — las asignaciones vencidas se cierran solas al consultarlas.

---

## 10. Comandos frecuentes

| Quiero... | Comando |
|---|---|
| Activar el ambiente | `conda activate bocar_django` o `.venv\Scripts\activate` |
| Correr el servidor | `python manage.py runserver` |
| Generar migraciones tras cambiar un modelo | `python manage.py makemigrations` |
| Aplicar migraciones | `python manage.py migrate` |
| Ver migraciones pendientes | `python manage.py showmigrations` |
| Crear admin | `python manage.py createsuperuser` |
| Actualizar dependencias tras un pull | `pip install -r requirements.txt` |

---

## 11. Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `KeyError: 'DJANGO_SECRET_KEY'` | Falta el `.env` o la variable | Sección 5 |
| `ModuleNotFoundError: No module named '...'` | Ambiente sin activar o dependencias sin instalar | Secciones 3 y 4 |
| `no such table: ...` | Migraciones sin aplicar | `python manage.py migrate` |
| `ConnectionRefusedError` en Celery | RabbitMQ apagado | Sección 9, o pon `NOTIFICATIONS_ENABLED=False` |
| Los correos no llegan | Flag apagado o backend de consola | Activa `NOTIFICATIONS_ENABLED` y configura SMTP en el `.env` |
| Error CORS en el navegador | Origen del frontend no permitido | Agrégalo a `CORS_ALLOWED_ORIGINS` en `settings.py` |
| El chatbot da error | `GEMINI_API_KEY` faltante u Ollama apagado | Revisa las variables del chatbot (sección 5) |
| `401` en todas las peticiones | Sin login o token expirado | `POST /auth/login/` o `POST /auth/refresh/` |
| `429` al hacer login | Más de 5 intentos por minuto | Espera un minuto |

---

> **¿Buscas la lista de endpoints?** → [endpoints.md](endpoints.md) o Swagger (`/schema/swagger/`)
> **¿Buscas la arquitectura, módulos y diseño?** → [documentacion_tecnica.md](documentacion_tecnica.md)
> **¿Buscas el flujo de negocio (RFQs, roles)?** → [flujo_completo.md](flujo_completo.md)
