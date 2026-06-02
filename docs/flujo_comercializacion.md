# Flujo de usuario — Comercialización

> **Nota:** Todos los flujos asumen que el usuario ya realizó login y cuenta con un token de sesión válido en cookie.

---

## Roles

| Rol | Descripción |
|---|---|
| `Com` | Ver RFQs, asignar proveedores, gestionar solicitudes y extensiones. |
| `Com Admin` | Todo lo anterior + borrado lógico de RFQs. |

---

## Endpoints por área y paso del flujo

| Área de usuario | Área funcional | Método | Endpoint | Para qué parte del flujo | Acceso |
|---|---|---|---|---|---|
| **Comercialización** | **Dashboard — RFQs** | GET | `/api_comercializacion/v1/rfqs/` | Ver el listado de todos los RFQs activos (En_Com, En_Pro y completados) con deadline dinámico y progreso de proveedores. | Com / Com Admin |
| | **Dashboard — Solicitudes** | GET | `/api_comercializacion/v1/solicitudes/` | Ver en un solo objeto las solicitudes pendientes de edición (de Industrialización) y de extensión de tiempo (de Proveedores), separadas por tipo mold/trimming. | Com / Com Admin |
| | **Detalle RFQ** | GET | `/api_mold/v1/rfq-molds/<id>/` | Ver todos los datos de un RFQ Mold antes de asignar proveedores. | Com / Com Admin |
| | | GET | `/api_trimming/v1/rfq-trimmings/<id>/` | Ver todos los datos de un RFQ Trimming antes de asignar proveedores. | Com / Com Admin |
| | **Proveedores disponibles** | GET | `/api_proveedores/v1/proveedores/` | Consultar el listado de proveedores para seleccionar a quién asignar. | Com / Com Admin |
| | **Asignar proveedores** | POST | `/api_comercializacion/v1/asignaciones/crear/?tipo=mold\|trimming` | Asignar uno o varios proveedores a un RFQ. Omite duplicados silenciosamente. Al asignar el primero, el RFQ cambia a `En_Pro`. Puede llamarse múltiples veces. | Com / Com Admin |
| | **Solicitudes de edición** | PATCH | `/api_comercializacion/v1/edit-requests/<id>/aprobar/?tipo=mold\|trimming` | Aprobar una solicitud de edición de Industrialización. Regresa el RFQ a `En_Ind`. Bloqueado si el RFQ ya está en `En_Pro`. | Com / Com Admin |
| | | PATCH | `/api_comercializacion/v1/edit-requests/<id>/rechazar/?tipo=mold\|trimming` | Rechazar una solicitud de edición. El RFQ permanece en `En_Com`. | Com / Com Admin |
| | **Extensiones de tiempo** | PATCH | `/api_comercializacion/v1/extension/<id>/resolver/?tipo=mold\|trimming` | Aprobar o rechazar la solicitud de extensión de plazo de un proveedor. Si se aprueba, actualiza el `due_date` de la asignación del proveedor. | Com / Com Admin |
| | **Borrado lógico** | PATCH | `/api_mold/v1/rfq-molds/<id>/delete/` | Dar de baja un RFQ Mold sin eliminarlo físicamente. | Com Admin |
| | | PATCH | `/api_trimming/v1/rfq-trimmings/<id>/delete/` | Dar de baja un RFQ Trimming sin eliminarlo físicamente. | Com Admin |

---

## Ejemplo de llamada por paso

| Paso | Ejemplo |
|---|---|
| Ver listado de RFQs | `GET /api_comercializacion/v1/rfqs/` |
| Ver solicitudes pendientes | `GET /api_comercializacion/v1/solicitudes/` |
| Ver detalle de RFQ Mold | `GET /api_mold/v1/rfq-molds/12/` |
| Ver proveedores disponibles | `GET /api_proveedores/v1/proveedores/` |
| Asignar proveedores a RFQ Mold | `POST /api_comercializacion/v1/asignaciones/crear/?tipo=mold` · body: `{ "id_rfq": 12, "due_date": "2026-07-15", "proveedores": [1, 2, 3] }` |
| Agregar más proveedores después | `POST /api_comercializacion/v1/asignaciones/crear/?tipo=mold` · body: `{ "id_rfq": 12, "due_date": "2026-07-15", "proveedores": [4, 5] }` |
| Aprobar solicitud de edición Mold | `PATCH /api_comercializacion/v1/edit-requests/3/aprobar/?tipo=mold` · sin body |
| Rechazar solicitud de edición Trimming | `PATCH /api_comercializacion/v1/edit-requests/5/rechazar/?tipo=trimming` · sin body |
| Aprobar extensión de tiempo Mold | `PATCH /api_comercializacion/v1/extension/2/resolver/?tipo=mold` · body: `{ "status": "Aprobada" }` |
| Rechazar extensión de tiempo Trimming | `PATCH /api_comercializacion/v1/extension/4/resolver/?tipo=trimming` · body: `{ "status": "Rechazada" }` |
| Borrado lógico RFQ Mold (admin) | `PATCH /api_mold/v1/rfq-molds/12/delete/` · sin body |

---

## Estructura de respuesta — Solicitudes pendientes

```json
GET /api_comercializacion/v1/solicitudes/

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

## Reglas de negocio clave

| Regla | Detalle |
|---|---|
| Asignación de proveedores | Si un proveedor ya tiene asignación activa para ese RFQ, se omite silenciosamente sin error. Puede llamarse múltiples veces para agregar más. |
| Cambio de status al asignar | Al asignar el primer proveedor, el RFQ cambia automáticamente de `En_Com` a `En_Pro`. |
| Aprobar edición con RFQ en En_Pro | Si el RFQ ya llegó a proveedores (`En_Pro`), la aprobación de edición es bloqueada con `400`. No se puede revertir en ese estado. |
| Extensión de tiempo | Al aprobar una extensión, solo se actualiza el `due_date` de la asignación del proveedor. El `due_date` general del RFQ no se modifica. |
| Borrado lógico | Solo `Com Admin` puede hacerlo. El registro permanece en base de datos con `logical_delete = True`. |
