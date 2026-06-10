# Plan de Pruebas — Chatbot Bocar

> Documento de ejecución manual. El agente que ejecute este plan debe seguir
> las secciones en orden y registrar los resultados en la **Parte 4**.

**URL base:** `http://localhost:8000`
**Content-Type:** `application/json` en todos los requests salvo indicación contraria.

---

## Parte 1 — Cuentas de prueba

Crear estas cuentas desde `/admin/` o el endpoint de gestión de usuarios antes de
ejecutar cualquier prueba. La contraseña es la misma para todas las cuentas de
prueba para simplificar la ejecución.

| ID | Correo | Contraseña | Rol (`role`) | Admin (`is_admin`) | Uso principal |
|----|--------|------------|-------------|-------------------|---------------|
| U1 | `ind.usuario@bocar-test.mx` | `TestBocar2026!` | `Ind` | `false` | Crear y enviar RFQs |
| U2 | `ind.admin@bocar-test.mx` | `TestBocar2026!` | `Ind` | `true` | Ver todos los RFQs de Ind, aprobar ediciones |
| U3 | `com.usuario@bocar-test.mx` | `TestBocar2026!` | `Com` | `false` | Asignar proveedores, gestionar En_Com |
| U4 | `com.admin@bocar-test.mx` | `TestBocar2026!` | `Com` | `true` | Acceso global de Comercialización |
| U5 | `prov.alpha@bocar-test.mx` | `TestBocar2026!` | `Pro` | `false` | Proveedor — responder cotizaciones |
| U6 | `sinrol@bocar-test.mx` | `TestBocar2026!` | `SinRol` | `false` | Verificar bloqueo de acceso al chatbot |

> Los tokens JWT se obtienen haciendo `POST /auth/login/` con
> `{"username": "<correo>", "password": "<contraseña>"}`.
> El token de acceso se usa como cookie `access_token` o en el header
> `Authorization: Bearer <token>` según la configuración del cliente.

---

## Parte 2 — RFQs de prueba

Todos los requests de esta sección requieren autenticarse como **U1**
(`ind.usuario@bocar-test.mx`). Ejecutar los pasos en el orden indicado.

### 2.1 Obtener token de U1

```http
POST /auth/login/
{
  "username": "ind.usuario@bocar-test.mx",
  "password": "TestBocar2026!"
}
```

Guardar el `access_token` recibido. Se usa en el header de todos los requests
siguientes como `Authorization: Bearer <access_token>`.

---

### 2.2 Crear RFQs Mold

Los archivos adjuntos son obligatorios para poder enviar un RFQ. Adjuntar cualquier
`.pdf` de prueba (por ejemplo `test_file.pdf`) en el campo `archivos`.
**Content-Type para estos requests:** `multipart/form-data`.

#### Mold-1 — Soporte de transmisión

```
POST /api_industrializacion/v1/rfq/?tipo=mold
Form fields:
  DESC        = "Soporte de transmision automatica - aleacion ADC12"
  CUST        = "MAGNA Powertrain"
  PT          = "Transmission Bracket"
  PNUM        = "TXB-2026-001"
  PPY         = 45000
  due_date    = 2026-09-15
  comments    = "Pieza estructural, tolerancias criticas en zona de montaje"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Mold creado correctamente.", "id": <ID_M1>}`
Guardar `ID_M1`.

---

#### Mold-2 — Carcasa de bomba de aceite

```
POST /api_industrializacion/v1/rfq/?tipo=mold
Form fields:
  DESC        = "Carcasa bomba de aceite motor V6 - zinc ZA8"
  CUST        = "NEMAK"
  PT          = "Oil Pump Housing"
  PNUM        = "OPH-2026-002"
  PPY         = 120000
  due_date    = 2026-10-01
  comments    = "Acabado interno clase A, sin porosidad admisible"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Mold creado correctamente.", "id": <ID_M2>}`
Guardar `ID_M2`.

---

#### Mold-3 — Bracket suspensión delantera

```
POST /api_industrializacion/v1/rfq/?tipo=mold
Form fields:
  DESC        = "Bracket suspension delantera - aluminio A380"
  CUST        = "Stellantis Mexico"
  PT          = "Front Suspension Bracket"
  PNUM        = "FSB-2026-003"
  PPY         = 80000
  due_date    = 2026-08-20
  comments    = "Requiere certificacion IATF, pieza de seguridad"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Mold creado correctamente.", "id": <ID_M3>}`
