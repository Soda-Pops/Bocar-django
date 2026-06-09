# Seguridad — problemas pendientes

> Última actualización: 2026-06-08. Solo se listan issues sin resolver.

---

## Resumen

| ID | Severidad | Problema |
|----|-----------|---------|
| A | ✅ Resuelto | Mass assignment en serializers RFQ |
| B | ✅ Resuelto | Historial de RFQ visible a cualquier usuario autenticado |
| C | 🟠 Alto | Archivos subidos sin validación de tipo, tamaño ni cantidad |
| D | 🟠 Alto | Notificaciones enviadas a todos los proveedores, no solo los asignados |
| E | 🟡 Medio | Cambios de rol no se reflejan hasta que expira el token (hasta 10 h) |
| F | 🟡 Medio | Cookie del refresh token dura 24 h, pero el JWT expira en 10 h |
| G | 🟡 Medio | Operaciones de negocio sin transacción atómica |
| H | 🟡 Medio | Race condition: asignaciones duplicadas sin constraint de DB |
| I | 🟡 Medio | Sin lock de dependencias Python (builds no reproducibles) |
| J | 🟡 Medio | Falta CSRF explícito en endpoints mutantes con cookies |
| K | 🟢 Bajo | Swagger, ReDoc y `/admin/` expuestos en producción sin restricción |
| L | 🟢 Bajo | Historial y notificaciones se registran dos veces por acción |
| M | 🟢 Bajo | `request.user.proveedor` lanza 500 si el perfil no existe |
| N | 🟢 Bajo | `SameSite=Lax` en lugar de `Strict` en cookies |
| O | 🟢 Bajo | Celery usa `guest:guest` si no se configura `CELERY_BROKER_URL` |

---

## Detalle

---

### A — ✅ Mass assignment en serializers RFQ — RESUELTO

**OWASP:** A01 Broken Access Control, A08 Integrity Failures

**Corrección aplicada (2026-06-08):**

`status`, `complete` y `logical_delete` añadidos a `read_only_fields` en
`RFQMoldCreateSerializer` y `RFQTrimmingCreateSerializer`. El método `validate_status`
fue eliminado de ambos (redundante al ser el campo de solo lectura). Las transiciones
de estado siguen ocurriendo únicamente en sus endpoints de acción dedicados.

**Archivos modificados:**
- `RFQ_Mold/serializers.py` — `RFQMoldCreateSerializer.Meta.read_only_fields`
- `RFQ_Trimming/serializers.py` — `RFQTrimmingCreateSerializer.Meta.read_only_fields`

---

### B — ✅ Historial de RFQ visible a cualquier usuario autenticado — RESUELTO

**OWASP:** A01 Broken Access Control, A04 Data Exposure

**Corrección aplicada (2026-06-08):**

Política de visibilidad implementada en `historial/views.py`:

| Rol | Acceso |
|---|---|
| `SinRol` | 403 siempre |
| `Ind` (no admin) | Solo RFQs donde `rfq.created_by == request.user` |
| `Ind` (`is_admin`) | Todos los RFQs |
| `Com` | Todos los RFQs |
| `Pro` | Solo RFQs con asignación activa; eventos internos ocultados; usa `RFQHistorialPublicoSerializer` (sin campo `cambios`) |

Eventos visibles para `Pro`: `ENVIO_PROVEEDORES`, `ASIGNACION_PROVEEDORES`, `COTIZACION_RECIBIDA`, `CANCELACION`, `EXTENSION_SOLICITADA`, `EXTENSION_APROBADA`, `EXTENSION_RECHAZADA`.

**Archivos modificados:**
- `historial/views.py` — control de acceso por rol + filtro de eventos para Pro
- `historial/serializers.py` — nuevo `RFQHistorialPublicoSerializer` sin campo `cambios`
- `historial/services.py` — nuevo helper `get_rfq_object(tipo, rfq_id)`

---

### C — Archivos subidos sin validación de tipo, tamaño ni cantidad

**OWASP:** A02 Security Misconfiguration, A05 Unsafe File Handling

