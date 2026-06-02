# Flujo de usuario — Proveedor

> **Nota:** Todos los flujos asumen que el usuario ya realizó login y cuenta con un token de sesión válido en cookie. No existe distinción de roles dentro del área de Proveedor; todos los usuarios tienen el mismo acceso.

---

## Rol

| Rol | Descripción |
|---|---|
| `Pro` | Ver sus asignaciones, contestar RFQs y solicitar extensiones de tiempo. |

---

## Endpoints por área y paso del flujo

| Área de usuario | Área funcional | Método | Endpoint | Para qué parte del flujo | Acceso |
|---|---|---|---|---|---|
| **Proveedor** | **Dashboard** | GET | `/api_proveedores/v1/asginaciones/mis-asignaciones/` | Ver asignaciones separadas en **pendientes** (con deadline dinámico e indicador de borrador) y **contestadas**. Cada grupo dividido en mold y trimming. | Pro |
| | **Ver RFQ** | GET | `/api_proveedores/v1/asginaciones/detalle/<id>/?tipo=mold\|trimming` | Ver la información completa del RFQ asignado (archivos, datos técnicos). No incluye asignaciones de otros proveedores. | Pro |
| | **Guardar borrador** | POST | `/api_proveedores/v1/asginaciones/responder/<id>/?tipo=mold\|trimming` | Crear el cost breakdown como borrador (`status=draft`). No marca la asignación como respondida. Bloqueado si ya existe un borrador o si está vencida. | Pro |
| | **Ver borrador** | GET | `/api_proveedores/v1/asginaciones/responder/<id>/detalle/?tipo=mold\|trimming` | Recuperar el borrador guardado para continuar llenándolo. | Pro |
| | **Actualizar borrador** | PATCH | `/api_proveedores/v1/asginaciones/responder/<id>/actualizar/?tipo=mold\|trimming` | Modificar campos del borrador. Solo permitido mientras `status=draft`. Rechazado con `403` si ya fue enviado. | Pro |
| | **Enviar respuesta** | POST | `/api_proveedores/v1/asginaciones/responder/<id>/enviar/?tipo=mold\|trimming` | Enviar la respuesta definitiva (`draft` → `submitted`). Marca la asignación como `is_answered=True`. Bloqueado si ya fue enviada o si la asignación está vencida. | Pro |
| | **Solicitar extensión** | POST | `/api_proveedores/v1/asginaciones/extension/solicitar/<id>/?tipo=mold\|trimming` | Solicitar ampliación del plazo cuando la asignación está vencida. Solo puede haber una solicitud pendiente por asignación a la vez. | Pro |

---

## Ejemplo de llamada por paso

| Paso | Ejemplo |
|---|---|
| Ver asignaciones | `GET /api_proveedores/v1/asginaciones/mis-asignaciones/` |
| Ver detalle del RFQ Mold | `GET /api_proveedores/v1/asginaciones/detalle/41/?tipo=mold` |
| Ver detalle del RFQ Trimming | `GET /api_proveedores/v1/asginaciones/detalle/42/?tipo=trimming` |
| Guardar borrador Mold | `POST /api_proveedores/v1/asginaciones/responder/41/?tipo=mold` · body: campos del cost breakdown |
| Ver borrador guardado | `GET /api_proveedores/v1/asginaciones/responder/41/detalle/?tipo=mold` |
| Actualizar borrador | `PATCH /api_proveedores/v1/asginaciones/responder/41/actualizar/?tipo=mold` · body: solo los campos a modificar |
| Enviar respuesta definitiva | `POST /api_proveedores/v1/asginaciones/responder/41/enviar/?tipo=mold` · sin body |
| Solicitar extensión de tiempo | `POST /api_proveedores/v1/asginaciones/extension/solicitar/41/?tipo=mold` · body: `{ "motivo": "Retraso en importación.", "nueva_fecha": "2026-07-01" }` |

---

## Estructura de respuesta — Listado de asignaciones

```json
GET /api_proveedores/v1/asginaciones/mis-asignaciones/

{
  "pendientes": {
    "mold": [
      {
        "id": 41,
        "rfq_nombre": "Pieza A",
        "fecha_de_asignacion": "2026-05-15",
        "due_date": "2026-06-20",
        "deadline": "19 días",
        "en_tiempo": true,
        "tiene_borrador": false,
        "is_answered": false,
        "is_closed": false
      }
    ],
    "trimming": []
  },
  "contestadas": {
    "mold": [
      {
        "id": 38,
        "rfq_nombre": "Pieza B",
        "fecha_de_asignacion": "2026-04-10",
        "due_date": "2026-05-01",
        "deadline": "Vencido",
        "en_tiempo": false,
        "tiene_borrador": false,
        "is_answered": true,
        "is_closed": false
      }
    ],
    "trimming": []
  }
}
```

---

## Reglas de negocio clave

| Regla | Detalle |
|---|---|
| Visibilidad | El proveedor solo ve sus propias asignaciones. El detalle del RFQ no expone asignaciones de otros proveedores. |
| Borrador único | Solo puede existir un borrador por asignación. Si ya existe, el `POST` de crear retorna `409`. |
| Actualización bloqueada | Si el borrador ya fue enviado (`submitted`), el `PATCH` retorna `403`. |
| Envío bloqueado por vencimiento | Si la asignación está vencida (`due_date < hoy`), ni el `POST` de borrador ni el `POST` de enviar son permitidos. |
| Extensión de tiempo | Se puede solicitar aunque no haya borrador. Solo puede haber una solicitud `Pendiente` por asignación. La nueva fecha propuesta debe ser posterior al `due_date` actual. |
| Deadline dinámico | El campo `deadline` se calcula en cada solicitud GET: `"X días"`, `"Xh Ym"` si queda menos de 24 horas, o `"Vencido"`. |
| `tiene_borrador` | Indica si el proveedor ya guardó un borrador pero aún no lo envió. Útil para el frontend para mostrar un indicador visual. |
