# Pipeline de Calidad de Datos — Estaciones Meteorológicas de Misiones

Trabajo Práctico N° 2 de **Gestión de Calidad y Auditoría (Módulo 2)**: dimensiones de calidad, data profiling, validación con Great Expectations y un pipeline ETL con **patrón Gate**.

> ## 🎯 En este proyecto, `False` es el `True`
>
> El pipeline devuelve `"exito": false`, y **ese es el resultado correcto**.
>
> El dataset `datos/estaciones_meteo.csv` trae **errores inducidos a propósito** en todas las dimensiones de calidad. Un Gate de calidad bien hecho tiene que **detectarlos y frenar el pipeline** antes de que los datos sucios lleguen a transformación y carga.
>
> - Si el pipeline diera `exito: True` con este dataset, la compuerta estaría **rota**: dejaría pasar datos inválidos.
> - Con `exito: False`, la compuerta **se cerró**, no se escribió `meteo_limpio.csv` y el pipeline devolvió la lista exacta de reglas que fallaron.
>
> **Que la validación falle es la prueba de que el control de calidad funciona.**

---

## Arquitectura: patrón Gate

```
[ 1. Extracción ]  pd.read_csv(datos/estaciones_meteo.csv)
        │
        ▼
[ 2. Validación ]  ◄── COMPUERTA: suite de 10 Expectations (Great Expectations)
        │
        ├── ❌ Falla  ──► 🛑 Pipeline detenido
        │                  └─► return {"exito": False, "expectations_fallidas": [...]}
        │
        └── ✅ Pasa
                │
                ▼
[ 3. Transformación ]  estaciones a título · drop_duplicates · centinelas 999/-999 → None
        │
        ▼
[ 4. Carga ]  datos/meteo_limpio.csv
        └─► return {"exito": True, "filas_originales", "filas_limpias", "filas_eliminadas"}
```

---

## Resultado de la ejecución

La suite evalúa **10 expectations**: **4 pasan y 6 fallan (40 % de éxito)**. Por eso el Gate se cierra.

| # | Dimensión | Expectation | Resultado | Por qué |
|---|---|---|---|---|
| 1 | Estructura | `expect_table_columns_to_match_set` | ❌ | Aparece una columna no declarada: `viento_kmh` |
| 2 | Completitud | `expect_column_values_to_not_be_null` (`fecha`) | ✅ | |
| 3 | Completitud | `expect_column_values_to_not_be_null` (`estacion`) | ✅ | |
| 4 | Validez | `expect_column_values_to_be_between` (`temperatura`, -40 a 60) | ❌ | 48 valores fuera de rango (incluye los centinelas 999/-999) |
| 5 | Validez | `expect_column_values_to_be_between` (`humedad`, 0 a 100) | ❌ | 90 valores fuera de rango |
| 6 | Consistencia | `expect_column_values_to_be_in_set` (`estacion`) | ❌ | 19 variantes crudas para 8 estaciones (`posadas`, `Posadas `, `IGUAZU`, `OberÃ¡`, etc.) |
| 7 | Unicidad | `expect_compound_columns_to_be_unique` (`fecha`, `estacion`) | ❌ | Hay pares fecha + estación repetidos |
| 8 | Extra: formato | `expect_column_values_to_match_regex` (`fecha`, `DD/MM/AAAA`) | ❌ | Hay fechas con otro formato |
| 9 | Extra: rango | `expect_column_values_to_be_between` (`presion`, 900 a 1100 hPa) | ✅ | |
| 10 | Extra: tipo | `expect_column_values_to_be_in_type_list` (`id`, entero) | ✅ | |

Salida del pipeline (resumida):

```json
{
  "exito": false,
  "expectations_fallidas": [
    { "expectation": "expect_table_columns_to_match_set", "kwargs": { "column_set": ["id", "fecha", "..."] } },
    { "expectation": "expect_compound_columns_to_be_unique", "kwargs": { "column_list": ["fecha", "estacion"] } },
    { "expectation": "expect_column_values_to_match_regex", "kwargs": { "column": "fecha", "regex": "^\\d{2}/\\d{2}/\\d{4}$" } },
    { "expectation": "expect_column_values_to_be_in_set", "kwargs": { "column": "estacion", "value_set": ["Posadas", "..."] } },
    { "expectation": "expect_column_values_to_be_between", "kwargs": { "column": "temperatura", "min_value": -40.0, "max_value": 60.0 } },
    { "expectation": "expect_column_values_to_be_between", "kwargs": { "column": "humedad", "min_value": 0.0, "max_value": 100.0 } }
  ]
}
```

