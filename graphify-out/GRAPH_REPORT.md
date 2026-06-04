# Graph Report - .  (2026-06-04)

## Corpus Check
- Corpus is ~26,699 words - fits in a single context window. You may not need a graph.

## Summary
- 600 nodes · 1508 edges · 84 communities (56 shown, 28 thin omitted)
- Extraction: 65% EXTRACTED · 35% INFERRED · 0% AMBIGUOUS · INFERRED: 530 edges (avg confidence: 0.51)
- Token cost: 900 input · 420 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Assignment Admin Interfaces|Assignment Admin Interfaces]]
- [[_COMMUNITY_Historial & Assignment Serializers|Historial & Assignment Serializers]]
- [[_COMMUNITY_RFQ Trimming Management|RFQ Trimming Management]]
- [[_COMMUNITY_Comercialización & Permissions|Comercialización & Permissions]]
- [[_COMMUNITY_Notification Tests|Notification Tests]]
- [[_COMMUNITY_User & Notification Services|User & Notification Services]]
- [[_COMMUNITY_Comercialización Flow Docs|Comercialización Flow Docs]]
- [[_COMMUNITY_General RFQ API Views|General RFQ API Views]]
- [[_COMMUNITY_App Configurations|App Configurations]]
- [[_COMMUNITY_Historial Audit Trail|Historial Audit Trail]]
- [[_COMMUNITY_Settings & Proveedor Admin|Settings & Proveedor Admin]]
- [[_COMMUNITY_Historial Test Suite|Historial Test Suite]]
- [[_COMMUNITY_JWT Token Serializers|JWT Token Serializers]]
- [[_COMMUNITY_Django Management|Django Management]]
- [[_COMMUNITY_Asignaciones Migrations|Asignaciones Migrations]]
- [[_COMMUNITY_Module Group 15|Module Group 15]]
- [[_COMMUNITY_Module Group 17|Module Group 17]]
- [[_COMMUNITY_Module Group 18|Module Group 18]]
- [[_COMMUNITY_Module Group 19|Module Group 19]]
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

