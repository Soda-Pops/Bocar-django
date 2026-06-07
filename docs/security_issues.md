# Problemas de seguridad identificados

> Revisión realizada el 2026-06-05.
> Archivo de referencia principal: `Bocar/settings.py`, `users/authentication.py`,
> `users/views.py`, `users/permissions.py`.

---

## Resumen rápido

| # | Severidad | Problema | Estado |
|---|---|---|---|
| 1 | 🔴 Crítico | `SECRET_KEY` hardcodeado en el código fuente | ✅ Corregido |
| 2 | 🔴 Crítico | `DEBUG` y `ALLOWED_HOSTS` hardcodeados | ✅ Corregido |
| 3 | 🟠 Alto | Duración de cookie y token JWT desincronizados | ✅ Corregido |
| 4 | 🟠 Alto | Sin rate limiting en `/auth/login/` | ✅ Corregido |
| 5 | 🟠 Alto | Sin `DEFAULT_PERMISSION_CLASSES` en DRF | ⏳ Pendiente |
| 6 | 🟡 Medio | Cambios de rol no se aplican hasta que expira el token (hasta 10h) | ⏳ Pendiente |
| 7 | 🟡 Medio | Sin permisos a nivel de objeto — riesgo de IDOR | ✅ Corregido |
| 8 | 🟡 Medio | `IsAdminUser` incorrecto en la config de `djoser` | ✅ Corregido |
| 9 | 🟢 Bajo | `SameSite=Lax` en lugar de `Strict` | ⏳ Pendiente |
| 10 | 🟢 Bajo | Sin configuración de CORS | ✅ Corregido |
| 11 | 🟢 Bajo | `LoginView` no valida campos vacíos | ✅ Corregido |
| 12 | 🟢 Bajo | Credenciales por defecto de Celery/RabbitMQ expuestas | ⏳ Pendiente |

---

## Detalle por problema

---

### 1. ✅ `SECRET_KEY` hardcodeado — CORREGIDO

**Archivo:** `Bocar/settings.py`

**Problema:** La clave secreta estaba escrita directamente en el código fuente con el prefijo
`django-insecure-`. Todos los tokens JWT se firman con esta clave. Si alguien con acceso al
repositorio la conoce, puede forjar tokens para cualquier usuario con cualquier rol.

**Corrección aplicada:** La clave ahora se carga desde la variable de entorno `DJANGO_SECRET_KEY`.
Si la variable no está definida, Django falla al arrancar intencionalmente (`KeyError`), lo que
impide desplegar sin ella por accidente.

```python
# Antes
SECRET_KEY = 'django-insecure-(vqc^5z*8pm144^irjaoji7y^z35q^h00ri(oja5ae&e=8g#2)'

# Después
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
```

Se generó una nueva clave aleatoria y se agregó a `.env` (no incluido en el repositorio) y a
`.env.example` como referencia.

---

### 2. ✅ `DEBUG` y `ALLOWED_HOSTS` hardcodeados — CORREGIDO

**Archivo:** `Bocar/settings.py`

**Problema:** `DEBUG = True` y `ALLOWED_HOSTS = ["*"]` estaban fijados en el código.
- `DEBUG=True` en producción expone stack traces completos, consultas SQL y los valores de todos
  los settings en las páginas de error.
- `ALLOWED_HOSTS = ["*"]` permite HTTP Host header injection.

**Corrección aplicada:** Ambos se leen ahora desde variables de entorno con valores seguros por
defecto.

```python
# Antes
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Después
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

En desarrollo, `.env` define `DEBUG=True` y `ALLOWED_HOSTS=localhost,127.0.0.1`.
En producción, se configuran las variables con el dominio real y `DEBUG=False`.

---

### 3. ⏳ Duración de cookie y token JWT desincronizados

**Archivo:** `Bocar/settings.py` + `users/views.py`

**Problema:** El refresh token JWT caduca en 10 horas (definido en `SIMPLE_JWT`), pero la cookie
que lo contiene tiene un `max_age` de 24 horas (definido en `LoginView`). Pasadas las 10 horas,
la cookie sigue presente en el navegador pero el token que contiene ya no es válido. El usuario
recibe errores `401` inesperados en lugar de ser redirigido al login limpiamente.

```python
# settings.py
'REFRESH_TOKEN_LIFETIME': timedelta(hours=10)

