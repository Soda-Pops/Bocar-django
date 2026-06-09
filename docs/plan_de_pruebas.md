# Plan de Pruebas — Sistema Bocar

> **Propósito:** Verificar el ciclo de vida completo de RFQs (Mold y Trimming), el control de
> acceso por rol y la integridad del historial de auditoría.
>
> **Ejecutar contra:** `http://localhost:8000`
>
> **Convenciones:**
> - `{TOKEN_X}` — valor real del `access_token` obtenido en el login del usuario X.
> - `{ID_X}` — ID real del recurso X creado durante la ejecución.
> - Los casos están ordenados secuencialmente; los módulos posteriores reusan IDs de anteriores.
> - Cada caso indica **PASS** si el HTTP status y el body coinciden con lo esperado.

---

## Preparación — Datos de prueba

Crear los siguientes usuarios en `/admin/` (o vía `createsuperuser`) antes de ejecutar.
**Contraseña uniforme:** `Test1234!`

| Variable | Email | Role | is_admin |
|---|---|---|---|
| `USER_IND_A` | ind_a@test.com | Ind | False |
| `USER_IND_B` | ind_b@test.com | Ind | False |
| `USER_IND_ADMIN` | ind_admin@test.com | Ind | True |
| `USER_COM` | com@test.com | Com | False |
| `USER_COM_ADMIN` | com_admin@test.com | Com | True |
| `USER_PRO` | pro@test.com | Pro | False |
| `USER_SIN_ROL` | sinrol@test.com | SinRol | False |

Adicionalmente, desde `/admin/`:
- Crear un registro `Proveedor` vinculando `id_account = USER_PRO`. Anotar el `{ID_PROVEEDOR}`.

---

## Módulo 0 — Autenticación

### AUTH-01 — Login exitoso

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/auth/login/`
**Headers:** `Content-Type: application/json`
**Body:**
```json
{
  "email": "ind_a@test.com",
  "password": "Test1234!"
}
```
**Resultado esperado:**
- Status: `200 OK`
- Body contiene `{ "detail": "..." }` (o mensaje de login exitoso)
- Cabecera `Set-Cookie` contiene `access_token` y `refresh_token`

**Acción:** Anotar el token de cada usuario. Repetir este caso para los 7 usuarios y guardar:
`{TOKEN_IND_A}`, `{TOKEN_IND_B}`, `{TOKEN_IND_ADMIN}`, `{TOKEN_COM}`, `{TOKEN_COM_ADMIN}`, `{TOKEN_PRO}`, `{TOKEN_SIN_ROL}`

---

### AUTH-02 — Login con campos vacíos

**Actor:** (anónimo)
**Método:** `POST`
**Endpoint:** `/auth/login/`
**Body:**
```json
{
  "email": "",
  "password": ""
}
```
**Resultado esperado:**
- Status: `400 Bad Request`
- Body: `{ "error": "Email y contraseña son requeridos." }`

---

### AUTH-03 — Login con credenciales incorrectas

**Actor:** (anónimo)
**Método:** `POST`
**Endpoint:** `/auth/login/`
**Body:**
```json
{
  "email": "ind_a@test.com",
  "password": "ContraseñaIncorrecta"
}
```
**Resultado esperado:**
- Status: `401 Unauthorized`

---

### AUTH-04 — Refresh de token

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/auth/refresh/`
**Headers:** `Cookie: refresh_token={REFRESH_TOKEN_IND_A}`
**Body:** (vacío)
**Resultado esperado:**
- Status: `200 OK`
- Nueva cookie `access_token` presente en `Set-Cookie`

---

