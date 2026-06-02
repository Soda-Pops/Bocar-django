# Flujo de usuario — Industrialización

> **Nota:** Todos los flujos asumen que el usuario ya realizó login y cuenta con un token de sesión válido en cookie.

---

## Roles

| Rol | Descripción |
|---|---|
| `Ind` | Puede crear, editar, enviar RFQs y solicitar ediciones. |
| `Ind Admin` | Todo lo anterior + borrado lógico sin aprobación. |

---

## Endpoints por área y paso del flujo

| Área de usuario | Área funcional | Método | Endpoint | Para qué parte del flujo | Acceso |
|---|---|---|---|---|---|
| **Industrialización** | **Dashboard** | GET | `/api_industrializacion/v1/rfqs/` | Ver el listado de todos los RFQs. Borradores: solo los propios. En_Com / En_Pro / Completados: todos los usuarios. | Ind / Ind Admin |
| | **Dashboard** | GET | `/api_general/v1/rfq-count/?user_id=<id>` | Ver el conteo rápido de RFQs por status e histograma mensual del año. | Ind / Ind Admin |
| | **Crear RFQ** | POST | `/api_industrializacion/v1/rfq/?tipo=mold\|trimming` | Crear un nuevo RFQ y guardarlo como borrador (`En_Ind`). Acepta archivos opcionales. | Ind / Ind Admin |
| | **Detalle RFQ** | GET | `/api_mold/v1/rfq-molds/<id>/` | Ver todos los datos de un RFQ Mold, incluyendo archivos adjuntos. Retomar un borrador. | Ind / Ind Admin |
| | | GET | `/api_trimming/v1/rfq-trimmings/<id>/` | Ver todos los datos de un RFQ Trimming, incluyendo archivos adjuntos. Retomar un borrador. | Ind / Ind Admin |
| | **Editar RFQ** | PATCH | `/api_industrializacion/v1/rfq/<id>/?tipo=mold\|trimming` | Editar un RFQ mientras esté en borrador (`En_Ind`). Rechazado con `403` si ya fue enviado. | Ind / Ind Admin |
| | **Enviar RFQ** | POST | `/api_industrializacion/v1/rfq/<id>/enviar/?tipo=mold\|trimming` | Enviar el RFQ a Comercialización (`En_Ind` → `En_Com`). Requiere al menos un archivo adjunto. | Ind / Ind Admin |
| | **Solicitar edición** | POST | `/api_industrializacion/v1/edit-requests/?tipo=mold\|trimming` | Solicitar que Comercialización regrese el RFQ a `En_Ind` para corregirlo. Solo válido si está en `En_Com`. Bloqueado si ya está en `En_Pro`. | Ind / Ind Admin |
| | **Borrado lógico** | PATCH | `/api_mold/v1/rfq-molds/<id>/delete/` | Dar de baja un RFQ Mold sin eliminarlo físicamente. | Ind Admin |
| | | PATCH | `/api_trimming/v1/rfq-trimmings/<id>/delete/` | Dar de baja un RFQ Trimming sin eliminarlo físicamente. | Ind Admin |

---

## Ejemplo de llamada por paso

| Paso | Ejemplo |
|---|---|
| Ver listado | `GET /api_industrializacion/v1/rfqs/` |
| Ver conteo | `GET /api_general/v1/rfq-count/?user_id=3` |
| Crear RFQ Mold | `POST /api_industrializacion/v1/rfq/?tipo=mold` · body: `multipart/form-data` con campos del RFQ y archivos opcionales |
| Crear RFQ Trimming | `POST /api_industrializacion/v1/rfq/?tipo=trimming` · body: `multipart/form-data` con campos del RFQ y archivos opcionales |
| Ver detalle Mold | `GET /api_mold/v1/rfq-molds/12/` |
| Ver detalle Trimming | `GET /api_trimming/v1/rfq-trimmings/7/` |
| Editar borrador Mold | `PATCH /api_industrializacion/v1/rfq/12/?tipo=mold` · body: solo los campos a actualizar |
| Enviar Mold | `POST /api_industrializacion/v1/rfq/12/enviar/?tipo=mold` · sin body |
| Solicitar edición Mold | `POST /api_industrializacion/v1/edit-requests/?tipo=mold` · body: `{ "rfq_mold": 12, "reason": "Error en dimensiones." }` |
| Solicitar edición Trimming | `POST /api_industrializacion/v1/edit-requests/?tipo=trimming` · body: `{ "rfq_trimming": 7, "reason": "Datos incorrectos." }` |
| Borrar Mold (admin) | `PATCH /api_mold/v1/rfq-molds/12/delete/` · sin body |

---

## Reglas de negocio clave

| Regla | Detalle |
|---|---|
| Visibilidad de borradores | En el listado, los RFQs en `En_Ind` solo son visibles para su creador. |
| Edición bloqueada | Si el RFQ está en `En_Com` o `En_Pro`, el endpoint de edición retorna `403`. La única salida es una solicitud de edición aprobada por Comercialización Admin. |
| Archivo obligatorio al enviar | No se puede cambiar de `En_Ind` a `En_Com` si el RFQ no tiene al menos un archivo adjunto (puede haberse subido en cualquier edición previa). |
| Solicitud de edición bloqueada en En_Pro | Si el RFQ ya llegó a proveedores (`En_Pro`), la solicitud de edición es rechazada con `400`. Ya no es posible revertirlo. |
| Borrado lógico | Solo `Ind Admin` puede hacerlo. El registro permanece en base de datos con `logical_delete = True`. |