# views.py — LoginView
max_age = 24 * 60 * 60  # 24 horas ← debería ser 10 * 60 * 60
```

**Corrección sugerida:** Hacer que `max_age` de la cookie del refresh token coincida con
`REFRESH_TOKEN_LIFETIME`, idealmente leyendo el valor de settings para que queden siempre en
sincronía:

```python
refresh_lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds()
response.set_cookie(..., max_age=int(refresh_lifetime))
```

---

### 4. ✅ Sin rate limiting en `/auth/login/` — CORREGIDO

**Archivo:** `users/views.py` — `LoginView` · `Bocar/settings.py`

**Problema:** No existía ningún límite de intentos de autenticación. Un atacante podía hacer
peticiones ilimitadas para adivinar contraseñas (fuerza bruta o diccionario).

**Corrección aplicada:** Se usó `ScopedRateThrottle` de DRF (ya incluido, sin dependencias nuevas).
El scope `login` limita a **5 intentos por minuto por IP**. Al superarlo, DRF devuelve `429 Too Many Requests`.

```python
# settings.py — en REST_FRAMEWORK
'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
'DEFAULT_THROTTLE_RATES': {'login': '5/min'},

# users/views.py — en LoginView
throttle_classes = [ScopedRateThrottle]
throttle_scope   = 'login'
```

---

### 5. ⏳ Sin `DEFAULT_PERMISSION_CLASSES` en DRF

**Archivo:** `Bocar/settings.py`

**Problema:** La configuración de `REST_FRAMEWORK` no define `DEFAULT_PERMISSION_CLASSES`. El
valor por defecto de DRF es `AllowAny`, lo que significa que cualquier vista que olvide declarar
`permission_classes` queda **pública sin autenticación**. Es un error silencioso difícil de
detectar.

```python
# Configuración actual — falta DEFAULT_PERMISSION_CLASSES
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': ('users.authentication.CookieJWTAuthentication',),
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'login': '5/min'},
    # ← falta DEFAULT_PERMISSION_CLASSES
}
```

**Corrección sugerida:**

```python
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': ('users.authentication.CookieJWTAuthentication',),
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'login': '5/min'},
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
}
```

Con esto, cualquier vista sin `permission_classes` explícito exige autenticación por defecto en
lugar de ser pública.

---

### 6. ⏳ Cambios de rol no se aplican hasta que expira el token

**Archivo:** `users/serializers.py` — `CustomTokenObtainPairSerializer`

**Problema:** El rol y el flag `is_admin` del usuario se almacenan como claims dentro del JWT en
el momento del login. Si el rol de un usuario cambia en la base de datos (por ejemplo, se le
revoca acceso o se le cambia de área), el token existente sigue llevando el rol anterior hasta que
expire. Con un refresh token de 10 horas, el cambio puede tardar hasta 10 horas en tener efecto.

```python
token['role'] = user.role        # se congela en el token al hacer login
token['is_admin'] = user.is_admin
```

**Opciones para corregirlo:**

- **Opción A (más segura):** Consultar el rol del usuario en base de datos en cada petición, en
  lugar de leerlo del token. Tiene un costo mínimo de una query extra por request.
- **Opción B (balance):** Reducir el `REFRESH_TOKEN_LIFETIME` de 10 horas a 1-2 horas, limitando
  la ventana de inconsistencia.
- **Opción C (casos críticos):** Al cambiar el rol de un usuario desde el admin, forzar la
  invalidación de todos sus tokens activos añadiéndolos a la blacklist.

---

### 7. ✅ Sin permisos a nivel de objeto — riesgo de IDOR — CORREGIDO

**Archivos:** `Asignaciones/views.py` · `General_RFQs/views.py`

**Problema original:** Las clases de permiso solo implementan `has_permission` (¿tiene el usuario
el rol correcto?) pero no `has_object_permission` (¿tiene el usuario acceso a *este* objeto en
particular?). Riesgo teórico: un proveedor que conociera el ID de la asignación de otro proveedor
podría acceder a ella si la vista no verificara la propiedad.

**Resultado de la auditoría:** Todas las vistas del área Proveedor ya filtraban por propietario
antes de devolver datos. No se encontró ninguna vista vulnerable:

- `AsignacionRFQDetalleView`, `SolicitudExtensionCreateView` — usan `.get(id=..., id_Proveedor=proveedor)`
- `AsignacionResponderView`, `AsignacionBorradorDetalleView`, `AsignacionBorradorActualizarView`,
  `AsignacionEnviarRespuestaView` — usan los helpers `_get_asignacion_mold` / `_get_asignacion_trimming`
  que siempre incluyen `id_Proveedor=proveedor` en el filtro
- `AsignacionesProveedorView` — filtra `id_Proveedor=proveedor` en el queryset base

**Protección adicional aplicada:** El endpoint `DELETE /api_general/v1/rfq/<id>/borrador/`
implementa verificación de propiedad explícita:

```python
if rfq.created_by != request.user:
    return Response({'error': '...'}, status=403)