### AUTH-05 — Logout

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/auth/logout/`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Body:** (vacío)
**Resultado esperado:**
- Status: `200 OK`
- Las cookies `access_token` y `refresh_token` se eliminan (Set-Cookie con `Max-Age=0` o `expires` en el pasado)

**Nota:** Volver a hacer login para restaurar `{TOKEN_IND_A}` antes del siguiente módulo.

---

## Módulo 1 — Ciclo completo RFQ Mold

### MOLD-01 — Crear RFQ Mold

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Body:** `multipart/form-data`

| Campo | Valor |
|---|---|
| `due_date` | `2026-12-31` |
| `DESC` | `Prueba molde A` |
| `PT` | `Pieza-Test-001` |
| `archivos` | (adjuntar cualquier archivo .pdf o .txt de prueba) |

**Resultado esperado:**
- Status: `201 Created`
- Body: `{ "detail": "RFQ Mold creado correctamente." }`

**Efecto secundario:**
- RFQ creado con `status = En_Ind`, `created_by = USER_IND_A`
- Historial: evento `CREACION` registrado

**Acción:** Consultar el ID del RFQ recién creado via `GET /api_mold/v1/rfq-molds/` y anotar `{ID_RFQ_MOLD}`.

---

### MOLD-02 — USER_IND_A lista sus RFQs y ve su borrador

**Actor:** `USER_IND_A`
**Método:** `GET`
**Endpoint:** `/api_industrializacion/v1/rfqs/`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `200 OK`
- El campo `mold` contiene una entrada con `id = {ID_RFQ_MOLD}` y `status = "En_Ind"`

---

### MOLD-03 — USER_IND_B NO ve el borrador de A

**Actor:** `USER_IND_B`
**Método:** `GET`
**Endpoint:** `/api_industrializacion/v1/rfqs/`
**Headers:** `Cookie: access_token={TOKEN_IND_B}`
**Resultado esperado:**
- Status: `200 OK`
- El RFQ `{ID_RFQ_MOLD}` **no aparece** en la lista `mold` (los borradores En_Ind son solo visibles para su creador)

---

### MOLD-04 — Editar RFQ

**Actor:** `USER_IND_A`
**Método:** `PATCH`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_MOLD}/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{
  "DESC": "Descripcion actualizada",
  "PPY": 5000.0
}
```
**Resultado esperado:**
- Status: `200 OK`
- Body: `{ "detail": "RFQ Mold actualizado correctamente." }`

**Efecto secundario:**
- Historial: evento `EDICION` con diff de campos `DESC` y `PPY`

---

### MOLD-05 — Detalle via endpoint deprecado (solo Ind)

**Actor:** `USER_IND_A`
**Método:** `GET`
**Endpoint:** `/api_mold/v1/rfq-molds/{ID_RFQ_MOLD}/`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `200 OK`
- Body contiene todos los campos del RFQ, incluyendo `archivos` (lista de adjuntos)
- Campo `logical_delete = false` (el endpoint ya no devuelve registros borrados)

---

### MOLD-06 — Intentar enviar sin archivo adjunto

> Este caso aplica si se crea un RFQ nuevo sin archivo. Para el RFQ `{ID_RFQ_MOLD}` ya tiene
> archivos (MOLD-01), por lo que este caso requiere un RFQ limpio.

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/?tipo=mold`
**Body:** `multipart/form-data` — solo `due_date=2026-12-31`, sin campo `archivos`
Anotar el ID como `{ID_RFQ_MOLD_SIN_ARCHIVO}`.

Luego intentar enviarlo:

**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_MOLD_SIN_ARCHIVO}/enviar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `400 Bad Request`
- Body: `{ "detail": "El RFQ debe tener al menos un archivo adjunto antes de enviarse." }`

---

### MOLD-07 — Enviar RFQ a Comercialización

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_MOLD}/enviar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Body:** (vacío)
**Resultado esperado:**
- Status: `200 OK`
- Body: `{ "detail": "RFQ Mold enviado a Comercialización correctamente." }`

**Efecto secundario:**
- `status` del RFQ cambia a `En_Com`
- Historial: evento `ENVIO_COMERCIALIZACION` con `status_anterior=En_Ind`, `status_nuevo=En_Com`

---

### MOLD-08 — Intentar editar RFQ en estado En_Com

**Actor:** `USER_IND_A`
**Método:** `PATCH`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_MOLD}/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{ "DESC": "Intento de edicion en Com" }
```
**Resultado esperado:**
- Status: `403 Forbidden`
- Body contiene mensaje sobre estado incorrecto

---

### MOLD-09 — Com lista RFQs y ve el RFQ en En_Com

**Actor:** `USER_COM`
**Método:** `GET`
**Endpoint:** `/api_comercializacion/v1/rfqs/`
**Headers:** `Cookie: access_token={TOKEN_COM}`
**Resultado esperado:**
- Status: `200 OK`
- El campo `mold` contiene entrada con `id = {ID_RFQ_MOLD}` y `status = "En_Com"`
- Campos `progreso_proveedores = "Sin proveedores asignados"` y `deadline` con días restantes