Los RFQs aceptan archivos sin ningún límite de extensión, MIME real, tamaño por
archivo, número de archivos ni escaneo de contenido. Los archivos se almacenan bajo
`media/Files/RFQ_Mold/` y `media/Files/RFQ_Trimming/`, en rutas directamente
accesibles si el servidor web expone `/media/`.

**Para resolverlo:** validar extensión permitida (ej. pdf, xlsx, dwg), tipo MIME
real (leer los primeros bytes, no confiar en la extensión), tamaño máximo por archivo
y por RFQ. Descargar los archivos únicamente a través de un endpoint autenticado y
autorizado, sin exponer la ruta directa. Configurar `DATA_UPLOAD_MAX_MEMORY_SIZE` y
`FILE_UPLOAD_MAX_MEMORY_SIZE` en settings.

**Archivos a revisar:**
- `RFQ_Mold/models.py` (línea 151)
- `RFQ_Trimming/models.py` (línea 117)
- `RFQ_Mold/serializers.py` (línea 27)
- `RFQ_Trimming/serializers.py` (línea 33)
- `Industrializacion/views.py` (líneas 109, 187, 218)
- `Bocar/settings.py` — agregar `DATA_UPLOAD_MAX_MEMORY_SIZE`

---

### D — Notificaciones enviadas a todos los proveedores, no solo los asignados

**OWASP:** A01 Broken Access Control, A04 Data Exposure

Cuando un RFQ avanza al área de Proveedores, `notificar_proveedores` obtiene todos
los usuarios con `role='Pro'` y les envía correo, ignorando la lista de asignaciones
ya creadas para ese RFQ. Proveedores no invitados reciben información o metadata de
RFQs que no les pertenecen.

**Para resolverlo:** construir la lista de destinatarios desde
`rfq.asignaciones.filter(logical_delete=False)` en lugar de consultar por rol global.

**Archivos a revisar:**
- `notificaciones/services.py` (líneas 65, 67)
- `Comercializacion/views.py` (línea 258)

---

### E — Cambios de rol no se reflejan hasta que expira el token

**OWASP:** A07 Authentication Failures

El rol y `is_admin` del usuario quedan almacenados como claims dentro del JWT al
hacer login. Si el rol cambia en la base de datos, el token sigue llevando el rol
anterior durante toda su vida útil (hasta 10 horas). El cambio no tiene efecto hasta
que el usuario vuelve a hacer login.

**Opciones para resolverlo:**
- **Más segura:** leer el rol directamente de la base de datos en cada request en
  lugar de leerlo del token. Costo: una query extra por petición.
- **Balance:** reducir `REFRESH_TOKEN_LIFETIME` de 10 h a 1–2 h para acotar la
  ventana de inconsistencia.
- **Casos críticos:** al cambiar el rol desde el admin, añadir todos los tokens
  activos del usuario a la blacklist.

**Archivos a revisar:**
- `users/serializers.py` — `CustomTokenObtainPairSerializer`
- `users/authentication.py` — donde se lee el rol del token por request

---

### F — Cookie del refresh token dura 24 h, el JWT expira en 10 h

**OWASP:** A07 Authentication Failures

`REFRESH_TOKEN_LIFETIME` es 10 horas en `settings.py`, pero la cookie que contiene
ese token se configura con `max_age = 24 * 60 * 60` (24 horas) en `LoginView`.
Pasadas las 10 horas, la cookie sigue en el navegador pero el token que contiene ya
es inválido, generando errores 401 inesperados sin redirigir al login.

**Para resolverlo:** derivar `max_age` directamente del setting para que siempre
estén sincronizados:

```python
refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
response.set_cookie(..., max_age=int(refresh_lifetime))
```

**Archivos a revisar:**
- `users/views.py` — `LoginView` (líneas ~117, ~238)
- `Bocar/settings.py` — `SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']`

---

### G — Operaciones de negocio sin transacción atómica

**OWASP:** A08 Integrity Failures

Las transiciones de estado de un RFQ implican varios pasos: actualizar el estado del
objeto, crear asignaciones, registrar historial y enviar notificaciones. Estas
operaciones ocurren en pasos separados sin `transaction.atomic`. Si cualquier paso
falla a mitad del proceso, el sistema puede quedar en estado inconsistente: un RFQ
marcado como `En_Pro` sin asignaciones creadas, o asignaciones sin historial.

