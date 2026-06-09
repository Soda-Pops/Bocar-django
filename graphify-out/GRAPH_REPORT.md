# Graph Report - .  (2026-06-08)

## Corpus Check
- Corpus is ~37,496 words - fits in a single context window. You may not need a graph.

## Summary
- 724 nodes · 1184 edges · 97 communities (69 shown, 28 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Asignaciones Serializers & Deadline|Asignaciones Serializers & Deadline]]
- [[_COMMUNITY_Asignaciones Admin|Asignaciones Admin]]
- [[_COMMUNITY_Chatbot Views & APIView|Chatbot Views & APIView]]
- [[_COMMUNITY_Historial Models & Admin|Historial Models & Admin]]
- [[_COMMUNITY_RFQ Trimming Serializers|RFQ Trimming Serializers]]
- [[_COMMUNITY_Asignaciones Views & URLs|Asignaciones Views & URLs]]
- [[_COMMUNITY_Chatbot Context & Tools|Chatbot Context & Tools]]
- [[_COMMUNITY_App Configs|App Configs]]
- [[_COMMUNITY_Historial Services & Tests|Historial Services & Tests]]
- [[_COMMUNITY_Notificaciones Tests|Notificaciones Tests]]
- [[_COMMUNITY_Chatbot LLM Backends|Chatbot LLM Backends]]
- [[_COMMUNITY_Industrializacion Tests|Industrializacion Tests]]
- [[_COMMUNITY_Proveedores Models|Proveedores Models]]
- [[_COMMUNITY_Auth & System Config|Auth & System Config]]
- [[_COMMUNITY_Celery Tasks|Celery Tasks]]
- [[_COMMUNITY_Notificaciones Services|Notificaciones Services]]
- [[_COMMUNITY_Chatbot Permissions|Chatbot Permissions]]
- [[_COMMUNITY_Comercializacion & Proveedores API|Comercializacion & Proveedores API]]
- [[_COMMUNITY_Industrializacion API & Archivos|Industrializacion API & Archivos]]
- [[_COMMUNITY_Notificaciones Services Tests|Notificaciones Services Tests]]
- [[_COMMUNITY_Module Group 20|Module Group 20]]
- [[_COMMUNITY_Module Group 21|Module Group 21]]
- [[_COMMUNITY_Module Group 22|Module Group 22]]
- [[_COMMUNITY_Module Group 23|Module Group 23]]
- [[_COMMUNITY_Module Group 24|Module Group 24]]
- [[_COMMUNITY_Module Group 25|Module Group 25]]
- [[_COMMUNITY_Module Group 26|Module Group 26]]
- [[_COMMUNITY_Module Group 27|Module Group 27]]
- [[_COMMUNITY_Module Group 28|Module Group 28]]
- [[_COMMUNITY_Module Group 29|Module Group 29]]
- [[_COMMUNITY_Module Group 30|Module Group 30]]
- [[_COMMUNITY_Module Group 31|Module Group 31]]
- [[_COMMUNITY_Module Group 32|Module Group 32]]
- [[_COMMUNITY_Module Group 33|Module Group 33]]
- [[_COMMUNITY_Module Group 34|Module Group 34]]
- [[_COMMUNITY_Module Group 35|Module Group 35]]
- [[_COMMUNITY_Module Group 36|Module Group 36]]
- [[_COMMUNITY_Module Group 37|Module Group 37]]
- [[_COMMUNITY_Module Group 38|Module Group 38]]
- [[_COMMUNITY_Module Group 39|Module Group 39]]
- [[_COMMUNITY_Module Group 40|Module Group 40]]
- [[_COMMUNITY_Module Group 41|Module Group 41]]
- [[_COMMUNITY_Module Group 42|Module Group 42]]
- [[_COMMUNITY_Module Group 43|Module Group 43]]
- [[_COMMUNITY_Module Group 44|Module Group 44]]
- [[_COMMUNITY_Module Group 45|Module Group 45]]
- [[_COMMUNITY_Module Group 46|Module Group 46]]
- [[_COMMUNITY_Module Group 47|Module Group 47]]
- [[_COMMUNITY_Module Group 48|Module Group 48]]
- [[_COMMUNITY_Module Group 49|Module Group 49]]
- [[_COMMUNITY_Module Group 50|Module Group 50]]
- [[_COMMUNITY_Module Group 51|Module Group 51]]
- [[_COMMUNITY_Module Group 52|Module Group 52]]
- [[_COMMUNITY_Module Group 64|Module Group 64]]