---

### MOLD-10 — Com asigna proveedor al RFQ

**Actor:** `USER_COM_ADMIN`
**Método:** `POST`
**Endpoint:** `/api_comercializacion/v1/asignaciones/crear/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`, `Content-Type: application/json`
**Body:**
```json
{
  "id_rfq": {ID_RFQ_MOLD},
  "due_date": "2026-11-30",
  "proveedores": [{ID_PROVEEDOR}]
}
```
**Resultado esperado:**
- Status: `200 OK`
- Body indica asignaciones creadas

**Efecto secundario:**
- `status` del RFQ cambia a `En_Pro`
- Se crea registro `Asignacion_Proveedor_Mold` con `is_answered=False`, `is_closed=False`
- Historial: evento `ASIGNACION_PROVEEDORES` y `ENVIO_PROVEEDORES`

**Acción:** Consultar `GET /api_proveedores/v1/asginaciones/mis-asignaciones/` con `{TOKEN_PRO}` para obtener `{ID_ASIGNACION_MOLD}`.

---

### MOLD-11 — Proveedor lista sus asignaciones

**Actor:** `USER_PRO`
**Método:** `GET`
**Endpoint:** `/api_proveedores/v1/asginaciones/mis-asignaciones/`
**Headers:** `Cookie: access_token={TOKEN_PRO}`
**Resultado esperado:**
- Status: `200 OK`
- La asignación `{ID_ASIGNACION_MOLD}` aparece en `pendientes` con `is_answered=false`
- Campos `rfq_nombre`, `deadline`, `en_tiempo=true`

---

### MOLD-12 — Proveedor envía cotización definitiva

**Actor:** `USER_PRO`
**Paso 1** — Guardar borrador:
**Método:** `POST`
**Endpoint:** `/api_proveedores/v1/asginaciones/responder/{ID_ASIGNACION_MOLD}/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_PRO}`, `Content-Type: application/json`
**Body:**
```json
{
  "base_currency_exchange_rate": "USD"
}
```
(Todos los campos de costos son opcionales con default 0.0)
**Resultado esperado:** Status: `200 OK`

**Paso 2** — Enviar cotización definitiva:
**Método:** `POST`
**Endpoint:** `/api_proveedores/v1/asginaciones/responder/{ID_ASIGNACION_MOLD}/enviar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_PRO}`
**Body:** (vacío)
**Resultado esperado:**
- Status: `200 OK`
- Body indica cotización enviada

**Efecto secundario:**
- `is_answered=True` en la asignación
- Historial: evento `COTIZACION_RECIBIDA`
- La asignación aparece en `contestadas` (no en `pendientes`)

---

## Módulo 2 — Ciclo completo RFQ Trimming

### TRIM-01 — Crear RFQ Trimming

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/?tipo=trimming`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Body:** `multipart/form-data`

| Campo | Valor |
|---|---|
| `due_date` | `2026-12-31` |
| `archivos` | (adjuntar archivo de prueba) |

**Resultado esperado:** Status: `201 Created`

**Acción:** Anotar `{ID_RFQ_TRIMMING}`.

---

### TRIM-02 — Editar RFQ Trimming

**Actor:** `USER_IND_A`
**Método:** `PATCH`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_TRIMMING}/?tipo=trimming`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{ "due_date": "2027-01-15" }
```
**Resultado esperado:** Status: `200 OK`

---

### TRIM-03 — Enviar Trimming a Comercialización

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_TRIMMING}/enviar/?tipo=trimming`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `200 OK`
- `status` cambia a `En_Com`

---

### TRIM-04 — Com asigna proveedor al Trimming

