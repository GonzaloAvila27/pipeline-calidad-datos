# Reporte de Calidad de Datos — Estaciones Meteorológicas Misiones

Este reporte presenta el diagnóstico cuantitativo de las dimensiones de calidad analizadas sobre el dataset `datos/estaciones_meteo.csv`.

| Dimensión | Métrica calculada | Valor | Observaciones |
| :--- | :--- | :--- | :--- |
| **Completitud** | Tasa de completitud mínima | 82.21% | La columna más afectada es `humedad`. |
| **Unicidad** | Tasa de unicidad (filas completas) | 100.0% | Se detectaron un total de 0 filas duplicadas. |
| **Validez (temp.)** | Tasa de validez en `temperatura` [-40, 60] | 98.93% | Existen 48 registros fuera del rango físico establecido. |
| **Validez (hum.)** | Tasa de validez en `humedad` [0, 100] | 97.83% | Existen 90 registros con porcentajes de humedad inválidos. |
| **Consistencia** | Inconsistencia en `estacion` | 19 vs 8 | Hay inconsistencias. Existen variantes por tipeo, espacios o mayúsculas. |
| **Actualidad** | Rango de fechas del dataset | 01/01/1990 — 30/06/2025 | Monitorear si el rango cubre el período esperado o incluye años fuera de contexto. |

---
*Reporte generado automáticamente mediante el módulo `src/diagnostico.py`.*