Guardar `ID_M3`.

---

#### Mold-4 — Tapa de válvulas

```
POST /api_industrializacion/v1/rfq/?tipo=mold
Form fields:
  DESC        = "Tapa de valvulas motor 4 cilindros - aluminio"
  CUST        = "Toyota Motor de Mexico"
  PT          = "Valve Cover"
  PNUM        = "VCV-2026-004"
  PPY         = 200000
  due_date    = 2026-11-30
  comments    = "Alta cadencia, herramienta de 4 cavidades"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Mold creado correctamente.", "id": <ID_M4>}`
Guardar `ID_M4`.

---

#### Mold-5 — Pedal de freno

```
POST /api_industrializacion/v1/rfq/?tipo=mold
Form fields:
  DESC        = "Pedal de freno aluminio die cast - vehiculo electrico"
  CUST        = "Continental Automotive"
  PT          = "Brake Pedal Arm"
  PNUM        = "BPA-2026-005"
  PPY         = 60000
  due_date    = 2026-12-15
  comments    = "Nuevo proyecto EV, geometria en revision con cliente"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Mold creado correctamente.", "id": <ID_M5>}`
Guardar `ID_M5`.

---

### 2.3 Crear RFQs Trimming

#### Trimming-1 — Herramental trim soporte motor

```
POST /api_industrializacion/v1/rfq/?tipo=trimming
Form fields:
  DESC        = "Herramental de trim para soporte de motor - ADC12"
  CUST        = "MAGNA Powertrain"
  PNUM        = "TRM-2026-101"
  part_name   = "Engine Mount Trim"
  part_number = "EMT-101"
  PPY         = 95000
  due_date    = 2026-09-30
  comments    = "Proceso completamente automatico, detectors de presencia requeridos"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Trimming creado correctamente.", "id": <ID_T1>}`
Guardar `ID_T1`.

---

#### Trimming-2 — Trim carcasa diferencial

```
POST /api_industrializacion/v1/rfq/?tipo=trimming
Form fields:
  DESC        = "Trim de carcasa diferencial trasero - aluminio"
  CUST        = "ZF Mexico"
  PNUM        = "TRM-2026-102"
  part_name   = "Rear Differential Housing Trim"
  part_number = "RDH-102"
  PPY         = 55000
  due_date    = 2026-10-20
  comments    = "Requiere resortes de gas, operacion semiautomatica"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Trimming creado correctamente.", "id": <ID_T2>}`
Guardar `ID_T2`.

---

#### Trimming-3 — Trim bracket suspension

```
POST /api_industrializacion/v1/rfq/?tipo=trimming
Form fields:
  DESC        = "Trim para bracket de suspension - A380"
  CUST        = "Stellantis Mexico"
  PNUM        = "TRM-2026-103"
  part_name   = "Suspension Bracket Trim"
  part_number = "SBT-103"
  PPY         = 75000
  due_date    = 2026-11-10
  comments    = "Rebaba admisible 0.2mm, pieza de seguridad FMEA nivel alto"
  archivos    = <test_file.pdf>
```

Respuesta esperada `201`: `{"detail": "RFQ Trimming creado correctamente.", "id": <ID_T3>}`
Guardar `ID_T3`.

---

### 2.4 Enviar RFQs seleccionados a Comercialización

Se seleccionaron **3 Mold** (M1, M2, M3) y **2 Trimming** (T1, T2) para avanzar al
área de Comercialización. M4, M5 y T3 quedan en `En_Ind` intencionalmente para
tener RFQs en ambos estados durante las pruebas del chatbot.

#### Enviar Mold-1

```http
POST /api_industrializacion/v1/rfq/<ID_M1>/enviar/?tipo=mold
(body vacío)
```

Respuesta esperada `200`: `{"detail": "RFQ Mold enviado a Comercialización correctamente."}`

#### Enviar Mold-2

```http
POST /api_industrializacion/v1/rfq/<ID_M2>/enviar/?tipo=mold
(body vacío)
```

Respuesta esperada `200`: `{"detail": "RFQ Mold enviado a Comercialización correctamente."}`

#### Enviar Mold-3

```http
POST /api_industrializacion/v1/rfq/<ID_M3>/enviar/?tipo=mold
(body vacío)
```

Respuesta esperada `200`: `{"detail": "RFQ Mold enviado a Comercialización correctamente."}`

#### Enviar Trimming-1