**Actor:** `USER_COM_ADMIN`
**Método:** `POST`
**Endpoint:** `/api_comercializacion/v1/asignaciones/crear/?tipo=trimming`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`, `Content-Type: application/json`
**Body:**
```json
{
  "id_rfq": {ID_RFQ_TRIMMING},
  "due_date": "2026-11-30",
  "proveedores": [{ID_PROVEEDOR}]
}
```
**Resultado esperado:** Status: `200 OK`, `status` del RFQ cambia a `En_Pro`

**Acción:** Anotar `{ID_ASIGNACION_TRIMMING}`.

---

### TRIM-05 — Proveedor guarda borrador de cotización Trimming

**Actor:** `USER_PRO`
**Método:** `POST`
**Endpoint:** `/api_proveedores/v1/asginaciones/responder/{ID_ASIGNACION_TRIMMING}/?tipo=trimming`
**Headers:** `Cookie: access_token={TOKEN_PRO}`, `Content-Type: application/json`
**Body:**
```json
{ "base_currency_exchange_rate": "USD" }
```
**Resultado esperado:** Status: `200 OK`, `is_answered=False` (borrador guardado)

---

### TRIM-06 — Proveedor envía cotización Trimming

**Actor:** `USER_PRO`
**Método:** `POST`
**Endpoint:** `/api_proveedores/v1/asginaciones/responder/{ID_ASIGNACION_TRIMMING}/enviar/?tipo=trimming`
**Headers:** `Cookie: access_token={TOKEN_PRO}`
**Resultado esperado:**
- Status: `200 OK`
- `is_answered=True`
- Historial: evento `COTIZACION_RECIBIDA`

---

## Módulo 3 — Solicitud de edición

> Este módulo usa un nuevo RFQ Mold. Crear uno y enviarlo a Com siguiendo MOLD-01 y MOLD-07.
> Anotar `{ID_RFQ_EDIT}`.

### EDIT-01 — Ind solicita edición de RFQ en En_Com

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/edit-requests/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{
  "rfq_mold": {ID_RFQ_EDIT},
  "reason": "Se encontró un error en las especificaciones DCM"
}
```
**Resultado esperado:**
- Status: `201 Created`
- Body: `{ "detail": "Solicitud de edición enviada correctamente." }`

**Efecto secundario:**
- Registro `RFQ_Mold_EditRequest` creado con `status=Pendiente`
- Historial: evento `SOLICITUD_EDICION`

**Acción:** Anotar `{ID_EDIT_REQUEST}` desde la respuesta o via `/api_comercializacion/v1/solicitudes/`.

---

### EDIT-02 — Com lista solicitudes pendientes

**Actor:** `USER_COM_ADMIN`
**Método:** `GET`
**Endpoint:** `/api_comercializacion/v1/solicitudes/`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`
**Resultado esperado:**
- Status: `200 OK`
- La solicitud `{ID_EDIT_REQUEST}` aparece con `status=Pendiente` en la sección de solicitudes de edición

---

### EDIT-03 — Com rechaza la solicitud

**Actor:** `USER_COM_ADMIN`
**Método:** `PATCH`
**Endpoint:** `/api_comercializacion/v1/edit-requests/{ID_EDIT_REQUEST}/rechazar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`, `Content-Type: application/json`
**Body:**
```json
{ "status": "Rechazada" }
```
**Resultado esperado:**
- Status: `200 OK`
- `status` de la solicitud cambia a `Rechazada`
- RFQ `{ID_RFQ_EDIT}` sigue en `En_Com`

**Efecto secundario:**
- Historial: evento `EDICION_RECHAZADA`

---

### EDIT-04 — Ind crea segunda solicitud (la rechazada no bloquea)

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/edit-requests/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{
  "rfq_mold": {ID_RFQ_EDIT},
  "reason": "Segunda solicitud de edición"
}
```
**Resultado esperado:**
- Status: `201 Created` (la solicitud rechazada no bloquea una nueva)

**Acción:** Anotar `{ID_EDIT_REQUEST_2}`.

---

### EDIT-05 — Com aprueba la segunda solicitud

**Actor:** `USER_COM_ADMIN`
**Método:** `PATCH`
**Endpoint:** `/api_comercializacion/v1/edit-requests/{ID_EDIT_REQUEST_2}/aprobar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`, `Content-Type: application/json`
**Body:**
```json
{ "status": "Aprobada" }
```
**Resultado esperado:**
- Status: `200 OK`
- RFQ `{ID_RFQ_EDIT}` regresa a `status=En_Ind`

**Efecto secundario:**
- Historial: evento `EDICION_APROBADA` con `status_anterior=En_Com`, `status_nuevo=En_Ind`

---

### EDIT-06 — Ind edita y reenvía el RFQ a Com