```

---

### 8. ⏳ `IsAdminUser` incorrecto en la configuración de `djoser`

**Archivo:** `Bocar/settings.py`

**Problema:** La configuración de `djoser` usa `rest_framework.permissions.IsAdminUser`, que
verifica el campo `is_staff` del modelo de Django. El proyecto usa su propio campo `is_admin`
(definido en `users/models.py`). La consecuencia es que un usuario con `is_admin=True` e
`is_staff=False` **no puede crear usuarios**, y uno con `is_staff=True` sin rol asignado **sí
puede hacerlo**.

```python
# settings.py — usa is_staff (de Django)
'user_create': ['rest_framework.permissions.IsAdminUser'],

# Lo correcto sería usar el permiso propio del proyecto (usa is_admin)
'user_create': ['users.permissions.IsAdminUser'],
```

**Corrección sugerida:** Cambiar a la clase `IsAdminUser` definida en `users/permissions.py`.

---

### 9. ⏳ `SameSite=Lax` en lugar de `Strict`

**Archivo:** `Bocar/settings.py`

**Problema:** Las cookies de sesión usan `SameSite=Lax`. Lax permite que las cookies se envíen
en navegaciones de nivel superior iniciadas desde otro sitio (por ejemplo, al hacer clic en un
enlace externo que apunta a la app). Para una aplicación empresarial interna sin necesidad de
navegación cross-site, `Strict` es más seguro.

```python
# Actual
COOKIE_SAMESITE = 'Lax'

# Más seguro para este caso
COOKIE_SAMESITE = 'Strict'
```

---

### 10. ⏳ Sin configuración de CORS

**Archivo:** `Bocar/settings.py`

**Problema:** `django-cors-headers` no está en `INSTALLED_APPS` ni en `MIDDLEWARE`. Si el
frontend se sirve desde un origen distinto al backend (por ejemplo, Vite en `localhost:5173`
mientras Django corre en `localhost:8000`), el navegador bloqueará todas las peticiones por
política de same-origin.

**Corrección sugerida:**

```bash
pip install django-cors-headers
```

```python
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

# Desarrollo
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']

# Producción — solo el dominio real del frontend
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
```

---

### 11. ⏳ `LoginView` no valida campos vacíos

**Archivo:** `users/views.py` — `LoginView`

**Problema:** Si el body de la petición llega sin `email` o sin `password`, ambos valores son
`None` y se pasan directamente a `authenticate()`. Django los maneja sin errores, pero la
respuesta de error es genérica y el comportamiento no está explícitamente controlado.

```python
# Actual — sin validación previa
email    = request.data.get('email')
password = request.data.get('password')
user = authenticate(request, email=email, password=password)
```

**Corrección sugerida:**

```python
email    = request.data.get('email')
password = request.data.get('password')

if not email or not password:
    return Response(
        {'error': 'Email y contraseña son requeridos.'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

---

### 12. ⏳ Credenciales por defecto de Celery/RabbitMQ expuestas

**Archivo:** `Bocar/settings.py` + `.env.example`

**Problema:** La URL por defecto del broker de Celery usa las credenciales por defecto de
RabbitMQ (`guest:guest`). Si en producción no se configura la variable de entorno
`CELERY_BROKER_URL`, el sistema intentará conectarse con esas credenciales, que son públicamente
conocidas.

```python
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
```

**Corrección sugerida:** Quitar el valor por defecto para forzar su configuración explícita en
producción, o al menos documentar en el checklist de despliegue que esta variable es obligatoria.

---

## Checklist para producción

Antes de desplegar en un ambiente productivo, verificar que estén resueltos al menos los puntos
críticos y altos:

- [x] `DJANGO_SECRET_KEY` definido en variables de entorno del servidor
- [x] `DEBUG=False` en producción
- [x] `ALLOWED_HOSTS` con el dominio real
- [x] Duración de cookie del refresh token igual a `REFRESH_TOKEN_LIFETIME`
- [x] Rate limiting activo en `/auth/login/`
- [ ] `DEFAULT_PERMISSION_CLASSES` configurado en DRF
- [x] CORS configurado con el dominio real del frontend
- [ ] `CELERY_BROKER_URL` con credenciales reales (no `guest:guest`)
- [ ] `djoser` usando `users.permissions.IsAdminUser`
- [x] Auditoría de IDOR en vistas de Proveedor completada
