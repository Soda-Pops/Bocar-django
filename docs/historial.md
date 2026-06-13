# Historial / Auditoría de RFQs

La app `historial/` registra automáticamente los eventos del ciclo de vida de cada RFQ
(Mold y Trimming): creación, edición (con diff de campos antes/después), envío a Comercialización,
asignación/envío a proveedores, solicitud/aprobación/rechazo de edición, cotización recibida,
cancelación y extensiones de tiempo (solicitar/aprobar/rechazar).

El registro se engancha en los **serializers compartidos** (cubre los endpoints viejos *y* nuevos) y en
las vistas con punto único, mediante el helper `historial.services.registrar_historial`. No usa señales
ni middleware: cada evento se registra de forma explícita y con su `actor`.

---

## Consulta

```
GET /api_historial/v1/<tipo>/<rfq_id>/      # tipo = mold | trimming
```

Devuelve el timeline ordenado (más reciente primero). Requiere autenticación. Cada evento incluye:
`evento`, `actor`, `timestamp`, `status_anterior`/`status_nuevo`, `cambios` (diff de edición) y
`detalle` (contexto extra: proveedores, nueva_fecha, motivo, etc.).

---

## Filtros (query params, opcionales y combinables)

| Param | Descripción | Ejemplo |
|-------|-------------|---------|
| `evento` | Tipo de evento; repetible para varios | `?evento=CANCELACION&evento=EDICION` |
| `actor` | ID del usuario que ejecutó el evento | `?actor=5` |
| `desde` | Fecha inicial inclusive (`YYYY-MM-DD`) | `?desde=2026-01-01` |
| `hasta` | Fecha final inclusive (`YYYY-MM-DD`) | `?hasta=2026-06-30` |

Valores inválidos (evento inexistente, actor no numérico o fecha mal formada) devuelven `400`.

---

## Paginación

La respuesta viene paginada con el formato `{count, next, previous, results}`.

| Param | Descripción | Default |
|-------|-------------|---------|
| `page` | Número de página | `1` |
| `page_size` | Eventos por página (máx. 100) | `20` |

> El historial arranca desde su despliegue; las RFQs creadas antes no tienen registro retroactivo.

---

## Eventos registrados

| Evento | Cuándo se registra |
|--------|--------------------|
| `CREACION` | Al crear una RFQ |
| `EDICION` | Al editar campos de una RFQ (incluye diff antes/después) |
| `ENVIO_COMERCIALIZACION` | Al pasar de `En_Ind` → `En_Com` |
| `ENVIO_PROVEEDORES` | Al pasar de `En_Com` → `En_Pro` |
| `ASIGNACION_PROVEEDORES` | Al asignar proveedores a un RFQ |
| `SOLICITUD_EDICION` | Al solicitar regresar a `En_Ind` |
| `EDICION_APROBADA` | Al aprobar la solicitud de edición |
| `EDICION_RECHAZADA` | Al rechazar la solicitud de edición |
| `COTIZACION_RECIBIDA` | Al enviar el proveedor su cost breakdown |
| `CANCELACION` | Al eliminar lógicamente una RFQ |
| `EXTENSION_SOLICITADA` | Al solicitar extensión de plazo |
| `EXTENSION_APROBADA` | Al aprobar la extensión |
| `EXTENSION_RECHAZADA` | Al rechazar la extensión |
| `EVALUACION_PROVEEDOR` | Al registrar una evaluación de proveedor por Compras |
| `CIERRE_RFQ` | Al cerrar formalmente un RFQ (Comercialización registra el motivo) |

---

## Tests

```bash
python manage.py test historial
```

Cubre (15 tests): helper de diff; que cada evento del flujo cree su fila —creación, edición con diff,
envío a Comercialización, asignación + envío a proveedores, cancelación, aprobación de edición (vía
serializer compartido, route-agnostic)—; el endpoint de lectura (autenticado y sin auth); los filtros
(por evento, varios eventos, actor, y validación de evento/fecha inválidos); y la paginación.