**Actor:** `USER_IND_A`

**Paso 1** — Editar:
**Método:** `PATCH`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_EDIT}/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{ "DESC": "Descripcion corregida tras aprobacion de edicion" }
```
**Resultado esperado:** Status: `200 OK`

**Paso 2** — Reenviar a Com:
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_EDIT}/enviar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `200 OK`
- `status` del RFQ regresa a `En_Com`

---

## Módulo 4 — Extensión de tiempo

> Este módulo usa `{ID_ASIGNACION_MOLD}` del ciclo principal. Si ya fue enviada la cotización,
> crear una nueva asignación (nueva vuelta de MOLD-01 a MOLD-10) y anotar `{ID_ASIGNACION_EXT}`.

### EXT-01 — Proveedor solicita extensión de tiempo

**Actor:** `USER_PRO`
**Método:** `POST`
**Endpoint:** `/api_proveedores/v1/asginaciones/extension/solicitar/{ID_ASIGNACION_EXT}/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_PRO}`, `Content-Type: application/json`
**Body:**
```json
{
  "motivo": "Se requiere tiempo adicional para calcular costos de materiales importados",
  "nueva_fecha": "2027-01-31"
}
```
**Resultado esperado:**
- Status: `201 Created`
- Body contiene `id` de la solicitud y `status=Pendiente`

**Efecto secundario:**
- Historial: evento `EXTENSION_SOLICITADA`

**Acción:** Anotar `{ID_EXTENSION}`.

---

### EXT-02 — Com lista solicitudes pendientes (incluye extensión)

**Actor:** `USER_COM_ADMIN`
**Método:** `GET`
**Endpoint:** `/api_comercializacion/v1/solicitudes/`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`
**Resultado esperado:**
- Status: `200 OK`
- La solicitud de extensión `{ID_EXTENSION}` aparece con `status=Pendiente`

---

### EXT-03 — Com rechaza la extensión

**Actor:** `USER_COM_ADMIN`
**Método:** `PATCH`
**Endpoint:** `/api_comercializacion/v1/extension/{ID_EXTENSION}/resolver/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`, `Content-Type: application/json`
**Body:**
```json
{ "status": "Rechazada" }
```
**Resultado esperado:**
- Status: `200 OK`
- `status` de la solicitud: `Rechazada`
- `due_date` de la asignación NO cambia

**Efecto secundario:**
- Historial: evento `EXTENSION_RECHAZADA`

---

### EXT-04 — Proveedor solicita nueva extensión y Com la aprueba

**Actor:** `USER_PRO`

**Paso 1** — Nueva solicitud:
**Método:** `POST`
**Endpoint:** `/api_proveedores/v1/asginaciones/extension/solicitar/{ID_ASIGNACION_EXT}/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_PRO}`, `Content-Type: application/json`
**Body:**
```json
{
  "motivo": "Segunda solicitud con justificación adicional",
  "nueva_fecha": "2027-02-28"
}
```
**Resultado esperado:** Status: `201 Created`

**Acción:** Anotar `{ID_EXTENSION_2}`.

**Paso 2** — Com aprueba:
**Método:** `PATCH`
**Endpoint:** `/api_comercializacion/v1/extension/{ID_EXTENSION_2}/resolver/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM_ADMIN}`, `Content-Type: application/json`
**Body:**
```json
{ "status": "Aprobada" }
```
**Resultado esperado:**
- Status: `200 OK`
- `status` de la solicitud: `Aprobada`
- `due_date` de la asignación actualizado a `2027-02-28`

**Efecto secundario:**
- Historial: evento `EXTENSION_APROBADA` con `detalle.nueva_fecha = "2027-02-28"`

---

## Módulo 5 — Control de acceso (pruebas negativas)

### SEC-01 — Com no puede crear RFQ en Industrialización

**Actor:** `USER_COM`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM}`
**Body:** `multipart/form-data` — `due_date=2026-12-31`
**Resultado esperado:** Status: `403 Forbidden`

---

### SEC-02 — Pro no puede crear RFQ en Industrialización

**Actor:** `USER_PRO`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_PRO}`
**Body:** `multipart/form-data` — `due_date=2026-12-31`
**Resultado esperado:** Status: `403 Forbidden`

---

### SEC-03 — SinRol no puede crear RFQ en Industrialización

