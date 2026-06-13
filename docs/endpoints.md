# Referencia de Endpoints — Sistema Bocar

> Documentación interactiva siempre actualizada: **Swagger UI** en `/schema/swagger/` y **ReDoc** en `/schema/redoc/`. Todos los endpoints requieren autenticación excepto `POST /auth/login/`.

## Convenciones

- La mayoría de los endpoints de negocio requieren el query parameter `?tipo=mold` o `?tipo=trimming`. Si se omite, la API responde `400`.
- La autenticación viaja en cookies HttpOnly — en `fetch`/`axios` usa `credentials: 'include'` / `withCredentials: true`.

---

## Autenticación — `/auth/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `POST` | `/auth/login/` | público | Autentica con email y contraseña; establece cookies HttpOnly con los tokens. Límite: 5 intentos/min |
| `POST` | `/auth/logout/` | cualquiera | Cierra sesión e invalida el refresh token |
| `POST` | `/auth/refresh/` | cualquiera | Emite un nuevo access token usando la cookie de refresh |
| `GET` | `/auth/me/` | cualquiera | Devuelve los datos del usuario autenticado (id, email, rol, is_admin) |

## RFQ Mold — `/api_mold/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfq-molds/` | autenticado | Lista los RFQ Mold activos con campos resumidos |
| `GET` | `/rfq-molds/<id>/` | autenticado | Detalle completo de un RFQ Mold |
| `PATCH` | `/rfq-molds/<id>/delete/` | `Com` admin | Borrado lógico del RFQ |

## RFQ Trimming — `/api_trimming/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfq-trimmings/` | autenticado | Lista los RFQ Trimming activos con campos resumidos |
| `GET` | `/rfq-trimmings/<id>/` | autenticado | Detalle completo de un RFQ Trimming |
| `PATCH` | `/rfq-trimmings/<id>/delete/` | `Com` admin | Borrado lógico del RFQ |

## General — `/api_general/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfq-count/` | autenticado | Conteo de RFQs (Mold + Trimming) por estado; acepta `?user_id=<id>` |
| `PATCH` | `/rfq/<id>/delete/?tipo=mold\|trimming` | admin | Borrado lógico unificado por tipo |
| `DELETE` | `/rfq/<id>/borrador/?tipo=mold\|trimming` | `Ind` | Elimina físicamente un borrador propio en `En_Ind` |

## Industrialización — `/api_industrializacion/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfqs/` | `Ind` | Lista RFQs: borradores propios (`En_Ind`) y todos los demás estados |
| `POST` | `/rfq/?tipo=mold\|trimming` | `Ind` | Crea una RFQ; acepta archivos en `multipart/form-data` |
| `PATCH` | `/rfq/<id>/?tipo=mold\|trimming` | `Ind` | Edita una RFQ (solo en estado `En_Ind`) |
| `POST` | `/rfq/<id>/enviar/?tipo=mold\|trimming` | `Ind` | Envía la RFQ a Comercialización (`En_Ind → En_Com`) |
| `POST` | `/edit-requests/?tipo=mold\|trimming` | `Ind` | Solicita regresar una RFQ de `En_Com` a `En_Ind` |

## Comercialización — `/api_comercializacion/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/rfqs/` | `Com` | Lista todos los RFQs activos con progreso de respuesta de proveedores |
| `GET` | `/solicitudes/` | `Com` | Solicitudes pendientes: de edición (Ind) y de extensión (Pro) |
| `POST` | `/asignaciones/crear/?tipo=mold\|trimming` | `Com` | Asigna proveedores a una RFQ y la mueve a `En_Pro`; omite duplicados |
| `PATCH` | `/edit-requests/<id>/aprobar/?tipo=mold\|trimming` | `Com` admin | Aprueba la solicitud de edición; la RFQ vuelve a `En_Ind` |
| `PATCH` | `/edit-requests/<id>/rechazar/?tipo=mold\|trimming` | `Com` admin | Rechaza la solicitud; la RFQ permanece en `En_Com` |
| `PATCH` | `/extension/<id>/resolver/?tipo=mold\|trimming` | `Com` | Aprueba/rechaza una extensión de plazo; si aprueba, actualiza el `due_date` |
| `GET` | `/rfq/<id>/comparativa/?tipo=mold\|trimming` | `Com` | Comparativa de precios de los proveedores que ya respondieron (desglose + total) |
| `POST` | `/rfq/<id>/cerrar/?tipo=mold\|trimming` | `Com` | Cierre formal de la RFQ con motivo (`closure_reason`); requiere asignaciones cerradas/vencidas |
| `PATCH` | `/rfq/<id>/deadline/?tipo=mold\|trimming` | `Com` | Extiende el deadline de una RFQ expirada (la nueva fecha debe ser futura) y reabre las asignaciones pendientes |