## God Nodes (most connected - your core abstractions)
1. `Asignacion_Proveedor_Mold` - 53 edges
2. `Asignacion_Proveedor_Trimming` - 48 edges
3. `SolicitudExtensionMold` - 37 edges
4. `SolicitudExtensionTrimming` - 37 edges
5. `registrar_historial()` - 29 edges
6. `AsignacionEnviarRespuestaView` - 28 edges
7. `RFQ_Mold` - 28 edges
8. `SolicitudExtensionMoldResolverSerializer` - 26 edges
9. `SolicitudExtensionTrimmingResolverSerializer` - 26 edges
10. `RFQ_Trimming` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Currency` --uses--> `Asignacion_Proveedor_Mold`  [INFERRED]
  Prov_RFQ_Mold/models.py → Asignaciones/models.py
- `Meta` --uses--> `Asignacion_Proveedor_Mold`  [INFERRED]
  Prov_RFQ_Mold/models.py → Asignaciones/models.py
- `Status` --uses--> `Asignacion_Proveedor_Mold`  [INFERRED]
  Prov_RFQ_Mold/models.py → Asignaciones/models.py
- `CrearAsignacionesView` --uses--> `Asignacion_Proveedor_Mold`  [INFERRED]
  Comercializacion/views.py → Asignaciones/models.py
- `EditRequestAprobarView` --uses--> `Asignacion_Proveedor_Mold`  [INFERRED]
  Comercializacion/views.py → Asignaciones/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **RFQ Lifecycle: Industrialización → Comercialización → Proveedor** — docs_flujo_industrializacion_flujo_industrializacion, docs_flujo_comercializacion_flujo_comercializacion, docs_flujo_proveedor_flujo_proveedor [EXTRACTED 1.00]
- **Email Notification Templates serving all RFQ lifecycle events** — notificaciones_rfq_a_compras_template, notificaciones_rfq_a_proveedores_template, notificaciones_cotizacion_recibida_template, notificaciones_modificacion_rfq_template, notificaciones_cancelacion_confirmada_template, notificaciones_solicitud_cancelacion_template [EXTRACTED 1.00]
- **RFQ Status Transitions across Ind, Com, and Pro roles** — docs_flujo_industrializacion_rfq_status, docs_flujo_comercializacion_asignacion_proveedores, docs_flujo_proveedor_cost_breakdown [INFERRED 0.95]

## Communities (84 total, 28 thin omitted)

### Community 0 - "Assignment Admin Interfaces"
Cohesion: 0.09
Nodes (53): CustomAsignacion_Proveedor_MoldAdmin, CustomAsignacion_Proveedor_TrimmingAdmin, Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming, ExtensionStatus, Meta, SolicitudExtensionMold, SolicitudExtensionTrimming (+45 more)

### Community 1 - "Historial & Assignment Serializers"
Cohesion: 0.06
Nodes (48): diff_campos(), Crea una entrada de historial para una RFQ.      Es defensivo: un fallo al reg, Devuelve {campo: {'antes': x, 'despues': y}} para los campos que cambian., Convierte valores no nativos de JSON (date, Decimal, etc.) a algo serializable., registrar_historial(), _serializable(), DiffCamposTest, make_user() (+40 more)

### Community 2 - "RFQ Trimming Management"
Cohesion: 0.11
Nodes (28): CustomRFQ_TrimmingAdmin, EditStatus, Meta, RFQ_Trimming, RFQ_Trimming_EditRequest, RFQ_Trimming_File, Status, Meta (+20 more)

### Community 3 - "Comercialización & Permissions"
Cohesion: 0.11
Nodes (27): SolicitudExtensionMoldListSerializer, SolicitudExtensionTrimmingListSerializer, BasePermission, _calcular_deadline(), _calcular_progreso(), CrearAsignacionesSerializer, Meta, str (+19 more)

### Community 4 - "Notification Tests"
Cohesion: 0.06
Nodes (12): EnviarTest, FlujoNotificacionesViewsTest, make_user(), NotificacionServicesTest, NotificacionTasksTest, Tests sobre la función _enviar: BCC, TO, y caso vacío., Cost_Breakdown_Mold, Currency (+4 more)

### Community 5 - "User & Notification Services"
Cohesion: 0.10
Nodes (28): AbstractUser, _emails_admins(), _emails_por_rol(), _enviar(), notificar_cancelacion_confirmada(), notificar_cancelacion_solicitada(), notificar_comercializacion(), notificar_cotizacion_recibida() (+20 more)

### Community 6 - "Comercialización Flow Docs"
Cohesion: 0.09
Nodes (31): Asignación de Proveedores, Borrado Lógico RFQ, Extensiones de Tiempo (Comercialización), Flujo Comercialización, Rol Com (Comercialización), Rol Com Admin, Solicitudes de Edición (Comercialización), Crear RFQ (Industrialización) (+23 more)

### Community 7 - "General RFQ API Views"
Cohesion: 0.11
Nodes (15): APIView, RFQGlobalCountView, JWTAuthentication, OpenApiAuthenticationExtension, CookieJWTAuthentication, CookieJWTAuthenticationScheme, Extiende JWTAuthentication para leer el access token     de la cookie HttpOnly, LoginView (+7 more)

### Community 8 - "App Configurations"
Cohesion: 0.08
Nodes (13): AppConfig, AsignacionesConfig, ComercializacionConfig, GeneralRfqsConfig, HistorialConfig, IndustrializacionConfig, NotificacionesConfig, ProvRfqMoldConfig (+5 more)

### Community 9 - "Historial Audit Trail"
Cohesion: 0.17
Nodes (14): RFQHistorialAdmin, Evento, Meta, Registro de auditoría del ciclo de vida de una RFQ (Mold o Trimming).      No, RFQHistorial, Tipo, Meta, RFQHistorialSerializer (+6 more)

### Community 10 - "Settings & Proveedor Admin"
Cohesion: 0.15
Nodes (10): Django settings for Bocar project.  Generated by 'django-admin startproject' u, CustomProveedorAdmin, Continente, Meta, Proveedor, Meta, ProveedorListSerializer, Serializer de solo lectura para listar proveedores.     Expone únicamente los c (+2 more)

## Knowledge Gaps
- **46 isolated node(s):** `Migration`, `Migration`, `Meta`, `Meta`, `Migration` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Asignacion_Proveedor_Mold` connect `Assignment Admin Interfaces` to `Comercialización & Permissions`, `Notification Tests`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `registrar_historial()` connect `Historial & Assignment Serializers` to `Assignment Admin Interfaces`, `Historial Test Suite`, `RFQ Trimming Management`, `Comercialización & Permissions`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `RFQ_Mold` connect `Historial & Assignment Serializers` to `Assignment Admin Interfaces`, `Comercialización & Permissions`, `Notification Tests`, `User & Notification Services`, `General RFQ API Views`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Asignacion_Proveedor_Mold` (e.g. with `CustomAsignacion_Proveedor_MoldAdmin` and `CustomAsignacion_Proveedor_TrimmingAdmin`) actually correct?**
  _`Asignacion_Proveedor_Mold` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `Asignacion_Proveedor_Trimming` (e.g. with `CustomAsignacion_Proveedor_MoldAdmin` and `CustomAsignacion_Proveedor_TrimmingAdmin`) actually correct?**
  _`Asignacion_Proveedor_Trimming` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `SolicitudExtensionMold` (e.g. with `AsignacionMoldProveedorSerializer` and `AsignacionTrimmingProveedorSerializer`) actually correct?**
  _`SolicitudExtensionMold` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `SolicitudExtensionTrimming` (e.g. with `AsignacionMoldProveedorSerializer` and `AsignacionTrimmingProveedorSerializer`) actually correct?**
  _`SolicitudExtensionTrimming` has 32 INFERRED edges - model-reasoned connections that need verification._