**Actor:** `USER_SIN_ROL`
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_SIN_ROL}`
**Body:** `multipart/form-data` — `due_date=2026-12-31`
**Resultado esperado:** Status: `403 Forbidden`

---

### SEC-04 — Sin autenticación no puede crear RFQ

**Actor:** (anónimo, sin cookie)
**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/?tipo=mold`
**Headers:** (ninguno)
**Body:** `multipart/form-data` — `due_date=2026-12-31`
**Resultado esperado:** Status: `401 Unauthorized`

---

### SEC-05 — USER_IND_B no puede editar RFQ de USER_IND_A

**Actor:** `USER_IND_B`
**Método:** `PATCH`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_MOLD_SIN_ARCHIVO}/?tipo=mold`

> Usar el RFQ creado en MOLD-06 que sigue en En_Ind y pertenece a USER_IND_A.

**Headers:** `Cookie: access_token={TOKEN_IND_B}`, `Content-Type: application/json`
**Body:**
```json
{ "DESC": "Intento de edicion por otro usuario" }
```
**Resultado esperado:**
- Status: `403 Forbidden`
- Body: `{ "detail": "No tienes permiso para editar este RFQ." }`

---

### SEC-06 — USER_IND_B no puede enviar RFQ de USER_IND_A

**Actor:** `USER_IND_B`

Primero adjuntar archivo al RFQ `{ID_RFQ_MOLD_SIN_ARCHIVO}` como USER_IND_B (fallará también por propiedad):

**Método:** `POST`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_MOLD_SIN_ARCHIVO}/enviar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_B}`
**Resultado esperado:**
- Status: `403 Forbidden`
- Body: `{ "detail": "No tienes permiso para enviar este RFQ." }`

---

### SEC-07 — USER_COM (sin is_admin) no puede aprobar solicitudes de edición

**Actor:** `USER_COM`

> Usar `{ID_EDIT_REQUEST}` del módulo 3 (ya resuelta). Si todas están resueltas, tomar cualquier
> ID de EditRequest existente.

**Método:** `PATCH`
**Endpoint:** `/api_comercializacion/v1/edit-requests/{ID_EDIT_REQUEST}/aprobar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM}`, `Content-Type: application/json`
**Body:**
```json
{ "status": "Aprobada" }
```
**Resultado esperado:** Status: `403 Forbidden`

---

### SEC-08 — USER_COM (sin is_admin) no puede rechazar solicitudes

**Actor:** `USER_COM`
**Método:** `PATCH`
**Endpoint:** `/api_comercializacion/v1/edit-requests/{ID_EDIT_REQUEST}/rechazar/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM}`, `Content-Type: application/json`
**Body:**
```json
{ "status": "Rechazada" }
```
**Resultado esperado:** Status: `403 Forbidden`

---

### SEC-09 — USER_PRO no puede listar RFQs via endpoint deprecado

**Actor:** `USER_PRO`
**Método:** `GET`
**Endpoint:** `/api_mold/v1/rfq-molds/`
**Headers:** `Cookie: access_token={TOKEN_PRO}`
**Resultado esperado:** Status: `403 Forbidden`

---

### SEC-10 — USER_COM no puede listar RFQs via endpoint deprecado

**Actor:** `USER_COM`
**Método:** `GET`
**Endpoint:** `/api_mold/v1/rfq-molds/`
**Headers:** `Cookie: access_token={TOKEN_COM}`
**Resultado esperado:** Status: `403 Forbidden`

---

### SEC-11 — POST en endpoint deprecado devuelve 405