## God Nodes (most connected - your core abstractions)
1. `Asignacion_Proveedor_Mold` - 27 edges
2. `Asignacion_Proveedor_Trimming` - 27 edges
3. `HistorialFlujoTest` - 22 edges
4. `SolicitudExtensionMold` - 21 edges
5. `SolicitudExtensionTrimming` - 21 edges
6. `ExtensionStatus` - 20 edges
7. `str` - 16 edges
8. `RFQTrimmingListCreateView` - 14 edges
9. `RFQMoldComercializacionSerializer` - 13 edges
10. `RFQTrimmingComercializacionSerializer` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Email Template: rfq_a_compras.html` ----> `Área: Comercialización`  [EXTRACTED]
  notificaciones/templates/notificaciones/rfq_a_compras.html → docs/flujo_comercializacion.md
- `Email Template: rfq_a_proveedores.html` ----> `Área: Proveedores`  [EXTRACTED]
  notificaciones/templates/notificaciones/rfq_a_proveedores.html → docs/flujo_proveedor.md
- `_parse_bool()` --references--> `bool`  [EXTRACTED]
  chatbot/tools.py → Asignaciones/serializers.py
- `Bocar Django System` ----> `API: /auth/ (Authentication Endpoints)`  [EXTRACTED]
  README.MD → docs/flujo_completo.md
- `Bocar Django System` ----> `Módulo: Chatbot`  [EXTRACTED]
  README.MD → docs/chatbot.md

## Import Cycles
- None detected.

## Communities (97 total, 28 thin omitted)

### Community 0 - "Asignaciones Serializers & Deadline"
Cohesion: 0.06
Nodes (38): _calcular_deadline(), Tiempo restante dinámico igual que en Comercialización., _calcular_deadline(), _calcular_progreso(), CrearAsignacionesSerializer, Meta, Recibe el queryset de asignaciones de un RFQ y devuelve el string de progreso., Recibe un date y devuelve un string dinámico:     - Si ya venció          → "Ve (+30 more)

### Community 1 - "Asignaciones Admin"
Cohesion: 0.10
Nodes (28): CustomAsignacion_Proveedor_MoldAdmin, CustomAsignacion_Proveedor_TrimmingAdmin, Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming, ExtensionStatus, Meta, SolicitudExtensionMold, SolicitudExtensionTrimming (+20 more)

### Community 2 - "Chatbot Views & APIView"
Cohesion: 0.07
Nodes (28): APIView, ChatbotQueryView, POST /api_chatbot/v1/query/     Recibe una pregunta en lenguaje natural y devuel, PATCH /api_general/v1/rfq/<id>/delete/?tipo=mold|trimming     Borrado lógico un, DELETE /api_general/v1/rfq/<id>/borrador/?tipo=mold|trimming     Eliminación fí, RFQBorradorDeleteView, RFQGlobalCountView, RFQLogicalDeleteView (+20 more)

### Community 3 - "Historial Models & Admin"
Cohesion: 0.06
Nodes (26): RFQHistorialAdmin, Evento, Meta, Registro de auditoría del ciclo de vida de una RFQ (Mold o Trimming).      No, RFQHistorial, Tipo, Meta, RFQHistorialSerializer (+18 more)

### Community 4 - "RFQ Trimming Serializers"
Cohesion: 0.10
Nodes (21): Meta, RFQTrimmingCreateSerializer, RFQTrimmingDetailSerializer, RFQTrimmingFileSerializer, RFQTrimmingListSerializer, TrimmingEditRequestApproveSerializer, TrimmingEditRequestCreateSerializer, TrimmingEditRequestListSerializer (+13 more)

### Community 5 - "Asignaciones Views & URLs"
Cohesion: 0.09
Nodes (23): AsignacionBorradorActualizarView, AsignacionBorradorDetalleView, AsignacionEnviarRespuestaView, AsignacionesProveedorView, AsignacionResponderView, AsignacionRFQDetalleView, _get_asignacion_mold(), _get_asignacion_trimming() (+15 more)

### Community 6 - "Chatbot Context & Tools"
Cohesion: 0.08
Nodes (30): API: /api_chatbot/v1/, build_system_prompt(), get_tools_for_role(), str, Módulo: Chatbot, _extract_json(), process_query(), str (+22 more)

### Community 7 - "App Configs"
Cohesion: 0.07
Nodes (15): AppConfig, AsignacionesConfig, ChatbotConfig, ComercializacionConfig, GeneralRfqsConfig, HistorialConfig, IndustrializacionConfig, ModuloIaConfig (+7 more)

### Community 8 - "Historial Services & Tests"
Cohesion: 0.20
Nodes (3): Crea una entrada de historial para una RFQ.      Es defensivo: un fallo al reg, registrar_historial(), HistorialFlujoTest

### Community 9 - "Notificaciones Tests"
Cohesion: 0.12
Nodes (6): EnviarTest, FlujoNotificacionesViewsTest, make_user(), NotificacionTasksTest, Tests sobre la función _enviar: BCC, TO, y caso vacío., TestCase

### Community 10 - "Chatbot LLM Backends"
Cohesion: 0.12
Nodes (11): ABC, BaseLLM, str, str, str, BaseLLM, Envía un mensaje al modelo y devuelve su respuesta como string., GeminiLLM (+3 more)

### Community 11 - "Industrializacion Tests"
Cohesion: 0.12
Nodes (9): APITestCase, RFQEditarViewTests, CustomRFQ_TrimmingAdmin, EditStatus, Meta, RFQ_Trimming, RFQ_Trimming_EditRequest, RFQ_Trimming_File (+1 more)

### Community 12 - "Proveedores Models"
Cohesion: 0.19
Nodes (9): Continente, Meta, Proveedor, Meta, ProveedorListSerializer, Serializer de solo lectura para listar proveedores.     Expone únicamente los c, ProveedorListSerializerTests, ProveedorListView (+1 more)

### Community 13 - "Auth & System Config"
Cohesion: 0.12
Nodes (18): API: /auth/ (Authentication Endpoints), API: /api_historial/v1/, Bocar Django System, CookieJWTAuthentication, CORS Configuration, Security: DEBUG/ALLOWED_HOSTS Hardcoded (Fixed), Security: DEFAULT_PERMISSION_CLASSES Missing (Pending), Django REST Framework (DRF) (+10 more)

### Community 14 - "Celery Tasks"
Cohesion: 0.19
Nodes (11): Celery (Async Task Queue), _get_rfq(), _get_user(), notificar_cancelacion_confirmada(), notificar_cancelacion_solicitada(), notificar_comercializacion(), notificar_cotizacion_recibida(), notificar_modificacion_rfq() (+3 more)

### Community 15 - "Notificaciones Services"
Cohesion: 0.23
Nodes (15): _emails_admins(), _emails_por_rol(), _enviar(), notificar_cancelacion_confirmada(), notificar_cancelacion_solicitada(), notificar_comercializacion(), notificar_cotizacion_recibida(), notificar_modificacion_rfq() (+7 more)

### Community 16 - "Chatbot Permissions"
Cohesion: 0.18
Nodes (7): BasePermission, IsChatbotAllowed, IsAdminUser, IsComercializacionAdmin, IsComercializacionUser, IsProveedor, Solo usuarios con role='Pro'.     Usado en: consulta de asignaciones propias de

### Community 17 - "Comercializacion & Proveedores API"
Cohesion: 0.23
Nodes (12): API: /api_comercializacion/v1/, API: /api_proveedores/v1/, Área: Comercialización, Área: Proveedores, Asignación de Proveedor, Borrador de Cotización (Draft), Cost Breakdown, Due Date / Deadline (+4 more)

### Community 18 - "Industrializacion API & Archivos"
Cohesion: 0.21
Nodes (10): API: /api_industrializacion/v1/, Archivos Adjuntos (Attachments), Área: Industrialización, Logical Delete, CustomProveedorAdmin, RFQ (Request for Quotation), RFQ Mold, RFQ Trimming (+2 more)

### Community 20 - "Module Group 20"
Cohesion: 0.20
Nodes (7): Cost_Breakdown_Trimming, Currency, float_field(), List, Meta, Shortcut para campos float con default 0, Status

### Community 21 - "Module Group 21"
Cohesion: 0.31
Nodes (6): _fecha_invalida(), HistorialPagination, _parse_fecha(), GET /api_historial/v1/<tipo>/<rfq_id>/     Devuelve el historial de eventos de, RFQHistorialView, PageNumberPagination

### Community 22 - "Module Group 22"
Cohesion: 0.25
Nodes (8): Email Template: cancelacion_confirmada.html, Email Template: modificacion_rfq.html, Email Template: rfq_a_compras.html, Email Template: rfq_a_proveedores.html, Módulo: Notificaciones, Notification: notificar_comercializacion, Notification: notificar_proveedores, NOTIFICATIONS_ENABLED Env Flag

### Community 23 - "Module Group 23"
Cohesion: 0.25
Nodes (5): JWTAuthentication, OpenApiAuthenticationExtension, CookieJWTAuthentication, CookieJWTAuthenticationScheme, Extiende JWTAuthentication para leer el access token     de la cookie HttpOnly

### Community 25 - "Module Group 25"
Cohesion: 0.33
Nodes (3): AbstractUser, CustomUser, Roles

### Community 26 - "Module Group 26"
Cohesion: 0.33
Nodes (6): RFQ Lifecycle / State Machine, Solicitud de Edición, Status: Completado, Status: En_Com, Status: En_Ind, Status: En_Pro

### Community 27 - "Module Group 27"
Cohesion: 0.40
Nodes (5): Email Template: solicitud_cancelacion.html, is_admin Flag, Notification: notificar_cancelacion_solicitada (Pending), Role: Com (Comercialización), Role: Ind (Industrialización)

## Knowledge Gaps
- **73 isolated node(s):** `allow`, `Migration`, `Migration`, `Meta`, `Meta` (+68 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulo: Historial / Auditoría` connect `Auth & System Config` to `Industrializacion API & Archivos`, `Historial Models & Admin`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `Bocar Django System` connect `Auth & System Config` to `Industrializacion API & Archivos`, `Chatbot Context & Tools`, `Module Group 22`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `RFQ (Request for Quotation)` connect `Industrializacion API & Archivos` to `Comercializacion & Proveedores API`, `Module Group 26`, `Auth & System Config`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Asignacion_Proveedor_Mold` (e.g. with `CustomAsignacion_Proveedor_MoldAdmin` and `CustomAsignacion_Proveedor_TrimmingAdmin`) actually correct?**
  _`Asignacion_Proveedor_Mold` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `Asignacion_Proveedor_Trimming` (e.g. with `CustomAsignacion_Proveedor_MoldAdmin` and `CustomAsignacion_Proveedor_TrimmingAdmin`) actually correct?**
  _`Asignacion_Proveedor_Trimming` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `SolicitudExtensionMold` (e.g. with `AsignacionMoldProveedorSerializer` and `AsignacionTrimmingProveedorSerializer`) actually correct?**
  _`SolicitudExtensionMold` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `allow`, `Migration`, `Migration` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._