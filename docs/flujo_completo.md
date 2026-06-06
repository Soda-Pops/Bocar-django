# Flujo completo del sistema — Bocar

> **Nota general:** Todos los endpoints (excepto `POST /auth/login/`) requieren autenticación.
> El sistema usa JWT almacenado en **cookies HttpOnly**. El frontend nunca accede al token
> directamente — lo envía automáticamente en cada petición.

---

## Índice

1. [Autenticación](#1-autenticación)
2. [Ciclo de vida de un RFQ](#2-ciclo-de-vida-de-un-rfq)
3. [Área — Industrialización](#3-área--industrialización)
4. [Área — Comercialización](#4-área--comercialización)
5. [Área — Proveedor](#5-área--proveedor)
6. [Endpoints de apoyo](#6-endpoints-de-apoyo)
7. [Notificaciones por correo](#7-notificaciones-por-correo)
8. [Roles y permisos](#8-roles-y-permisos)

---

## 1. Autenticación

El sistema usa **JWT en cookies HttpOnly**. El access token dura 15 minutos y el refresh token 10 horas. Al expirar el access token, el frontend llama a `/auth/refresh/` de forma transparente para obtener uno nuevo sin que el usuario tenga que volver a iniciar sesión.

### Endpoints

---

#### `POST /auth/login/`

Inicia sesión. Recibe email y contraseña, devuelve los datos del usuario en el body y los tokens **únicamente en cookies** (nunca en el body).

**Body:**
```json
{
  "email": "usuario@empresa.com",
  "password": "contraseña"
}
```

**Respuesta exitosa `200`:**
```json
{
  "message": "Login exitoso.",
  "user": {
    "id": 1,
    "email": "usuario@empresa.com",
    "username": "juan.perez",
    "role": "Ind",
    "is_admin": false
  }
}
```

**Cookies que se establecen:**
| Cookie | Duración | Descripción |
|---|---|---|
| `access_token` | 15 min | Token de acceso para cada petición |
| `refresh_token` | 10 horas | Token para renovar el access token |

**Errores:**
| Código | Motivo |
|---|---|
| `401` | Email o contraseña incorrectos |

---

#### `POST /auth/logout/`

Cierra sesión. Invalida el refresh token en la base de datos (blacklist) y elimina ambas cookies del navegador. Requiere estar autenticado.

**Respuesta exitosa `200`:**
```json
{ "message": "Logout exitoso." }
```

**Errores:**
| Código | Motivo |
|---|---|
| `400` | No hay sesión activa o el token ya estaba expirado |
| `401` | No autenticado |

---

#### `POST /auth/refresh/`

Renueva el access token usando el refresh token de la cookie. Si `ROTATE_REFRESH_TOKENS=True` (activado), también emite un nuevo refresh token y el anterior queda invalidado.

**Respuesta exitosa `200`:**
```json
{ "message": "Token renovado." }
```

**Errores:**
| Código | Motivo |
|---|---|
| `401` | No hay refresh token en cookie, o ya expiró |

---

#### `GET /auth/me/`

Valida que la sesión siga activa y devuelve los datos del usuario autenticado. El frontend debe llamar este endpoint al cargar la aplicación para reconstruir el estado de sesión — **nunca decodificar el token en el cliente**.

**Respuesta exitosa `200`:**
```json
{
  "id": 1,
  "email": "usuario@empresa.com",
  "username": "juan.perez",
  "role": "Ind",
  "is_admin": false
}
```

**Errores:**
| Código | Motivo |
|---|---|
| `401` | Sesión expirada o cookie inválida → redirigir al login |

---

## 2. Ciclo de vida de un RFQ

Un RFQ (Request for Quotation) pasa por tres estados y dos tipos: **Mold** y **Trimming**. Ambos tipos siguen el mismo flujo de estados.

```
[En_Ind] ──enviar──► [En_Com] ──asignar proveedor──► [En_Pro] ──respuestas completas──► [Completado]
            ▲               │
            └──aprobación───┘
           (solicitud de edición)
```

| Status | Significado | Quién puede actuar |
|---|---|---|
| `En_Ind` | Borrador en Industrialización | Ind / Ind Admin |
| `En_Com` | Enviado a Comercialización | Com / Com Admin |
| `En_Pro` | Asignado a proveedores | Pro (responder) + Com (extensiones) |
| `Completado` | Todos los proveedores respondieron | Solo lectura |

> **Borrado lógico:** Un RFQ nunca se elimina físicamente. Se marca con `logical_delete = True`.
> Solo `Ind Admin` y `Com Admin` pueden realizar esta operación.

---

## 3. Área — Industrialización

**Roles:** `Ind` · `Ind Admin`
**Prefijo base:** `/api_industrializacion/v1/`
**Prefijo de detalle:** `/api_mold/v1/` y `/api_trimming/v1/`

Esta área es donde nace un RFQ. Los usuarios de Industrialización crean los RFQs, los editan, adjuntan archivos y los envían a Comercialización cuando están listos.

---

#### `GET /api_industrializacion/v1/rfqs/`

Lista todos los RFQs (mold y trimming) combinados, con deadline dinámico.

**Visibilidad:**
- RFQs en `En_Ind` → solo los propios (borradores del usuario autenticado)
- RFQs en `En_Com`, `En_Pro`, `Completado` → todos los del sistema

**Respuesta `200`:** Lista de RFQs con `id`, `nombre`, `tipo`, `status`, `deadline`, `created_by`, `created_at`.

---

#### `GET /api_general/v1/rfq-count/?user_id=<id>`

Devuelve conteo de RFQs por status e histograma mensual del año en curso. Útil para el dashboard.

**Query params:**
| Param | Requerido | Descripción |
|---|---|---|
| `user_id` | No | ID del usuario para filtrar los `En_Ind`. Si se omite, usa el usuario autenticado |

**Respuesta `200`:**
```json
{
  "total": 24,
  "por_status": {
    "En_Ind": 3,
    "En_Com": 5,
    "En_Pro": 12,
    "Completado": 4
  },
  "histograma_mensual": [2, 0, 4, 3, 6, 5, 1, 0, 0, 0, 0, 0]
}
```

---

#### `POST /api_industrializacion/v1/rfq/?tipo=mold|trimming`

Crea un nuevo RFQ en estado `En_Ind` (borrador). Acepta archivos opcionales como parte del `multipart/form-data`.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** `multipart/form-data` con los campos del RFQ y archivos opcionales.

**Respuesta `201`:** Datos del RFQ creado.

**Errores:**
| Código | Motivo |
|---|---|
| `400` | Datos inválidos o faltantes |

---

#### `GET /api_mold/v1/rfq-molds/<id>/`
#### `GET /api_trimming/v1/rfq-trimmings/<id>/`

Devuelve todos los datos de un RFQ específico, incluyendo archivos adjuntos. Sirve tanto para ver un borrador existente como para ver el detalle completo antes de editar o enviar.

**Respuesta `200`:** Objeto completo del RFQ con archivos adjuntos.

**Errores:**
| Código | Motivo |
|---|---|
| `404` | El RFQ no existe |

---

#### `PATCH /api_industrializacion/v1/rfq/<id>/?tipo=mold|trimming`

Edita los campos de un RFQ existente. **Solo funciona si el RFQ está en `En_Ind`.**

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** Solo los campos a modificar (patch parcial).

**Errores:**
| Código | Motivo |
|---|---|
| `403` | El RFQ ya fue enviado (`En_Com` o `En_Pro`) — no se puede editar directamente |
| `404` | El RFQ no existe |

> Para editar un RFQ que ya está en `En_Com`, es necesario que Industrialización haga una
> **solicitud de edición** y Comercialización la apruebe.

---

#### `POST /api_industrializacion/v1/rfq/<id>/enviar/?tipo=mold|trimming`

Cambia el status del RFQ de `En_Ind` a `En_Com`, enviándolo a Comercialización.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** vacío

**Regla obligatoria:** El RFQ debe tener **al menos un archivo adjunto** antes de poder enviarse. Si no tiene archivos, se retorna `400`.

**Respuesta `200`:** RFQ actualizado con `status: "En_Com"`.

**Errores:**
| Código | Motivo |
|---|---|
| `400` | El RFQ no tiene archivos adjuntos |
| `400` | El RFQ no está en `En_Ind` |

---

#### `POST /api_industrializacion/v1/edit-requests/?tipo=mold|trimming`

Crea una solicitud para que Comercialización regrese el RFQ a `En_Ind` y permitir correcciones. Solo válido si el RFQ está actualmente en `En_Com`.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:**
```json
{
  "rfq_mold": 12,
  "reason": "Error en las dimensiones de la pieza."
}
```
*(usar `rfq_trimming` si el tipo es trimming)*

**Respuesta `201`:** Solicitud de edición creada con status `Pendiente`.

**Errores:**
| Código | Motivo |
|---|---|
| `400` | El RFQ está en `En_Pro` — ya no se puede solicitar edición |
| `400` | El RFQ no está en `En_Com` |

---

#### `PATCH /api_general/v1/rfq/<id>/delete/?tipo=mold|trimming`

Borrado lógico del RFQ. El registro permanece en base de datos con `logical_delete = True`. **Requiere `is_admin = True` (cualquier rol).**

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** vacío

**Respuesta `200`:**
```json
{ "message": "Registro eliminado correctamente." }
```

**Errores:**
| Código | Motivo |
|---|---|
| `400` | Falta `?tipo` o valor inválido |
| `400` | El RFQ ya estaba marcado como eliminado |
| `403` | El usuario no tiene `is_admin = True` |

---

## 4. Área — Comercialización

**Roles:** `Com` · `Com Admin`
**Prefijo base:** `/api_comercializacion/v1/`

Esta área recibe los RFQs enviados por Industrialización, asigna proveedores, gestiona solicitudes de edición y aprueba o rechaza extensiones de tiempo solicitadas por proveedores.

---

#### `GET /api_comercializacion/v1/rfqs/`

Lista todos los RFQs activos (mold y trimming combinados) que están en `En_Com`, `En_Pro` o `Completado`. Incluye deadline dinámico y progreso de proveedores (cuántos han respondido del total asignado).

**Respuesta `200`:**
```json
[
  {
    "id": 12,
    "nombre": "Pieza A",
    "tipo": "mold",
    "status": "En_Pro",
    "deadline": "12 días",
    "progreso": "2/3 proveedores respondieron"
  }
]
```

---

#### `GET /api_comercializacion/v1/solicitudes/`

Devuelve en un solo objeto todas las solicitudes pendientes de atención:
- **Solicitudes de edición** de Industrialización (quieren recuperar el RFQ para corregirlo)
- **Solicitudes de extensión de tiempo** de Proveedores (piden más plazo)

Ambas separadas por tipo `mold` / `trimming`.

**Respuesta `200`:**
```json
{
  "solicitudes_edicion": {
    "mold": [
      {
        "id": 3,
        "rfq_mold": 12,
        "rfq_mold_status": "En_Com",
        "requested_by": 2,
        "requested_by_name": "juan.perez",
        "requested_at": "2026-06-01T10:00:00Z",
        "status": "Pendiente",
        "reason": "Error en las dimensiones de la pieza."
      }
    ],
    "trimming": []
  },
  "solicitudes_extension": {
    "mold": [
      {
        "id": 2,
        "rfq_nombre": "Pieza A",
        "proveedor_nombre": "Proveedor X S.A.",
        "due_date_actual": "2026-06-15",
        "nueva_fecha": "2026-06-30",
        "motivo": "Retraso en importación de materiales.",
        "status": "Pendiente",
        "solicitada_at": "2026-06-01T14:30:00Z"
      }
    ],
    "trimming": []
  }
}
```

---

#### `GET /api_proveedores/v1/proveedores/`

Lista todos los proveedores disponibles en el sistema. Usado por Comercialización para seleccionar a quién asignar un RFQ.

**Respuesta `200`:** Lista de proveedores con `id`, `nombre`, `pais`, y campos relevantes.

---

#### `POST /api_comercializacion/v1/asignaciones/crear/?tipo=mold|trimming`

Asigna uno o varios proveedores a un RFQ. Si un proveedor ya tiene asignación activa para ese RFQ, se omite silenciosamente sin error. Puede llamarse múltiples veces para agregar más proveedores.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:**
```json
{
  "id_rfq": 12,
  "due_date": "2026-07-15",
  "proveedores": [1, 2, 3]
}
```

**Comportamiento automático:** Al asignar el **primer** proveedor, el RFQ cambia de `En_Com` a `En_Pro` automáticamente.

**Respuesta `201`:** Lista de asignaciones creadas.

**Errores:**
| Código | Motivo |
|---|---|
| `400` | Datos inválidos o RFQ no está en `En_Com` |

---

#### `PATCH /api_comercializacion/v1/edit-requests/<id>/aprobar/?tipo=mold|trimming`

Aprueba una solicitud de edición de Industrialización. El RFQ regresa a `En_Ind` para que pueda ser corregido.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** vacío

**Regla:** Si el RFQ ya está en `En_Pro` (ya fue asignado a proveedores), la aprobación es **bloqueada con `400`**. No es posible revertirlo en ese punto.

**Respuesta `200`:** Solicitud con `status: "Aprobada"`, RFQ con `status: "En_Ind"`.

**Errores:**
| Código | Motivo |
|---|---|
| `400` | El RFQ ya está en `En_Pro` — no se puede revertir |
| `404` | La solicitud no existe |

---

#### `PATCH /api_comercializacion/v1/edit-requests/<id>/rechazar/?tipo=mold|trimming`

Rechaza una solicitud de edición. El RFQ permanece en `En_Com` sin cambios.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** vacío

**Respuesta `200`:** Solicitud con `status: "Rechazada"`.

---

#### `PATCH /api_comercializacion/v1/extension/<id>/resolver/?tipo=mold|trimming`

Aprueba o rechaza una solicitud de extensión de plazo enviada por un proveedor.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:**
```json
{ "status": "Aprobada" }
```
o
```json
{ "status": "Rechazada" }
```

**Comportamiento al aprobar:** Se actualiza **solo el `due_date` de la asignación del proveedor** que solicitó la extensión. El `due_date` general del RFQ no se modifica.

**Respuesta `200`:** Solicitud resuelta.

---

## 5. Área — Proveedor

**Rol:** `Pro` (sin distinción de admin dentro del área)
**Prefijo base:** `/api_proveedores/v1/asginaciones/`

> **Nota:** El prefijo contiene un error tipográfico en la URL (`asginaciones` en lugar de
> `asignaciones`). El código funciona correctamente — es solo la URL la que está mal escrita.

Los proveedores ven únicamente sus propias asignaciones. Nunca tienen acceso a las asignaciones de otros proveedores ni a los datos de contacto de la competencia.

---

#### `GET /api_proveedores/v1/asginaciones/mis-asignaciones/`

Devuelve las asignaciones del proveedor autenticado, separadas en **pendientes** y **contestadas**, cada grupo dividido en `mold` y `trimming`.

El campo `deadline` se calcula dinámicamente en cada petición:
- `"19 días"` — si queda más de 24 horas
- `"5h 30m"` — si queda menos de 24 horas
- `"Vencido"` — si ya pasó el `due_date`

**Respuesta `200`:**
```json
{
  "pendientes": {
    "mold": [
      {
        "id": 41,
        "rfq_nombre": "Pieza A",
        "fecha_de_asignacion": "2026-05-15",
        "due_date": "2026-06-20",
        "deadline": "16 días",
        "en_tiempo": true,
        "tiene_borrador": false,
        "is_answered": false,
        "is_closed": false
      }
    ],
    "trimming": []
  },
  "contestadas": {
    "mold": [...],
    "trimming": []
  }
}
```

---

#### `GET /api_proveedores/v1/asginaciones/detalle/<id>/?tipo=mold|trimming`

Devuelve la información técnica completa del RFQ asignado: dimensiones, archivos, especificaciones. No expone datos de otros proveedores asignados al mismo RFQ.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Errores:**
| Código | Motivo |
|---|---|
| `403` | La asignación no pertenece al proveedor autenticado |
| `404` | La asignación no existe |

---

#### `POST /api_proveedores/v1/asginaciones/responder/<id>/?tipo=mold|trimming`

Guarda el cost breakdown como **borrador** (`status=draft`). No marca la asignación como respondida. Permite al proveedor guardar su avance y continuar después.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** Campos del cost breakdown (precios, tiempos, condiciones, etc.)

**Reglas:**
- Solo puede existir **un borrador por asignación**. Si ya existe, retorna `409`.
- Bloqueado si la asignación está vencida (`due_date < hoy`).

**Respuesta `201`:** Borrador creado.

**Errores:**
| Código | Motivo |
|---|---|
| `409` | Ya existe un borrador para esta asignación |
| `400` | La asignación está vencida |

---

#### `GET /api_proveedores/v1/asginaciones/responder/<id>/detalle/?tipo=mold|trimming`

Recupera el borrador guardado para continuar editándolo, o la respuesta ya enviada para consultarla.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Respuesta `200`:** Datos del cost breakdown con su `status` (`draft` o `submitted`).

---

#### `PATCH /api_proveedores/v1/asginaciones/responder/<id>/actualizar/?tipo=mold|trimming`

Modifica campos del borrador. **Solo permitido mientras `status=draft`.**

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** Solo los campos a actualizar.

**Errores:**
| Código | Motivo |
|---|---|
| `403` | El borrador ya fue enviado (`submitted`) — no se puede modificar |

---

#### `POST /api_proveedores/v1/asginaciones/responder/<id>/enviar/?tipo=mold|trimming`

Envía la respuesta definitiva. Cambia el borrador de `draft` a `submitted` y marca la asignación como `is_answered = True`. **Esta acción es irreversible.**

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:** vacío

**Reglas:**
- Bloqueado si la respuesta ya fue enviada anteriormente.
- Bloqueado si la asignación está vencida (`due_date < hoy`).

**Respuesta `200`:** Asignación con `is_answered: true`.

**Errores:**
| Código | Motivo |
|---|---|
| `400` | La respuesta ya fue enviada |
| `400` | La asignación está vencida |

---

#### `POST /api_proveedores/v1/asginaciones/extension/solicitar/<id>/?tipo=mold|trimming`

Solicita una ampliación del plazo cuando la asignación está vencida. No requiere tener un borrador guardado. Solo puede haber **una solicitud pendiente** por asignación al mismo tiempo.

**Query param requerido:** `?tipo=mold` o `?tipo=trimming`

**Body:**
```json
{
  "motivo": "Retraso en importación de materiales.",
  "nueva_fecha": "2026-07-01"
}
```

**Regla:** La `nueva_fecha` debe ser posterior al `due_date` actual.

**Respuesta `201`:** Solicitud creada con `status: "Pendiente"`.

**Errores:**
| Código | Motivo |
|---|---|
| `400` | Ya existe una solicitud pendiente para esta asignación |
| `400` | La `nueva_fecha` no es posterior al `due_date` actual |

---

## 6. Endpoints de apoyo

### Historial de auditoría

#### `GET /api_historial/v1/<tipo>/<rfq_id>/`

Devuelve el historial completo de eventos de un RFQ: cambios de status, ediciones, asignaciones, etc. Cada evento registra qué cambió, quién lo hizo y cuándo.

**Path params:**
| Param | Valores | Descripción |
|---|---|---|
| `tipo` | `mold` · `trimming` | Tipo del RFQ |
| `rfq_id` | entero | ID del RFQ |

**Respuesta `200`:**
```json
[
  {
    "id": 1,
    "rfq_id": 12,
    "tipo": "mold",
    "evento": "status_change",
    "detalle": { "antes": "En_Ind", "despues": "En_Com" },
    "usuario": "juan.perez",
    "timestamp": "2026-06-01T10:00:00Z"
  }
]
```

### Documentación interactiva

| URL | Descripción |
|---|---|
| `GET /schema/swagger/` | Interfaz Swagger UI — probar endpoints en el navegador |
| `GET /schema/redoc/` | Documentación ReDoc |
| `GET /api/schema/` | Esquema OpenAPI en formato JSON |

---

## 7. Notificaciones por correo

El sistema envía correos automáticamente en los siguientes eventos. Los correos se procesan de forma asíncrona mediante **Celery + RabbitMQ** para no bloquear las respuestas de la API.

| Evento | Plantilla | Destinatarios |
|---|---|---|
| RFQ enviado a Comercialización | `rfq_a_compras.html` | Área de Compras / Comercialización |
| RFQ asignado a proveedor | `rfq_a_proveedores.html` | Proveedor asignado |
| Proveedor envía cotización | `cotizacion_recibida.html` | Comercialización |
| RFQ modificado | `modificacion_rfq.html` | Afectados por el cambio |
| Cancelación solicitada | `solicitud_cancelacion.html` | Comercialización |
| Cancelación confirmada | `cancelacion_confirmada.html` | Industrialización + Proveedor |

> Las notificaciones se pueden activar o desactivar mediante la variable de entorno
> `NOTIFICATIONS_ENABLED=True/False` sin tocar código.

---

## 8. Roles y permisos

| Rol | `role` en BD | `is_admin` | Acceso |
|---|---|---|---|
| Industrialización | `Ind` | `False` | Crear, editar, enviar RFQs, solicitar edición |
| Industrialización Admin | `Ind` | `True` | Todo lo anterior + borrado lógico |
| Comercialización | `Com` | `False` | Ver RFQs, asignar proveedores, gestionar solicitudes y extensiones |
| Comercialización Admin | `Com` | `True` | Todo lo anterior + borrado lógico |
| Proveedor | `Pro` | `False` | Ver asignaciones propias, responder, solicitar extensiones |
| Sin rol | `SinRol` | `False` | Solo puede autenticarse — ningún endpoint es accesible |

> Los roles se verifican en cada endpoint mediante clases de permiso como `IsComercializacionAdmin`,
> `IsComercializacionUser` e `IsProveedor` definidas en `users/permissions.py`.