**Actor:** `USER_IND_A`
**Método:** `POST`
**Endpoint:** `/api_mold/v1/rfq-molds/`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{ "due_date": "2026-12-31" }
```
**Resultado esperado:** Status: `405 Method Not Allowed`

---

### SEC-12 — Proveedor no puede ver asignación de otro proveedor

**Actor:** `USER_PRO`

> Intentar acceder a una asignación con un ID que no corresponde al proveedor autenticado.
> Usar cualquier ID numérico que no sea `{ID_ASIGNACION_MOLD}` ni `{ID_ASIGNACION_TRIMMING}`.

**Método:** `GET`
**Endpoint:** `/api_proveedores/v1/asginaciones/detalle/9999/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_PRO}`
**Resultado esperado:** Status: `404 Not Found`

---

### SEC-13 — USER_IND_A no puede editar RFQ en En_Com (estado incorrecto)

**Actor:** `USER_IND_A`
**Método:** `PATCH`
**Endpoint:** `/api_industrializacion/v1/rfq/{ID_RFQ_MOLD}/?tipo=mold`

> `{ID_RFQ_MOLD}` está en `En_Pro` (fue enviado a Com y asignado en Módulo 1).

**Headers:** `Cookie: access_token={TOKEN_IND_A}`, `Content-Type: application/json`
**Body:**
```json
{ "DESC": "Edicion en estado incorrecto" }
```
**Resultado esperado:** Status: `403 Forbidden` (estado no es En_Ind)

---

### SEC-14 — USER_SIN_ROL no puede usar el chatbot

**Actor:** `USER_SIN_ROL`
**Método:** `POST`
**Endpoint:** `/api_chatbot/v1/query/`
**Headers:** `Cookie: access_token={TOKEN_SIN_ROL}`, `Content-Type: application/json`
**Body:**
```json
{ "pregunta": "¿Cuántos RFQs hay en el sistema?" }
```
**Resultado esperado:** Status: `403 Forbidden`

---

## Módulo 6 — Historial de auditoría

### HIST-01 — Historial completo del RFQ Mold principal

**Actor:** `USER_IND_A`
**Método:** `GET`
**Endpoint:** `/api_historial/v1/mold/{ID_RFQ_MOLD}/`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `200 OK`
- Lista de eventos que incluye **al menos** los siguientes, en este orden cronológico:

| # | Evento esperado |
|---|---|
| 1 | `CREACION` |
| 2 | `EDICION` |
| 3 | `ENVIO_COMERCIALIZACION` |
| 4 | `ASIGNACION_PROVEEDORES` |
| 5 | `ENVIO_PROVEEDORES` |
| 6 | `COTIZACION_RECIBIDA` |

---

### HIST-02 — Filtrar historial por evento

**Actor:** `USER_IND_A`
**Método:** `GET`
**Endpoint:** `/api_historial/v1/mold/{ID_RFQ_MOLD}/?evento=EDICION`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `200 OK`
- Todos los resultados tienen `evento = "EDICION"`
- No aparecen otros tipos de eventos

---

### HIST-03 — Historial del RFQ Trimming

**Actor:** `USER_IND_A`
**Método:** `GET`
**Endpoint:** `/api_historial/v1/trimming/{ID_RFQ_TRIMMING}/`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `200 OK`
- Eventos mínimos: `CREACION`, `EDICION`, `ENVIO_COMERCIALIZACION`, `ASIGNACION_PROVEEDORES`, `ENVIO_PROVEEDORES`, `COTIZACION_RECIBIDA`

---

## Módulo 7 — Borrado

### DEL-01 — Creador borra su propio borrador (borrado físico)

> Usar el RFQ `{ID_RFQ_MOLD_SIN_ARCHIVO}` que está en `En_Ind` y fue creado por `USER_IND_A`.

**Actor:** `USER_IND_A`
**Método:** `DELETE`
**Endpoint:** `/api_general/v1/rfq/{ID_RFQ_MOLD_SIN_ARCHIVO}/borrador/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_A}`
**Resultado esperado:**
- Status: `204 No Content`
- El RFQ ya no aparece en ningún listado

---

### DEL-02 — USER_IND_B no puede borrar borrador de otro usuario

> Crear un nuevo RFQ como `USER_IND_A` en `En_Ind`, anotar `{ID_RFQ_BORRADOR_A}`.

**Actor:** `USER_IND_B`
**Método:** `DELETE`
**Endpoint:** `/api_general/v1/rfq/{ID_RFQ_BORRADOR_A}/borrador/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_B}`
**Resultado esperado:** Status: `403 Forbidden`

---

### DEL-03 — Admin aplica borrado lógico a un RFQ activo

> Usar `{ID_RFQ_EDIT}` que está en `En_Com` o `En_Pro`.

**Actor:** `USER_IND_ADMIN`
**Método:** `PATCH`
**Endpoint:** `/api_general/v1/rfq/{ID_RFQ_EDIT}/delete/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_IND_ADMIN}`
**Resultado esperado:**
- Status: `200 OK`
- Body: `{ "message": "Registro eliminado correctamente." }`

**Efecto secundario:**
- `logical_delete=True` en el RFQ
- RFQ ya no aparece en listados normales
- Historial: evento `CANCELACION`

---

### DEL-04 — USER_COM (sin is_admin) no puede aplicar borrado lógico

**Actor:** `USER_COM`
**Método:** `PATCH`
**Endpoint:** `/api_general/v1/rfq/{ID_RFQ_MOLD}/delete/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM}`
**Resultado esperado:** Status: `403 Forbidden`

---

## Módulo 8 — Comparativa de precios por proveedor

> Requiere que el Módulo 1 esté completo: `{ID_RFQ_MOLD}` debe existir y
> `USER_PRO` debe haber enviado su cotización (MOLD-12 completado, `is_answered=True`).

### COMP-01 — Com obtiene comparativa con proveedor que ya respondió

**Actor:** `USER_COM`
**Método:** `GET`
**Endpoint:** `/api_comercializacion/v1/rfq/{ID_RFQ_MOLD}/comparativa/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM}`
**Resultado esperado:**
- Status: `200 OK`
- Body: lista con **exactamente un elemento** correspondiente a `USER_PRO`
```json
[
  {
    "usuario_id":            {ID_USER_PRO},
    "nombre_empresa":        "...",
    "accs_grand_total_sum":  0.0,
    "mat_grand_total_sum":   0.0,
    "grand_total_sum":       0.0,
    "corr_grand_total_sum":  0.0,
    "log_grand_total_sum":   0.0,
    "precio_total":          0.0
  }
]
```
- `precio_total` == suma de los cinco campos `*_grand_total_sum`
- No aparecen proveedores con `is_answered=False`

---

### COMP-02 — Comparativa de RFQ sin cotizaciones recibidas devuelve lista vacía

> Usar `{ID_RFQ_TRIMMING}` del Módulo 2 **antes** de que el proveedor envíe
> su cotización, o bien un RFQ recién enviado a `En_Pro`.

**Actor:** `USER_COM`
**Método:** `GET`
**Endpoint:** `/api_comercializacion/v1/rfq/{ID_RFQ_TRIMMING}/comparativa/?tipo=trimming`
**Headers:** `Cookie: access_token={TOKEN_COM}`
**Resultado esperado:**
- Status: `200 OK`
- Body: `[]`

---

### COMP-03 — Pro no puede acceder a la comparativa

**Actor:** `USER_PRO`
**Método:** `GET`
**Endpoint:** `/api_comercializacion/v1/rfq/{ID_RFQ_MOLD}/comparativa/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_PRO}`
**Resultado esperado:** Status: `403 Forbidden`

---

### COMP-04 — RFQ inexistente devuelve 404

**Actor:** `USER_COM`
**Método:** `GET`
**Endpoint:** `/api_comercializacion/v1/rfq/99999/comparativa/?tipo=mold`
**Headers:** `Cookie: access_token={TOKEN_COM}`
**Resultado esperado:**
- Status: `404 Not Found`
- Body: `{ "detail": "RFQ no encontrado." }`

---

## Tabla de cobertura de eventos del historial

| Evento | Caso que lo verifica |
|---|---|
| `CREACION` | MOLD-01, TRIM-01 |
| `EDICION` | MOLD-04, TRIM-02, EDIT-06 |
| `ENVIO_COMERCIALIZACION` | MOLD-07, TRIM-03 |
| `ENVIO_PROVEEDORES` | MOLD-10, TRIM-04 |
| `ASIGNACION_PROVEEDORES` | MOLD-10, TRIM-04 |
| `SOLICITUD_EDICION` | EDIT-01 |
| `EDICION_APROBADA` | EDIT-05 |
| `EDICION_RECHAZADA` | EDIT-03 |
| `COTIZACION_RECIBIDA` | MOLD-12, TRIM-06 |
| `CANCELACION` | DEL-03 |
| `EXTENSION_SOLICITADA` | EXT-01 |
| `EXTENSION_APROBADA` | EXT-04 |
| `EXTENSION_RECHAZADA` | EXT-03 |

**Total de casos:** 54
**Total de módulos:** 9 (0–8)
**Eventos del historial cubiertos:** 13/13