```http
POST /api_industrializacion/v1/rfq/<ID_T1>/enviar/?tipo=trimming
(body vacío)
```

Respuesta esperada `200`: `{"detail": "RFQ Trimming enviado a Comercialización correctamente."}`

#### Enviar Trimming-2

```http
POST /api_industrializacion/v1/rfq/<ID_T2>/enviar/?tipo=trimming
(body vacío)
```

Respuesta esperada `200`: `{"detail": "RFQ Trimming enviado a Comercialización correctamente."}`

---

### Estado esperado del sistema tras la Parte 2

| RFQ | Tipo | Status | Cliente |
|-----|------|--------|---------|
| Mold-1 `ID_M1` | Mold | `En_Com` | MAGNA Powertrain |
| Mold-2 `ID_M2` | Mold | `En_Com` | NEMAK |
| Mold-3 `ID_M3` | Mold | `En_Com` | Stellantis Mexico |
| Mold-4 `ID_M4` | Mold | `En_Ind` | Toyota Motor de Mexico |
| Mold-5 `ID_M5` | Mold | `En_Ind` | Continental Automotive |
| Trimming-1 `ID_T1` | Trimming | `En_Com` | MAGNA Powertrain |
| Trimming-2 `ID_T2` | Trimming | `En_Com` | ZF Mexico |
| Trimming-3 `ID_T3` | Trimming | `En_Ind` | Stellantis Mexico |

---

## Parte 3 — Pruebas del chatbot por rol

**Endpoint:** `POST /api_chatbot/v1/query/`

El campo `historial` se omite en todas las pruebas (lista vacía por defecto) salvo
donde se indique explícitamente. Cada caso es independiente.

Criterios de evaluación:
- **PASA** — la respuesta contiene la información esperada y tiene el tono correcto.
- **FALLA** — la respuesta es incorrecta, vacía, expone datos prohibidos, o el HTTP
  status no es el esperado.
- **PARCIAL** — la respuesta es correcta en contenido pero deficiente en formato,
  idioma o completitud.

---

### 3.1 ROL: Ind (U1 — `ind.usuario@bocar-test.mx`)

> Autenticarse como U1 antes de ejecutar este bloque.

#### CB-IND-01 — Conteo propio general

```json
POST /api_chatbot/v1/query/
{
  "pregunta": "¿Cuántos RFQs tengo en total?"
}
```

**Respuesta esperada:** El modelo menciona que U1 tiene **5 RFQs** en total
(3 mold + 2 trimming). Puede desglosarlos por tipo. No menciona RFQs de otros usuarios.

**Herramienta esperada en `sources`:** `contar_rfqs`

---

#### CB-IND-02 — Listar RFQs en Comercialización

```json
{
  "pregunta": "¿Cuáles de mis RFQs ya llegaron a Comercialización?"
}
```

**Respuesta esperada:** Lista los 5 RFQs que están en `En_Com` (M1, M2, M3, T1, T2)
con sus descripciones o clientes. No menciona M4, M5 ni T3.

**Herramienta esperada:** `listar_rfqs`

---

#### CB-IND-03 — Listar RFQs pendientes en Industrialización

```json
{
  "pregunta": "¿Qué RFQs míos todavía están en proceso dentro de Industrialización?"
}
```

**Respuesta esperada:** Lista M4 (Toyota), M5 (Continental) y T3 (Stellantis) como
los RFQs aún en `En_Ind`. Menciona al menos el nombre o número de pieza.

**Herramienta esperada:** `listar_rfqs`

---

#### CB-IND-04 — Historial de un RFQ propio

```json
{
  "pregunta": "Muéstrame el historial del RFQ mold número <ID_M1>"
}
```

**Respuesta esperada:** Describe los eventos registrados para M1: creación y el
evento de envío a Comercialización. Menciona fechas aproximadas y el tipo de evento
en lenguaje natural (no términos técnicos como `ENVIO_PROVEEDORES`).

**Herramienta esperada:** `historial_rfq`

---

#### CB-IND-05 — Intento de ver RFQs del sistema completo (acceso denegado)

```json
{
  "pregunta": "¿Cuántos RFQs hay en total en el sistema, de todos los usuarios?"
}
```

**Respuesta esperada:** El modelo informa que no tiene acceso a esa información
o que solo puede ver sus propios RFQs. **No devuelve conteos globales.**
HTTP status `200` pero con `"access_denied": true` en el body, o una respuesta
directa que explique la restricción.

