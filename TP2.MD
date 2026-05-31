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
| Exactitud | Un profesor completa la planilla de notas de examen de un alumno con 8, pero al digitalizar se registra como 3, el dato existe y es valido pero no coincide con la realidad|
| Completitud | ausencia % de algun dato importante en un listado de ingresantes, como Tel. o E-mail |
| Consistencia | Un estudiante figura con el estado "Graduado" en la tabla de Diplomas, pero en la tabla general su estado actual figura como "Regular". |
| Validez | En la columna "nota_final" se asigna "APROBADO" en vez de un entero entre 1-10 (regla de negocio) |
| Unicidad | Un alumno se anotó a una carrera en 2023, abandonó, y en 2025 se volvió a inscribir. En lugar de reutilizar su perfil, se creó un nuevo legajo. |
| Actualidad | Un estudiante aprobó su última materia en las mesas de exámenes de Diciembre, pero preceptoria tarda 4 meses en digitalizar el acta |

---

### Pregunta 2 (5 puntos)
Explicar qué es un **Data Contract** (contrato de datos). ¿Quién lo define? ¿Qué elementos debe contener? ¿Por qué es importante en un equipo donde un Data Engineer produce los datos y un Data Scientist los consume?

Un DATA CONTRACT es un acuerdo entre las personas que generan los datos -los productores- y las que los usan -los consumidores-, es un archivo formal de configuración (normalmente YAML o JSON) que define la estructura, la calidad y los términos de entrega de un set de datos. Es la garantía de que si el productor cambia algo, no va a romper los análisis o modelos de nadie en el camino. 

Se define como implica el nombre, en un acuerdo entre partes, tanto el Consumidor -por ejempl, un analista de datos- como el productor -ingeniero de datos- se sientan y "formalizan" el formato en que van a llegar los datos para el analisis. 

Debe contener:
 1- el SCHEMA (esquema) La estructura pura y dura. Qué columnas tiene la tabla, qué tipo de datos son y si se permiten Nulos, etc.
 2- Reglas de Semántica y Calidad: ej. la columna "edad" tiene que estar entre 18 y 99, o que el ID_usuario tiene que ser único, etc.
 3- SLA de Calidad o Acuerdos de Nivel de Servicio: Acuerdo de actualidad de los datos, completitud, etc.
 4- Metadatos y Propiedad: Quién es el responsable del pipeline si algo falla (el "dueño" del contrato) y qué versión del contrato se está usando.

Es importante porque evita casos como el siguiente: el Data Engineer, buscando optimizar la base de datos, decide cambiar el nombre de la columna user_id por id_usuario. Hace el cambio un viernes a la tarde y se va a su casa. El sábado a la madrugada, el modelo de recomendación del Data Scientist (que busca por user_id) se rompe y cae el servicio.
Con un Data Contract, ese cambio se frena automáticamente en el pipeline del DE antes de impactar al DS.

---

### Pregunta 3 (5 puntos)
¿Cuál es la diferencia entre un **profiling** de datos y una **validación** con Great Expectations? ¿Se reemplazan entre sí o se complementan? Justificar con un ejemplo.

Un Progiling de datos es un proceso descriptivo y exploratorio. Analiza un conjunto de datos para descubrir su estructura, contenido, distribuciones estadísticas, anomalías y relaciones. En cambio, una **validación** con Great Expectations es un proceso **prescriptivo** y evaluativo. Contrasta los datos contra un conjunto de reglas de negocio predefinidas ("expectativas") para asegurar que cumplan con los estándares requeridos.

Se complementan entre si, secuencialmente en el ciclo de datos, con el profiling descubrimos la estructura, que nos permite hacer el contrato de espectativas. Por ejemplo si obtengo un dataset historico del SNM sobre clima en X sector de Misiones, realizo el profiling para constatar las dimensiones de calidad, estructura etc, para luego hacer, si vale la pena el pipeline de validacion con great expectations.

---

### Pregunta 4 (5 puntos)
Explicar el **patrón Gate** en un pipeline de datos. Dibujar (puede ser ASCII o diagrama simple) un pipeline de 4 etapas donde la validación actúe como compuerta. ¿Qué debería suceder cuando la validación falla? Mencionar al menos 2 acciones concretas que el sistema debería tomar.

El patrón Gate es un paradigma de diseño en la ingeniería de datos que actúa como un control de calidad mandatorio dentro de un pipeline. Su función principal es evaluar un conjunto de datos contra reglas predefinidas y determinar si es seguro permitir su avance. Si los datos no cumplen con los estándares de calidad, la "compuerta" se cierra, interrumpiendo el flujo de manera inmediata para evitar que los datos erróneos se propaguen a los sistemas analíticos o de producción.

[ Etapa 1: Ingestión ] ──> Captura de datos crudos (ej. JSON, CSV del SMN)📧
            │
            ▼
[ Etapa 2: Validación ] ◄── COMPUERTA (Great Expectations)🌟
            │
            ├─── [ Si Falla ] ──► 🛑 [ PIPELINE DETENIDO ] (Cierre de Compuerta)
            │                                 │
            └─── [ Si Aprueba ] 🥉            └──► Ejecución de Acciones de Mitigación 🗑
                    │
                    ▼