## Proveedores — `/api_proveedores/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/proveedores/` | `Com` | Lista todos los proveedores registrados (incluye su `rating`) |

## Asignaciones — `/api_proveedores/v1/asginaciones/`

> Nota: el prefijo contiene un error tipográfico histórico (`asginaciones`) que se conserva por compatibilidad con el frontend.

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/mis-asignaciones/` | `Pro` | Asignaciones propias, separadas en pendientes y contestadas |
| `GET` | `/detalle/<id>/?tipo=mold\|trimming` | `Pro` | Detalle completo de la RFQ de una asignación propia |
| `POST` | `/responder/<id>/?tipo=mold\|trimming` | `Pro` | Guarda el cost breakdown como **borrador** (no marca respondida); acepta archivos adjuntos (`archivos`, multipart) |
| `GET` | `/responder/<id>/detalle/?tipo=mold\|trimming` | `Pro` | Devuelve el borrador o la respuesta enviada |
| `PATCH` | `/responder/<id>/actualizar/?tipo=mold\|trimming` | `Pro` | Actualiza el borrador (solo si sigue en `draft`) |
| `POST` | `/responder/<id>/enviar/?tipo=mold\|trimming` | `Pro` | Envío definitivo (`draft → submitted`); irreversible |
| `POST` | `/extension/solicitar/<id>/?tipo=mold\|trimming` | `Pro` | Solicita extensión de plazo (una pendiente a la vez) |
| `PATCH` | `/extension/resolver/<id>/?tipo=mold\|trimming` | `Com` | (Legacy) Resuelve una extensión — preferir el endpoint de Comercialización |

## Evaluaciones — `/api_evaluaciones/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `POST` | `/crear/?tipo=mold\|trimming` | `Com` | Evalúa la entrega de una asignación. Body: `asignacion_id`, `calidad_cotizacion` (1–5), `comunicacion` (1–5), `comentarios`. Las métricas de puntualidad/extensiones/envío se calculan solas. Devuelve el `score` y el nuevo rating del proveedor |
| `GET` | `/proveedor/<id>/` | `Com` | Historial de evaluaciones + resumen: rating, % puntualidad, % sin extensiones, promedios |

## Historial — `/api_historial/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET` | `/<tipo>/<rfq_id>/` | autenticado | Timeline de eventos de una RFQ. Filtros: `?evento=`, `?actor=`, `?desde=`, `?hasta=`. Paginación: `?page=`, `?page_size=` (máx. 100) |

## Chatbot — `/api_chatbot/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `POST` | `/query/` | con rol asignado | Pregunta en lenguaje natural; responde solo con datos accesibles para el rol del usuario |

## Módulo IA — `/modulo-ia/` y `/api_ia/v1/`

| Método | Ruta | Rol | Descripción |
|---|---|---|---|
| `GET`/`POST` | `/modulo-ia/` | autenticado | Panel HTML para solicitar reentrenamiento del módulo de IA (no es API REST) |
| `POST` | `/api_ia/v1/predictions/` | autenticado | Proxy hacia el servicio externo de predicciones de IA. Reenvía el body JSON tal cual. Responde `504` si el servicio externo no contesta en 30 s y `502` si no está disponible |

## Documentación y administración

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/schema/swagger/` | Swagger UI interactivo |
| `GET` | `/schema/redoc/` | Documentación ReDoc |
| `GET` | `/api/schema/` | Esquema OpenAPI (YAML/JSON) |
| `GET` | `/admin/` | Panel de administración de Django (requiere `is_staff=True`) |

---

## Códigos de error comunes

| Código | Causa | Acción correctiva |
|---|---|---|
| `400 Bad Request` | Falta `?tipo=` o body inválido | Agrega el query param o corrige los campos indicados |
| `401 Unauthorized` | Cookie `access_token` ausente o expirada | Llama a `POST /auth/refresh/`; si falla, vuelve a hacer login |
| `403 Forbidden` | Rol sin permiso, o plazo vencido | Verifica el rol; el proveedor puede solicitar extensión |
| `404 Not Found` | Recurso inexistente o no pertenece al usuario | Verifica el id y la propiedad del recurso |
| `409 Conflict` | Recurso duplicado (borrador ya existe / respuesta ya enviada) | Usa el endpoint de actualización (`PATCH`) |
| `429 Too Many Requests` | Más de 5 intentos de login por minuto | Espera un minuto y reintenta |
| `502 / 504` | Servicio externo de predicciones caído o sin responder | Verificar disponibilidad del servicio de IA |