**Para resolverlo:** envolver cada transición de negocio completa en
`transaction.atomic`. Usar `select_for_update` sobre el RFQ y las asignaciones en
operaciones concurrentes. Mover las notificaciones al callback
`transaction.on_commit` para que solo se envíen si la transacción completa fue exitosa.

**Archivos a revisar:**
- `Comercializacion/views.py` (líneas 164–258)
- `Industrializacion/views.py` (líneas 284–343)
- `historial/services.py` (líneas 8, 32)

---

### H — Race condition: asignaciones duplicadas sin constraint de base de datos

**OWASP:** A08 Integrity Failures

La vista de Comercialización verifica si ya existe una asignación y luego la crea en
dos operaciones separadas (check-then-create). Sin un `UniqueConstraint` en la base
de datos, dos requests que lleguen simultáneamente pueden pasar ambas la verificación
y crear asignaciones duplicadas para el mismo RFQ y proveedor.

**Para resolverlo:** agregar un `UniqueConstraint` condicional en el modelo
`Asignacion` que sea único por RFQ y proveedor cuando `logical_delete=False`.
Reemplazar el check-then-create por `get_or_create` dentro de una transacción.

**Archivos a revisar:**
- `Asignaciones/models.py` — agregar `UniqueConstraint`
- `Comercializacion/views.py` (líneas 181–190, 214–223)

---

### I — Sin lock de dependencias Python

**OWASP:** A03 Software Supply Chain

El backend no tiene `requirements.txt`, `pyproject.toml` ni ningún lock de
dependencias versionado en el repositorio. Esto impide reproducir builds de forma
estable y auditar CVEs. El comentario en `settings.py` menciona Django 6.0.5 pero
`pip freeze` local muestra Django 5.2.13, lo cual indica drift entre entornos.

**Para resolverlo:** crear `requirements.txt` con versiones fijadas y hashes
(`pip-compile` o `pip freeze > requirements.txt`). Añadir `pip-audit` o Safety en
el pipeline de CI para detectar vulnerabilidades automáticamente.

**Archivos a revisar:**
- No existe aún — crear `requirements.txt` en la raíz del proyecto.

---

### J — Falta CSRF explícito en endpoints mutantes con cookies

**OWASP:** A01 Broken Access Control, A07 Authentication Failures

El sistema usa JWT en cookies HttpOnly con `SameSite=Lax`. Esta configuración reduce
el riesgo de CSRF, pero no lo elimina: `SameSite=Lax` permite el envío de cookies en
navegaciones de nivel superior (ej. clic en enlace externo que genera un POST). No
hay token CSRF explícito para las mutaciones de la API. Además, `CORS_ALLOW_CREDENTIALS=True`
está activo, lo que amplía la superficie si algún origen permitido quedara mal configurado.

**Para resolverlo:** implementar token CSRF para todas las mutaciones basadas en
cookies. Considerar cambiar a `SameSite=Strict` (ver punto N).

**Archivos a revisar:**
- `users/views.py` (líneas ~101, ~111, ~221, ~232)
- `Bocar/settings.py` — `COOKIE_SAMESITE`, `CORS_ALLOW_CREDENTIALS`

---

### K — Swagger, ReDoc y `/admin/` expuestos en producción

**OWASP:** A02 Security Misconfiguration

`/admin/`, `/api/schema/`, `/schema/swagger/` y `/schema/redoc/` están registrados
incondicionalmente en las URLs. En producción facilitan el reconocimiento del
atacante: enumeran todos los endpoints, modelos, parámetros y la superficie del admin.

**Para resolverlo:** registrar Swagger y ReDoc solo cuando `DEBUG=True`. Considerar
mover `/admin/` a una ruta no obvia y protegerla con autenticación de doble factor
o allowlist de IPs.

**Archivos a revisar:**
- `Bocar/urls.py` (líneas 8, 36, 39)

---

### L — Historial y notificaciones se registran dos veces por acción

**OWASP:** A09 Logging & Alerting Failures

