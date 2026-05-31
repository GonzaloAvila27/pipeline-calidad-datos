"""
Pipeline ETL con patrón Gate — TP2 (SIN RESOLVER)

Implementar ejecutar_pipeline(ruta_csv: str) -> dict según TP2.MD.
"""
"""
Módulo: src/pipeline.py
Descripción: Pipeline ETL con patrón Gate utilizando Great Expectations (GX v1.0+).
"""

import json
import great_expectations as gx
import pandas as pd
from pathlib import Path

# Ruta por defecto para el dataset crudo
RUTA_DATASET_RAW = "datos/estaciones_meteo.csv"


def validar_datos_con_gx(df: pd.DataFrame):
    """
    Función interna que encapsula la suite de 10 expectativas (GX v1.0+)
    para actuar como compuerta (Gate) de calidad de datos.
    """
    context = gx.get_context(mode="ephemeral")
    datasource = context.data_sources.add_pandas(name="pipeline_datasource")
    asset = datasource.add_dataframe_asset(name="pipeline_asset")

    batch_definition = asset.add_batch_definition_whole_dataframe(
        name="pipeline_batch_definition"
    )
    batch_request = batch_definition.build_batch_request(
        batch_parameters={"dataframe": df}
    )

    suite = gx.ExpectationSuite(name="suite_pipeline_gate")
    context.suites.add(suite)

    validator = context.get_validator(
        batch_request=batch_request, expectation_suite=suite
    )

    # 1. ESTRUCTURA (1 Expectation)
    validator.expect_table_columns_to_match_set(
        column_set=[
            "id",
            "fecha",
            "estacion",
            "temperatura",
            "humedad",
            "presion",
            "precipitacion",
        ]
    )

    # 2. COMPLETITUD (2 Expectations)
    validator.expect_column_values_to_not_be_null(column="fecha")
    validator.expect_column_values_to_not_be_null(column="estacion")

    # 3. VALIDEZ (2 Expectations)
    validator.expect_column_values_to_be_between(
        column="temperatura", min_value=-40.0, max_value=60.0
    )
    validator.expect_column_values_to_be_between(
        column="humedad", min_value=0.0, max_value=100.0
    )

    # 4. CONSISTENCIA (1 Expectation)
    lista_estaciones_validas = [
        "Posadas",
        "Oberá",
        "Apóstoles",
        "Eldorado",
        "Puerto Iguazú",
        "San Vicente",
        "San Javier",
        "Bernardo de Irigoyen",
    ]
    validator.expect_column_values_to_be_in_set(
        column="estacion", value_set=lista_estaciones_validas
    )

    # 5. UNICIDAD (1 Expectation)
    validator.expect_compound_columns_to_be_unique(
        column_list=["fecha", "estacion"]
    )

    # 6. EXTRAS / ADICIONALES (3 Expectations)
    validator.expect_column_values_to_match_regex(
        column="fecha", regex=r"^\d{2}/\d{2}/\d{4}$"
    )
    validator.expect_column_values_to_be_between(
        column="presion", min_value=900.0, max_value=1100.0
    )
    validator.expect_column_values_to_be_in_type_list(
        column="id", type_list=["int", "int64", "integer"]
    )

    return validator.validate()


def ejecutar_pipeline(ruta_csv: str) -> dict:
    """
    Ejecuta el ciclo de vida de los datos (Extract, Validate, Transform, Load).
    Aplica patrón Gate de control estricto.
    """
    ruta = Path(ruta_csv)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo de origen en: {ruta.resolve()}")

    # 1. EXTRACCIÓN 
    try:
        df = pd.read_csv(ruta, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(ruta, encoding="latin-1")

    filas_originales = len(df)

    # 2. VALIDACIÓN (Patrón Gate)
    resultado_gx = validar_datos_con_gx(df)

    # 3. COMPORTAMIENTO SI LA VALIDACIÓN FALLA (Gate Cerrado)
    if not resultado_gx.success:
        expectations_fallidas = []
        for run_result in resultado_gx.results:
            if not run_result.success:
                # Extraemos el tipo de regla y sus parámetros limpiamente
                config = run_result.expectation_config
                expectations_fallidas.append({
                    "expectation": config.type,
                    "kwargs": {k: v for k, v in config.kwargs.items() if k != "batch_id"}
                })
        
        return {
            "exito": False,
            "expectations_fallidas": expectations_fallidas
        }

    # 4. COMPORTAMIENTO SI LA VALIDACIÓN PASA (Gate Abierto -> Transformaciones)
    if "estacion" in df.columns:
        df["estacion"] = df["estacion"].astype(str).str.strip().str.title()

    # - Eliminar filas duplicadas
    df = df.drop_duplicates()

    # - Reemplazar valores centinela técnicos (999, -999) por None
    valores_centinela = [999, -999, 999.0, -999.0]
    df = df.replace(valores_centinela, None)

    filas_limpias = len(df)
    filas_eliminadas = filas_originales - filas_limpias

    # 5. CARGA (Guardar resultado limpio)
    ruta_salida = Path("datos/meteo_limpio.csv")
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")

    # 6. RETORNAR MÉTRICAS EXITOSAS
    return {
        "exito": True,
        "filas_originales": filas_originales,
        "filas_limpias": filas_limpias,
        "filas_eliminadas": filas_eliminadas
    }


if __name__ == "__main__":
    print("=" * 60)
    print("EJECUTANDO PIPELINE ETL CON PATRÓN GATE")
    print("=" * 60)

    # Ejecutar el pipeline con el archivo crudo
    resultado_ejecucion = ejecutar_pipeline(RUTA_DATASET_RAW)

    # Mostrar la salida formateada elegantemente en consola
    print(json.dumps(resultado_ejecucion, indent=4, ensure_ascii=False))
    print("=" * 60)