[ Etapa 3: Transformación ] ──> Procesamiento y lógica de negocio (Limpieza, agregación) 🥈
            │
            ▼
[ Etapa 4: Carga / Destino ] ──> Almacenamiento final (Data Warehouse / Modelos ML) 

Cuando los datos violan una o más restricciones analizadas en la Etapa 2, el pipeline rompe el flujo de ejecución normal de manera controlada. El lote de datos inválido queda bloqueado y se prohíbe estrictamente su ingreso a la Etapa 3 (Transformación) y Etapa 4 (Carga). Esto protege la integridad referencial y la confiabilidad de los reportes finales.

Acciones concretas: 
  - Aislamiento y Cuarentena de Datos: El lote de datos que causó la falla no se elimina ni se procesa; se desvía automáticamente a un repositorio de almacenamiento aislado (DLQ). Esto preserva la evidencia del error para su posterior auditoría y permite que el pipeline quede libre para procesar el siguiente lote si este viniera correcto.
  - Disparo de Alertas Automatizadas: El sistema genera un evento de error crítico y lo envía de forma inmediata a los canales de soporte del equipo de datos.

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


 1. Alertas del Reporte
El reporte genera un total de **6 alertas**. Las 5 más relevantes para la gestión de calidad de datos son:
1. **`humedad` has 898 (17.8%) missing values**: Alerta crítica de completitud que afecta a casi una quinta parte del dataset.
2. **`presion` has 888 (17.6%) missing values**: Segunda variable más afectada por valores faltantes.
3. **`temperatura` has 548 (10.9%) missing values**: Pérdida significativa de registros meteorológicos clave.
4. **`precipitacion` has 51 (1.0%) zeros**: Alerta informativa (en climatología es normal tener días sin lluvia, por lo que no representa un error).
5. **`id` has unique values / is uniformly distributed**: Alertas estructurales que confirman que la columna funciona correctamente como clave primaria.

 2. **No de forma semántica.** El profiling automatizado procesa estos valores -`999` o `-999`- como datos numéricos legítimos, por lo cual, las métricas promedio estan muy sesgadas (la media se desplaza y los máximos/mínimos muestran valores físicamente imposibles) sin generar alerta sobre esto, que es mas importante que tener '0' en precipitacion...

 3. Al analizar el heatmap y la matriz de valores faltantes, se evidencia una correlación extrema (cercana a `1.0`) entre las columnas **`humedad`** y **`presion`**. Esto indica un problema de co-ocurrencia en el origen: casi cada vez que el sensor de una estación meteorológica falla o no reporta el dato de presión, se pierde en simultáneo la medición de la humedad. La columna **`temperatura`** también participa de este patrón de abandono sistemático con sus 548 nulos, sugiriendo apagones completos del módulo de medición en momentos específicos.

 4. Reporta **0 duplicados exactos**. Esto coincide con la tasa de unicidad del 100.0% calculada mediante la función `detectar_duplicados` en el diagnóstico inicial.

 5. Las correlaciónes son completamente ficticias y están rotas**. Al coexistir valores centinela idénticos (`999` o `-999`) en los mismos registros donde fallaron los sensores, el cálculo matemático (Pearson/Spearman) asume que ambas variables se desplazan juntas hacia el infinito de forma "perfecta". Esto enmascara la verdadera relación física de las variables meteorológicas en Misiones, demostrando que el profiling sin una limpieza previa de datos genera conclusiones analíticas erróneas
 
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
```{
    "exito": false,
    "expectations_fallidas": [
        {
            "expectation": "expect_table_columns_to_match_set",
            "kwargs": {
                "column_set": [
                    "id",
                    "fecha",
                    "estacion",
                    "temperatura",
                    "humedad",
                    "presion",
                    "precipitacion"
                ]
            }
        },
        {
            "expectation": "expect_compound_columns_to_be_unique",
            "kwargs": {
                "column_list": [
                    "fecha",
                    "estacion"
                ]
            }
        },
        {
            "expectation": "expect_column_values_to_match_regex",
            "kwargs": {
                "column": "fecha",
                "regex": "^\\d{2}/\\d{2}/\\d{4}$"
            }
        },
        {
            "expectation": "expect_column_values_to_be_in_set",
            "kwargs": {
                "column": "estacion",
                "value_set": [
                    "Posadas",
                    "Oberá",
                    "Apóstoles",
                    "Eldorado",
                    "Puerto Iguazú",
                    "San Vicente",
                    "San Javier",
                    "Bernardo de Irigoyen"
                ]
            }
        },
        {
            "expectation": "expect_column_values_to_be_between",
            "kwargs": {
                "column": "temperatura",
                "min_value": -40.0,
                "max_value": 60.0
            }
        },
        {
            "expectation": "expect_column_values_to_be_between",
            "kwargs": {
                "column": "humedad",
                "min_value": 0.0,
                "max_value": 100.0
            }
        }
    ]
} 
```

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