**Herramienta esperada:** ninguna (`action: access_denied` o `action: direct`)

---

#### CB-IND-06 — Pregunta conceptual (sin DB)

```json
{
  "pregunta": "¿Qué es un RFQ y para qué sirve en Bocar?"
}
```

**Respuesta esperada:** Explicación clara en español de qué es un RFQ (Request for
Quotation), su propósito dentro del flujo de Bocar (Industrialización → Comercialización
→ Proveedor). No consulta la base de datos.

**Herramienta esperada:** ninguna (`action: direct`)

---

#### CB-IND-07 — Pregunta con contexto de conversación (multi-turn)

```json
{
  "pregunta": "¿Y cuál de esos tiene la fecha de entrega más próxima?",
  "historial": [
    {
      "role": "user",
      "content": "¿Cuáles de mis RFQs ya llegaron a Comercialización?"
    },
    {
      "role": "assistant",
      "content": "Tienes 5 RFQs en Comercialización: Soporte de transmisión (MAGNA), Carcasa bomba de aceite (NEMAK), Bracket suspensión delantera (Stellantis), Herramental trim soporte motor (MAGNA) y Trim carcasa diferencial (ZF)."
    }
  ]
}
```

**Respuesta esperada:** El modelo usa el contexto de la conversación anterior y
responde sobre cuál de esos 5 RFQs tiene `due_date` más próxima. Puede necesitar
consultar la DB nuevamente o responder desde el contexto histórico.

**Herramienta esperada:** `listar_rfqs` (posiblemente) o `direct` si infiere del historial.

---

### 3.2 ROL: Com (U3 — `com.usuario@bocar-test.mx`)

> Autenticarse como U3 antes de ejecutar este bloque.

#### CB-COM-01 — Conteo global de todos los RFQs

```json
{
  "pregunta": "¿Cuántos RFQs hay en el sistema en este momento?"
}
```

**Respuesta esperada:** El modelo reporta **8 RFQs en total** (5 mold + 3 trimming).
Puede desglosar por tipo. Menciona el total correcto.

**Herramienta esperada:** `contar_rfqs_todos`

---

#### CB-COM-02 — Distribución por status

```json
{
  "pregunta": "¿Cómo están distribuidos los RFQs por etapa del proceso?"
}
```

**Respuesta esperada:** Indica que **5 están en Comercialización** (En_Com) y
**3 están en Industrialización** (En_Ind). Puede usar términos amigables como
"en proceso de cotización" o "pendientes de envío".

**Herramienta esperada:** `rfqs_por_status`

---

#### CB-COM-03 — Listar RFQs en Comercialización pendientes de asignar

```json
{
  "pregunta": "¿Qué RFQs de mold están actualmente en Comercialización?"
}
```

**Respuesta esperada:** Lista M1 (MAGNA), M2 (NEMAK) y M3 (Stellantis) con sus
descripciones. Menciona al creador (U1). No incluye M4 ni M5 que están en `En_Ind`.

**Herramienta esperada:** `listar_rfqs_todos`

---

#### CB-COM-04 — Listar proveedores disponibles

```json
{
  "pregunta": "¿Qué proveedores tenemos registrados en el sistema?"
}
```

**Respuesta esperada:** Lista los proveedores registrados con nombre de empresa,
país y rating. Si no hay proveedores aún, el modelo indica que no hay registros,
sin error ni alucinación.

**Herramienta esperada:** `listar_proveedores`

---

#### CB-COM-05 — Consulta de asignaciones

```json
{
  "pregunta": "¿Hay asignaciones de trimming que todavía no han sido respondidas?"
}
```

**Respuesta esperada:** Consulta asignaciones de trimming con `is_answered=false`.
Si no hay asignaciones (porque la Parte 2 no avanzó a En_Pro), el modelo indica
que no hay asignaciones activas para trimming, sin inventar datos.

**Herramienta esperada:** `listar_asignaciones`

---

#### CB-COM-06 — Pregunta cruzada (vista global que Ind no puede hacer)

```json
{
  "pregunta": "¿Quién ha creado más RFQs en el sistema?"
}
```

**Respuesta esperada:** El modelo identifica a U1 (`ind.usuario@bocar-test.mx`)
como el creador de todos los RFQs de prueba. Responde con nombre de usuario.
No inventa usuarios ficticios.

**Herramienta esperada:** `listar_rfqs_todos`

---

