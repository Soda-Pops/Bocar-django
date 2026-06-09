# Evaluación de Proveedores

La app `Evaluaciones/` permite a Compras calificar la entrega de cada proveedor al cerrar
una asignación (Mold o Trimming). El score resultante se acumula en `Proveedor.rating`
como promedio histórico de todas sus evaluaciones.

---

## Métricas automáticas

Derivadas de datos ya existentes en el sistema, sin captura manual:

| Métrica | Fuente |
|---------|--------|
| `fue_puntual` | `Asignacion.due_date` vs `Cost_Breakdown.last_change` cuando `status='submitted'` |
| `dias_diferencia` | Días entre la fecha de envío y el `due_date` (negativo = antes, positivo = tarde) |
| `solicito_extension` | Existencia de `SolicitudExtension` para la asignación |
| `cotizacion_enviada` | `Cost_Breakdown.status == 'submitted'` |

---

## Calificación manual (Compras, escala 1–5)

| Campo | Descripción |
|-------|-------------|
| `calidad_cotizacion` | Qué tan completo y detallado fue el `Cost_Breakdown` enviado |
| `comunicacion` | Interacción del proveedor durante el proceso |
| `comentarios` | Texto libre opcional |

---

## Fórmula de score (escala 0–5)

| Criterio | Peso | Cálculo |
|----------|------|---------|
| Puntualidad | 40 % | 5 pts si puntual; si tardío: `max(0, 5 - dias_diferencia × 0.5)`; 0 si no envió |
| Calidad de cotización | 30 % | Valor directo (1–5) |
| Comunicación | 20 % | Valor directo (1–5) |
| Sin solicitudes de extensión | 10 % | 5 pts si no solicitó extensión; 0 si solicitó |

El `Proveedor.rating` se recalcula automáticamente como promedio de todos sus scores al guardar cada evaluación.

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api_evaluaciones/v1/crear/?tipo=mold\|trimming` | Registrar evaluación de una asignación |
| `GET` | `/api_evaluaciones/v1/proveedor/<id>/` | Historial completo + resumen estadístico del proveedor |

Ambos endpoints requieren `role='Com'`.

### Body — POST `/crear/`

```json
{
  "asignacion_id": 12,
  "calidad_cotizacion": 4,
  "comunicacion": 3,
  "comentarios": "Texto opcional"
}
```

### Respuesta — POST `/crear/`

```json
{
  "detail": "Evaluación registrada correctamente.",
  "score": 3.75,
  "nuevo_rating_proveedor": 4.10
}
```

### Respuesta — GET `/proveedor/<id>/`

```json
{
  "proveedor_id": 7,
  "company_name": "Proveedor S.A.",
  "rating_actual": 4.10,
  "total_evaluaciones": 5,
  "pct_puntual": 80.0,
  "pct_sin_extension": 100.0,
  "pct_cotizacion_enviada": 100.0,
  "promedio_calidad": 4.2,
  "promedio_comunicacion": 3.8,
  "evaluaciones": [ ... ]
}
```

---

## Restricciones

- Solo se puede evaluar **una vez por asignación** (`unique_together` en `asignacion_tipo` + `asignacion_id`).
- Solo usuarios con `role='Com'` pueden crear o consultar evaluaciones.
- Al crear una evaluación se registra el evento `EVALUACION_PROVEEDOR` en `RFQHistorial`.
