# Trabajo Práctico N° 2 — Dimensiones de Calidad, Profiling y Validación de Datos

## Gestión de Calidad y Auditoría — Módulo 2

**Fecha de entrega:** Clase 7  
**Modalidad:** Individual o en parejas  
**Formato de entrega:** Repositorio Git (GitHub/GitLab) o carpeta comprimida con todos los archivos.

---

## Objetivos del TP

- Identificar y medir las **6 dimensiones de calidad de datos** sobre un dataset real.
- Aplicar **Data Profiling** automatizado con YData Profiling.
- Definir y ejecutar **validaciones** usando Great Expectations.
- Implementar un **pipeline con patrón Gate** que se detenga ante datos inválidos.
- Construir un **diccionario de datos** como documentación del dataset.

---

## Requisitos previos

- Python 3.10 o superior
- Dependencias:

```bash
pip install pandas pytest ydata-profiling great_expectations
```

### Estructura esperada del proyecto:

```
tp2/
├── datos/
│   └── estaciones_meteo.csv           # Dataset provisto (con errores inducidos)
├── src/
│   ├── __init__.py
│   ├── diagnostico.py                 # Funciones de diagnóstico de calidad
│   ├── profiling.py                   # Script de generación de profiling
│   ├── validacion_gx.py              # Suite de Great Expectations
│   └── pipeline.py                    # Pipeline ETL con patrón Gate
├── tests/
│   ├── __init__.py
│   ├── test_diagnostico.py            # Tests para diagnóstico
│   └── test_pipeline.py              # Tests para el pipeline
├── reportes/                          # Carpeta para reportes generados
│   └── .gitkeep
├── DICCIONARIO_DATOS.md               # Diccionario de datos del dataset
└── README.md
```

---

## Parte 1 — Preguntas Teóricas (20 puntos)

### Pregunta 1 (5 puntos)
Para cada una de las **6 dimensiones de calidad de datos**, dar un ejemplo **propio** (no del material de clase) de un problema concreto que podría ocurrir en un dataset de registros de alumnos de una universidad. Completar la tabla:

| Dimensión | Problema concreto en datos universitarios |
|---|---|
| Exactitud | |
| Completitud | |
| Consistencia | |
| Validez | |
| Unicidad | |
| Actualidad | |

### Pregunta 2 (5 puntos)
Explicar qué es un **Data Contract** (contrato de datos). ¿Quién lo define? ¿Qué elementos debe contener? ¿Por qué es importante en un equipo donde un Data Engineer produce los datos y un Data Scientist los consume?

### Pregunta 3 (5 puntos)
¿Cuál es la diferencia entre un **profiling** de datos y una **validación** con Great Expectations? ¿Se reemplazan entre sí o se complementan? Justificar con un ejemplo.

### Pregunta 4 (5 puntos)
Explicar el **patrón Gate** en un pipeline de datos. Dibujar (puede ser ASCII o diagrama simple) un pipeline de 4 etapas donde la validación actúe como compuerta. ¿Qué debería suceder cuando la validación falla? Mencionar al menos 2 acciones concretas que el sistema debería tomar.

---

## Parte 2 — Diagnóstico de Calidad (25 puntos)

Se provee el dataset `datos/estaciones_meteo.csv` con registros meteorológicos de estaciones de Misiones, Argentina. El dataset contiene **errores inducidos intencionalmente** en todas las dimensiones de calidad.

### Ejercicio 1 — Funciones de diagnóstico (15 puntos)

Implementar en `src/diagnostico.py` las siguientes funciones:

#### `calcular_completitud(df: pd.DataFrame) -> pd.Series`
Recibe un DataFrame y retorna una Serie de Pandas con la **tasa de completitud** (porcentaje de valores no nulos) para cada columna, redondeada a 2 decimales.

#### `detectar_duplicados(df: pd.DataFrame, subset: list[str] | None = None) -> dict`
Retorna un diccionario con:
- `"total_filas"`: cantidad total de filas.
- `"duplicados"`: cantidad de filas duplicadas (según `subset` o completas si `subset=None`).
- `"tasa_unicidad"`: porcentaje de unicidad redondeado a 2 decimales.

#### `detectar_outliers_rango(df: pd.DataFrame, columna: str, minimo: float, maximo: float) -> dict`
Detecta valores fuera de un rango dado. Retorna:
- `"total"`: total de valores no nulos en la columna.
- `"fuera_rango"`: cantidad de valores < mínimo o > máximo.
- `"tasa_validez"`: porcentaje de valores dentro del rango, redondeado a 2 decimales.

#### `detectar_inconsistencias_categoricas(df: pd.DataFrame, columna: str) -> dict`
Detecta valores que representan la misma categoría pero escritos distinto (normaliza a minúsculas y sin espacios extra). Retorna:
- `"valores_crudos"`: cantidad de valores únicos originales.
- `"valores_normalizados"`: cantidad de valores únicos normalizados.
- `"hay_inconsistencia"`: booleano (`True` si crudos > normalizados).

### Ejercicio 2 — Reporte de calidad (10 puntos)

Usando las funciones del Ejercicio 1, ejecutar un **diagnóstico completo** del dataset y completar la siguiente tabla en un archivo `REPORTE_CALIDAD.md`:

| Dimensión | Métrica calculada | Valor | Observaciones |
|---|---|---|---|
| Completitud | Tasa de completitud mínima | % | ¿Cuál es la columna más afectada? |
| Unicidad | Tasa de unicidad (filas completas) | % | ¿Cuántos duplicados hay? |
| Validez (temp.) | Tasa de validez en `temperatura` [-40, 60] | % | ¿Cuántos fuera de rango? |
| Validez (hum.) | Tasa de validez en `humedad` [0, 100] | % | ¿Cuántos fuera de rango? |
| Consistencia | Inconsistencia en `estacion` | crudos vs norm. | ¿Cuántas variantes hay? |
| Actualidad | Rango de fechas del dataset | min — max | ¿Hay datos muy antiguos? |

---

## Parte 3 — Data Profiling con YData Profiling (15 puntos)

### Ejercicio 3 — Generar y analizar el profiling

Implementar en `src/profiling.py` un script que:

1. Cargue el dataset `datos/estaciones_meteo.csv`.
2. Genere un reporte de profiling con `ProfileReport`.
3. Guarde el reporte como `reportes/profiling_meteo.html`.

Luego, abrir el reporte HTML y responder en el `REPORTE_CALIDAD.md`:

1. ¿Cuántas **alertas** genera el reporte? Listar las 5 más relevantes.
2. ¿El profiling detecta los **valores centinela** (999, -999) como outliers?
3. ¿Qué **patrón de nulos** se observa? ¿Hay columnas con nulos correlacionados?
4. ¿Cuántos **duplicados exactos** reporta?
5. Según el reporte, ¿qué par de variables numéricas tiene la **correlación más alta**?

---

## Parte 4 — Validación con Great Expectations (25 puntos)

### Ejercicio 4 — Definir una suite de Expectations (15 puntos)

En `src/validacion_gx.py`, crear una función `crear_suite_meteo()` que defina una suite de **al menos 10 Expectations** cubriendo:

| Dimensión | Expectations mínimas |
|---|---|
| Estructura | Verificar que existan las columnas obligatorias |
| Completitud | `fecha` y `estacion` sin nulos |
| Validez | `temperatura` entre -40 y 60, `humedad` entre 0 y 100 |
| Consistencia | `estacion` dentro de un conjunto de valores válidos |
| Unicidad | Combinación `(fecha, estacion)` única |
| Otros | Al menos 2 Expectations adicionales a elección del alumno |

La función debe retornar el resultado de la validación.

### Ejercicio 5 — Pipeline con patrón Gate (10 puntos)

En `src/pipeline.py`, implementar una función `ejecutar_pipeline(ruta_csv: str) -> dict` que:

1. **Extraiga** los datos del CSV.
2. **Valide** con la suite de GX creada en el ejercicio anterior.
3. Si la validación **falla**, retorne un diccionario con `"exito": False` y la lista de expectations que fallaron.
4. Si la validación **pasa**, ejecute las transformaciones básicas:
   - Normalizar nombres de estaciones a título (ej. "Posadas").
   - Eliminar duplicados.
   - Reemplazar valores centinela (999, -999) por `None`.
5. Guarde el DataFrame limpio en `datos/meteo_limpio.csv`.
6. Retorne un diccionario con `"exito": True`, `"filas_originales"`, `"filas_limpias"` y `"filas_eliminadas"`.

---

## Parte 5 — Diccionario de Datos (15 puntos)

### Ejercicio 6 — Crear el diccionario

Redactar el archivo `DICCIONARIO_DATOS.md` para el dataset `estaciones_meteo.csv`. Debe incluir, para **cada columna**:

| Campo | Descripción |
|---|---|
| **Nombre** | Nombre de la columna |
| **Descripción** | Qué representa |
| **Tipo de dato** | int, float, str, etc. |
| **Unidad** | °C, %, hPa, mm, km/h, etc. |
| **Rango válido** | Valores aceptables |
| **Nulos permitidos** | Sí / No |
| **Regla de validez** | Formato, restricciones |
| **Fuente** | Origen del dato |
| **Notas** | Observaciones (valores centinela, etc.) |

---

## Criterios de Evaluación

| Criterio | Puntos |
|---|---|
| **Parte 1:** Respuestas teóricas completas y fundamentadas | 20 |
| **Parte 2:** Funciones de diagnóstico + reporte de calidad | 25 |
| **Parte 3:** Profiling generado + análisis del reporte | 15 |
| **Parte 4:** Suite de GX + Pipeline con patrón Gate | 25 |
| **Parte 5:** Diccionario de datos completo | 15 |
| **Total** | **100** |

### Bonus (hasta 10 puntos extra):
- Escribir **tests con `pytest`** para las funciones de diagnóstico y pipeline.
- Usar `mostly` en GX para definir umbrales de tolerancia justificados.
- Generar un **reporte de comparación** entre el dataset original y el limpio usando YData Profiling.
- Agregar una función que genere un **resumen ejecutivo** en texto de la validación.

---

## Entrega

1. Todos los archivos organizados en la estructura indicada.
2. `REPORTE_CALIDAD.md` con todas las respuestas del análisis.
3. `DICCIONARIO_DATOS.md` completo.
4. Reporte HTML de profiling en `reportes/`.
5. Captura o salida de `pytest -v` si escribieron tests (bonus).