El detalle completo de la validación está en [`reportes/resultado_gx.json`](reportes/resultado_gx.json).

---

## Diagnóstico de calidad

Las métricas salen de `src/diagnostico.py` sobre las 5 047 filas del dataset. El detalle está en [`REPORTE_CALIDAD.md`](REPORTE_CALIDAD.md).

| Dimensión | Métrica | Valor | Observación |
|---|---|---|---|
| Completitud | Tasa mínima | 82.21 % | La columna más afectada es `humedad` |
| Unicidad | Filas completas únicas | 100 % | 0 duplicados exactos (el `id` las hace distintas) |
| Validez (temp.) | `temperatura` en [-40, 60] | 98.93 % | 48 valores fuera de rango |
| Validez (hum.) | `humedad` en [0, 100] | 97.83 % | 90 valores fuera de rango |
| Consistencia | Valores de `estacion` | 19 crudos vs 8 normalizados | Diferencias de tipeo, mayúsculas, espacios y encoding |
| Actualidad | Rango de fechas | 01/01/1990 — 30/06/2025 | Hay registros muy antiguos, fuera de contexto |

**Hallazgos del profiling** ([`reportes/profiling_meteo.html`](reportes/profiling_meteo.html)):

- Los valores centinela (999 / -999) **no** se marcan como error. Se toman como datos reales y distorsionan medias, máximos y correlaciones.
- Los nulos de `humedad` y `presion` están fuertemente correlacionados, lo que sugiere fallas simultáneas de sensores.

---

## Estructura del proyecto

```
pipeline-calidad-datos/
├── datos/
│   └── estaciones_meteo.csv     # Dataset con errores inducidos
├── src/
│   ├── diagnostico.py           # Funciones de diagnóstico + genera REPORTE_CALIDAD.md
│   ├── profiling.py             # Reporte YData Profiling → reportes/profiling_meteo.html
│   ├── validacion_gx.py         # crear_suite_meteo(): suite de 10 Expectations → reportes/resultado_gx.json
│   └── pipeline.py              # ejecutar_pipeline(): ETL con patrón Gate
├── tests/                       # Plantillas de tests (pytest)
├── reportes/                    # Salidas generadas
├── DICCIONARIO_DATOS.md
├── REPORTE_CALIDAD.md
└── TP2.MD                       # Consigna + respuestas teóricas
```

---

## Cómo ejecutarlo

Requisitos: Python 3.10 o superior.

```bash
python -m venv env
```

```bash
pip install pandas pytest ydata-profiling great_expectations
```

Ejecutá los scripts desde la raíz del repo, porque usan rutas relativas:

```bash
python src/diagnostico.py
```

```bash
python src/profiling.py
```

```bash
python src/validacion_gx.py
```

```bash
python src/pipeline.py
```

El último comando debería imprimir `"exito": false` con las 6 expectations fallidas. **Ese es el comportamiento esperado.**

---

## ¿Cuándo daría `exito: True`?

Solo con un dataset que cumpla el contrato: columnas exactas, estaciones normalizadas, sin pares fecha + estación duplicados, fechas en `DD/MM/AAAA` y valores físicamente válidos. En ese caso el pipeline transforma los datos, guarda `datos/meteo_limpio.csv` y devuelve el conteo de filas originales, limpias y eliminadas.

---

## Pendientes

- [ ] Completar `DICCIONARIO_DATOS.md` (todavía es la plantilla).
- [ ] Escribir los tests de `tests/test_diagnostico.py` y `tests/test_pipeline.py` (bonus). Uno clave: verificar que con el dataset crudo `ejecutar_pipeline()` devuelva `exito == False`.
- [ ] Decidir si `viento_kmh` se agrega al contrato o se descarta en la extracción.
