# Seguridad — problemas pendientes

> Última actualización: 2026-06-10. Solo se listan issues sin resolver.

---

## Resumen

| ID | Severidad | Problema |
|----|-----------|---------|
| A | 🟡 Medio | Race condition: asignaciones duplicadas sin constraint de DB |
| B | 🟡 Medio | Sin lock de dependencias Python (builds no reproducibles) |
| C | 🟡 Medio | Falta CSRF explícito en endpoints mutantes con cookies |
| D | 🟢 Bajo | Swagger, ReDoc y `/admin/` expuestos en producción sin restricción |
| E | 🟢 Bajo | Historial y notificaciones se registran dos veces por acción |
| F | 🟢 Bajo | `request.user.proveedor` lanza 500 si el perfil no existe |
| G | 🟢 Bajo | `SameSite=Lax` en lugar de `Strict` en cookies |
| H | 🟢 Bajo | Celery usa `guest:guest` si no se configura `CELERY_BROKER_URL` |

---

## Detalle

---

### A — Race condition: asignaciones duplicadas sin constraint de base de datos

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

### B — Sin lock de dependencias Python

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

### C — Falta CSRF explícito en endpoints mutantes con cookies

**OWASP:** A01 Broken Access Control, A07 Authentication Failures

El sistema usa JWT en cookies HttpOnly con `SameSite=Lax`. Esta configuración reduce
el riesgo de CSRF, pero no lo elimina: `SameSite=Lax` permite el envío de cookies en
navegaciones de nivel superior (ej. clic en enlace externo que genera un POST). No
hay token CSRF explícito para las mutaciones de la API. Además, `CORS_ALLOW_CREDENTIALS=True`
está activo, lo que amplía la superficie si algún origen permitido quedara mal configurado.

**Para resolverlo:** implementar token CSRF para todas las mutaciones basadas en
cookies. Considerar cambiar a `SameSite=Strict` (ver punto G).

**Archivos a revisar:**
- `users/views.py` (líneas ~101, ~111, ~221, ~232)
- `Bocar/settings.py` — `COOKIE_SAMESITE`, `CORS_ALLOW_CREDENTIALS`

---

### D — Swagger, ReDoc y `/admin/` expuestos en producción

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

### E — Historial y notificaciones se registran dos veces por acción

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

### F — `request.user.proveedor` lanza 500 si el perfil no existe

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

### G — `SameSite=Lax` en lugar de `Strict`

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

### H — Celery usa `guest:guest` si no se configura `CELERY_BROKER_URL`

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

**Prioridad alta — integridad de datos**

Agregar el `UniqueConstraint` de asignaciones (A) para eliminar el riesgo de
duplicados bajo carga concurrente.

**Prioridad media — endurecimiento**

Crear el lock de dependencias Python (B), implementar CSRF explícito (C) y
ajustar `SameSite` a `Strict` (G), considerando que C y G están relacionados.

**Prioridad baja — operaciones y robustez**

Gatear Swagger y el admin por ambiente (D), corregir los registros duplicados (E),
proteger el perfil proveedor faltante (F) y configurar las credenciales de Celery (H).
