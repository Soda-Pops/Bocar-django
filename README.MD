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

| Evento | Destinatarios (BCC) |
|--------|---------------------|
| RFQ enviada a revisión | Comercialización |
| RFQ regresada a Industrialización | Industrialización |
| RFQ eliminada lógicamente | Industrialización + Comercialización |
| RFQ enviada a proveedores | Proveedor |
| Cotización recibida | Comercialización |
| Solicitud de cancelación | Admins (`is_admin=True`) |

### Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `BOCAR_EMAIL_USER` | Cuenta de correo de notificaciones | `CORREO@DOMINIO.COM` |
| `BOCAR_EMAIL_PASSWORD` | Contraseña de la cuenta | — |
| `CELERY_BROKER_URL` | URL del broker RabbitMQ | `amqp://guest:guest@localhost:5672//` |

### Puesta en marcha

```bash
# 1. Instalar dependencias de Celery
pip install celery[librabbitmq]

# 2. Levantar RabbitMQ (Management UI en http://localhost:15672)
docker run -p 5672:5672 -p 15672:15672 rabbitmq:management

# 3. Correr el worker en una terminal separada
celery -A Bocar worker --loglevel=info
```

En **producción** cambiar `EMAIL_BACKEND` en `Bocar/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

### Tests

```bash
python manage.py test notificaciones
```

Cubre: lógica de BCC/TO en `_enviar`, filtrado de destinatarios por rol, casos sin destinatarios, y ejecución de tareas Celery (15 tests, sin broker requerido).