`AsignacionEnviarRespuestaView` registra el evento `COTIZACION_RECIBIDA` dos veces
y dispara dos notificaciones. `SolicitudExtensionMoldResolverSerializer` registra el
evento de extensión dos veces. El historial queda inflado, las alertas se duplican y
los conteos de métricas son incorrectos.

**Para resolverlo:** identificar y eliminar el bloque duplicado en cada caso.
Agregar una prueba que verifique que una acción produce exactamente un evento de
historial y una notificación.

**Archivos a revisar:**
- `Asignaciones/views.py` (líneas 448, 457, 461, 470)
- `Asignaciones/serializers.py` (líneas 308, 320)

---

### M — `request.user.proveedor` lanza 500 si el perfil no existe

**OWASP:** A10 Exceptional Conditions

Las vistas del área Proveedor asumen que todo usuario con `role='Pro'` tiene una
relación `proveedor` en la base de datos. Si ese perfil no existe (cuenta mal
configurada o creada sin seguir el flujo normal), Django lanza una excepción de
relación inexistente y el servidor devuelve un 500 no controlado.

**Para resolverlo:** agregar una verificación del perfil proveedor dentro del
permiso `IsProveedor` o en un helper centralizado, devolviendo 403 con mensaje
claro si el perfil no existe, en lugar de dejar que el servidor explote.

**Archivos a revisar:**
- `users/permissions.py` — clase `IsProveedor`
- `Asignaciones/views.py` (líneas 91, 151, 247, 295, 343, 408, 528)

---

### N — `SameSite=Lax` en lugar de `Strict`

**OWASP:** A07 Authentication Failures

`COOKIE_SAMESITE = 'Lax'` permite que las cookies se envíen en navegaciones de nivel
superior iniciadas desde otro sitio. Para una aplicación empresarial interna sin
necesidad de navegación cross-site, `Strict` es más seguro y elimina ese vector.

**Para resolverlo:** cambiar a `COOKIE_SAMESITE = 'Strict'` en `Bocar/settings.py`.
Verificar que el flujo de login y refresh no dependa de requests cross-site antes
de aplicarlo.

**Archivos a revisar:**
- `Bocar/settings.py` (línea `COOKIE_SAMESITE`)

---

### O — Celery usa `guest:guest` si no se configura `CELERY_BROKER_URL`

**OWASP:** A02 Security Misconfiguration

Si la variable de entorno `CELERY_BROKER_URL` no está definida en el servidor, el
sistema intenta conectarse a RabbitMQ con las credenciales por defecto `guest:guest`,
que son públicamente conocidas.

**Para resolverlo:** quitar el valor por defecto del setting para que Django falle
al arrancar si la variable no está configurada, en lugar de usar credenciales
inseguras silenciosamente. Agregar `CELERY_BROKER_URL` al checklist de despliegue.

**Archivos a revisar:**
- `Bocar/settings.py` — `CELERY_BROKER_URL`
- `.env.example` — documentar la variable como obligatoria

---

## Plan de remediación

**Semana 1 — lo que bloquea producción**

Empezar por los serializers RFQ (A): mientras no se restrinja `fields='__all__'`,
cualquier usuario con acceso a esos endpoints puede manipular estados de negocio desde
el body. Junto con eso, proteger el historial (B) con la misma lógica de visibilidad
que ya existe en el detalle del RFQ. Antes de terminar la semana, validar los archivos
subidos (C) al menos con extensión y tamaño máximo, y corregir las notificaciones (D)
para que solo lleguen a los proveedores asignados.

**Semana 2 — consistencia e integridad de datos**

Envolver las transiciones de negocio en `transaction.atomic` (G) y agregar el
`UniqueConstraint` de asignaciones (H). Estas dos cosas juntas son las que más daño
silencioso pueden causar ante carga concurrente. Después sincronizar la duración de
la cookie con el token JWT (F) y decidir la estrategia para los cambios de rol (E).

**Semana 3 — endurecimiento y operaciones**

Crear el lock de dependencias Python (I), gatear Swagger y el admin por ambiente (K),
corregir los registros duplicados (L), proteger el perfil proveedor faltante (M) y
ajustar `SameSite` (N) y las credenciales de Celery (O). El CSRF explícito (J)
puede ir aquí o junto a la revisión de cookies de la semana 2 según disponibilidad.