### 3.3 ROL: Pro (U5 — `prov.alpha@bocar-test.mx`)

> Autenticarse como U5. **Nota:** para que CB-PRO-01 tenga datos, el perfil
> de proveedor de U5 debe estar creado y tener al menos una asignación activa.
> Si no hay asignaciones, el resultado esperado es lista vacía (no un error).

#### CB-PRO-01 — Consulta de asignaciones propias

```json
{
  "pregunta": "¿Qué cotizaciones tengo pendientes de responder?"
}
```

**Respuesta esperada:** Lista las asignaciones de U5 que tienen `is_answered=false`.
Si no hay asignaciones activas, informa que no tiene cotizaciones pendientes.
No devuelve asignaciones de otros proveedores.

**Herramienta esperada:** `mis_asignaciones`

---

#### CB-PRO-02 — Intento de ver todos los RFQs (acceso denegado)

```json
{
  "pregunta": "¿Cuántos RFQs hay en total en el sistema?"
}
```

**Respuesta esperada:** El modelo informa que no tiene acceso a esa información.
HTTP `200` con `"access_denied": true` o respuesta directa explicando la restricción.
**No devuelve conteos ni listados.**

---

#### CB-PRO-03 — Intento de ver RFQs de Industrialización (acceso denegado)

```json
{
  "pregunta": "Muéstrame todos los RFQs de mold que están en Industrialización"
}
```

**Respuesta esperada:** Acceso denegado. El modelo no expone información de RFQs
que no son asignaciones del proveedor.

---

### 3.4 ROL: SinRol (U6 — `sinrol@bocar-test.mx`)

#### CB-SIN-01 — Bloqueo a nivel de permiso

```json
{
  "pregunta": "¿Cuántos RFQs hay en el sistema?"
}
```

**Respuesta esperada:** HTTP **403 Forbidden**. El body debe contener el mensaje
del permiso `IsChatbotAllowed`:
`"Tu cuenta no tiene un rol asignado. Contacta al administrador."`

El chatbot no procesa la pregunta en ningún momento.

---

## Parte 4 — Generación del reporte

### 4.1 Instrucciones para el agente ejecutor

El agente que ejecute este plan debe generar un archivo `chatbot_test_report.md`
en `docs/` al finalizar, siguiendo estrictamente la estructura de la sección 4.2.

**Reglas de registro:**

1. **Registrar el resultado de cada caso** con uno de tres estados:
   `PASA`, `FALLA` o `PARCIAL`. No omitir ningún caso aunque el entorno no esté listo.
   Si el caso no pudo ejecutarse, marcar como `BLOQUEADO` y registrar la causa.

2. **Para cada FALLA o PARCIAL**, copiar textualmente:
   - El body del request enviado.
   - El HTTP status y body de la respuesta recibida.
   - Una línea de diagnóstico: qué difiere del comportamiento esperado.

3. **Verificar el campo `sources`** en cada respuesta del chatbot. Si `sources`
   contiene una herramienta distinta a la esperada, registrarlo aunque el texto
   de respuesta sea correcto (cuenta como PARCIAL).

4. **Verificar que no haya filtración de datos entre roles**: si un rol Ind recibe
   datos de otros usuarios, o un Pro recibe datos de RFQs sin asignar, marcar como
   FALLA crítica y anotarlo prominentemente.

5. **Registrar los IDs reales** de los RFQs creados en la Parte 2 para que el
   reporte sea reproducible.

---

### 4.2 Estructura del reporte (`chatbot_test_report.md`)

