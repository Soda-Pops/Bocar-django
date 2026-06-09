# **BOCAR DJANGO**

## **Avisos importantes**

>[!NOTE]
>
> Por cuestiones de facilidad al desarrollar he decido dejar la configuracion par ahacer un archivo ``.sqlite3``, no afecta nada en diseño, en cuanto se cambien `settings.py` a una instacia de mysql todo seguira funcionando normal

>[!NOTE]
>
> Queda pendiente reincoorporar archivo ``environmente.yml`` para ambiente virtual

>[!NOTE]
>
>Se esta considerando usar docker pero para todo el proyecto, aun no es nada seguro, pero esto se esta pensando para tener mayor facilidad de desarrollo, sin tener tantas bases de datos aisladas.

## **Rutas de navegacion del proyecto**

Hemos implentado **Swagger** como medio estandar de documetacion de **APIs**, asi mismo para un maneho de pruebas y al mismo tiempo, para poder vizualizar los endpoints de mejor manera, sin embargo hay dos rutas con las que ustedes navegaran en django.

### **API docs with swagger**  
[http://127.0.0.1:8000/schema/swagger/](http://127.0.0.1:8000/schema/swagger/)


### **Admin panel**
[http://127.0.0.1:8000/schema/swagger/](http://127.0.0.1:8000/schema/swagger/)

>[!IMPORTANT]
>
> Como no se esta subiendo el archivo de tipo ``.sqlite3``, no hay un usuario, es importante que lo creen ustedes mismo con el comando

```bash
python manage.py createsuperuser
```

---

## **Sistema de Notificaciones por Email**

El módulo `notificaciones/` envía correos automáticos vía **BCC** al ocurrir eventos clave en el flujo de RFQs. El envío es **asíncrono** (Celery + RabbitMQ).

| Evento | Destinatarios (BCC) | Estado |
|--------|---------------------|--------|
| RFQ enviada a revisión (avance a `En_Com`) | Comercialización | Conectado — `Industrializacion` (enviar a Comercialización) |
| RFQ enviada a proveedores (`En_Pro`) | Proveedor | Conectado — `Comercializacion` (crear asignaciones) |
| Cotización recibida | Comercialización | Conectado — `Asignaciones` (proveedor envía respuesta) |
| RFQ regresada a Industrialización (solicitud y aprobación de edición) | Comercialización / Industrialización | Conectado |
| RFQ eliminada lógicamente | Industrialización + Comercialización | Conectado |
| Solicitud de cancelación | Admins (`is_admin=True`) | Pendiente — el borrado lógico hoy es directo, no hay flujo de solicitud |

> El único evento pendiente (`notificar_cancelacion_solicitada`) ya tiene su función en
> `notificaciones/services.py` y `notificaciones/tasks.py`; falta construir el flujo de *solicitud*
> de cancelación (modelo/endpoint) que la dispare.
>
> Todas las notificaciones se disparan condicionadas a la variable de entorno
> `NOTIFICATIONS_ENABLED` (ver más abajo).

### Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `NOTIFICATIONS_ENABLED` | Activa/desactiva el envío de correos. Acepta `True`/`1`/`yes`. Con el flag apagado **no se encolan tareas** (no requiere broker). | `False` |
| `EMAIL_BACKEND` | Backend de correo de Django. En producción: `django.core.mail.backends.smtp.EmailBackend`. | `django.core.mail.backends.console.EmailBackend` (consola) |
| `BOCAR_EMAIL_USER` | Cuenta de correo de notificaciones | `CORREO@DOMINIO.COM` |
| `BOCAR_EMAIL_PASSWORD` | Contraseña de la cuenta | — |
| `CELERY_BROKER_URL` | URL del broker RabbitMQ | `amqp://guest:guest@localhost:5672//` |

### Configuración con archivo `.env` (recomendado)

El proyecto carga automáticamente las variables de entorno desde un archivo `.env`
en la raíz (vía `python-dotenv`, configurado en `Bocar/settings.py`). Es la forma
recomendada: se define una sola vez y la leen tanto `runserver` como el worker de Celery.

```bash
# 1. Copiar la plantilla
cp .env.example .env        # En PowerShell: Copy-Item .env.example .env

# 2. Editar .env con los valores reales (credenciales, flag, backend, etc.)

# 3. Levantar el proyecto normalmente — el .env se carga solo
python manage.py runserver
```

> [!IMPORTANT]
> El archivo `.env` **no se versiona** (está en `.gitignore`) porque contiene la
> contraseña del correo. Sube únicamente `.env.example` como plantilla.

Si no existe `.env`, el proyecto sigue funcionando con los valores por defecto
(backend de consola, notificaciones apagadas). También puedes definir las variables
directamente en el sistema/sesión (`export` en Linux/macOS, `$env:VAR` en PowerShell),
y tendrán prioridad sobre el `.env`.

### Puesta en marcha

```bash
# 1. Instalar dependencias (incluye python-dotenv y Celery)
pip install python-dotenv celery[librabbitmq]

# 2. Levantar RabbitMQ (Management UI en http://localhost:15672)
docker run -p 5672:5672 -p 15672:15672 rabbitmq:management

# 3. Correr el worker en una terminal separada
celery -A Bocar worker --loglevel=info
```

### Tests

```bash
python manage.py test notificaciones
```

Cubre (19 tests, sin broker requerido):
- Lógica de BCC/TO en `_enviar`, filtrado de destinatarios por rol y casos sin destinatarios.
- Ejecución de las tareas Celery con `.apply()` (síncrono).
- **Integración por endpoint:** que cada vista de avance de flujo encole su tarea con
  `NOTIFICATIONS_ENABLED=True` y **no** la encole con el flag apagado:
  - `Industrializacion` enviar a Comercialización → `notificar_comercializacion`
  - `Comercializacion` crear asignaciones → `notificar_proveedores`
  - `Asignaciones` enviar respuesta → `notificar_cotizacion_recibida`