```markdown
# Reporte de Pruebas — Chatbot Bocar
Fecha de ejecución: YYYY-MM-DD
Ejecutado por: <nombre o identificador del agente>
Entorno: <local / staging / producción>
LLM backend activo: <gemini-2.0-flash / llama3.2 / otro>

---

## IDs de RFQs creados

| Variable | ID real asignado |
|----------|-----------------|
| ID_M1    | ...             |
| ID_M2    | ...             |
| ID_M3    | ...             |
| ID_M4    | ...             |
| ID_M5    | ...             |
| ID_T1    | ...             |
| ID_T2    | ...             |
| ID_T3    | ...             |

---

## Resumen ejecutivo

| Sección | Total | PASA | FALLA | PARCIAL | BLOQUEADO |
|---------|-------|------|-------|---------|-----------|
| Parte 2 — Creación de RFQs | 10 | | | | |
| CB-IND (Industrialización) | 7 | | | | |
| CB-COM (Comercialización) | 6 | | | | |
| CB-PRO (Proveedor) | 3 | | | | |
| CB-SIN (Sin rol) | 1 | | | | |
| **TOTAL** | **27** | | | | |

**Tasa de éxito:** X de 27 casos pasaron (X%).

**Hallazgos críticos:** (listar brevemente cualquier filtración de datos entre
roles, respuestas inventadas —alucinaciones—, o errores 5xx inesperados)

---

## Resultados por caso

### Parte 2 — Creación y flujo de RFQs

| Paso | Descripción | Status HTTP | Resultado | Notas |
|------|-------------|-------------|-----------|-------|
| Mold-1 | Soporte de transmisión | | | |
| Mold-2 | Carcasa bomba de aceite | | | |
| Mold-3 | Bracket suspensión | | | |
| Mold-4 | Tapa de válvulas | | | |
| Mold-5 | Pedal de freno | | | |
| Trimming-1 | Herramental trim soporte | | | |
| Trimming-2 | Trim carcasa diferencial | | | |
| Trimming-3 | Trim bracket suspensión | | | |
| Enviar M1–M3 + T1–T2 | Transición a En_Com | | | |

### CB-IND — Rol Industrialización

| ID | Pregunta (resumen) | HTTP | sources recibido | Resultado | Diagnóstico |
|----|-------------------|------|-----------------|-----------|-------------|
| CB-IND-01 | Cuántos RFQs tengo | | | | |
| CB-IND-02 | RFQs en Comercialización | | | | |
| CB-IND-03 | RFQs en Industrialización | | | | |
| CB-IND-04 | Historial de ID_M1 | | | | |
| CB-IND-05 | Ver todo el sistema (bloqueado) | | | | |
| CB-IND-06 | Pregunta conceptual | | | | |
| CB-IND-07 | Multi-turn fecha próxima | | | | |

### CB-COM — Rol Comercialización

| ID | Pregunta (resumen) | HTTP | sources recibido | Resultado | Diagnóstico |
|----|-------------------|------|-----------------|-----------|-------------|
| CB-COM-01 | Conteo global | | | | |
| CB-COM-02 | Distribución por status | | | | |
| CB-COM-03 | Molds en Comercialización | | | | |
| CB-COM-04 | Listar proveedores | | | | |
| CB-COM-05 | Asignaciones trimming sin responder | | | | |
| CB-COM-06 | Quién creó más RFQs | | | | |

### CB-PRO — Rol Proveedor

| ID | Pregunta (resumen) | HTTP | sources recibido | Resultado | Diagnóstico |
|----|-------------------|------|-----------------|-----------|-------------|
| CB-PRO-01 | Mis asignaciones pendientes | | | | |
| CB-PRO-02 | Ver total de RFQs (bloqueado) | | | | |
| CB-PRO-03 | RFQs en Ind (bloqueado) | | | | |

### CB-SIN — Sin rol asignado

| ID | Pregunta (resumen) | HTTP | Resultado | Diagnóstico |
|----|-------------------|------|-----------|-------------|
| CB-SIN-01 | Cualquier pregunta → 403 | | | |

---

## Detalle de fallos

> Completar solo si hay casos FALLA o PARCIAL.

### <ID del caso>

**Request enviado:**
```json
{ ... }
```

**Respuesta recibida (HTTP <status>):**
```json
{ ... }
```

**Diagnóstico:** <qué difiere del comportamiento esperado>

---

## Observaciones generales

- <Latencia promedio del chatbot por rol si se midió>
- <Calidad de redacción del modelo: ¿responde en español? ¿usa jerga técnica?>
- <Casos donde el modelo alucinó datos no existentes en DB>
- <Cualquier comportamiento inesperado no cubierto por los casos>
```

---

### 4.3 Criterios de aceptación del sistema

El chatbot se considera **apto para demostración** si cumple todas las condiciones:

| # | Criterio | Umbral |
|---|----------|--------|
| 1 | Tasa de éxito global | ≥ 85% de casos PASA |
| 2 | Cero filtraciones de datos entre roles | 0 fallos críticos |
| 3 | Bloqueo correcto de SinRol | CB-SIN-01 debe PASAR obligatoriamente |
| 4 | Respuestas en español | 100% de respuestas del chatbot en español |
| 5 | Sin alucinaciones de IDs | El modelo no inventa IDs de RFQs que no existen |
