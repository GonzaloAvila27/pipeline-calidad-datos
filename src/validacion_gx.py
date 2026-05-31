"""
Módulo: src/validacion_gx.py
Descripción: Suite de validación automatizada de Calidad de Datos utilizando 
             Great Expectations (Sintaxis oficial definitiva GX v1.0+).
"""

import json
import great_expectations as gx
import pandas as pd
from pathlib import Path

# Usamos barras normales para evitar dolores de cabeza con secuencias de escape en Windows
ruta_dataset = Path("datos/estaciones_meteo.csv")


def crear_suite_meteo(df: pd.DataFrame):
    """
    Debe cubrir al menos:
    - Estructura (columnas obligatorias)
    - Completitud (fecha y estacion)
    - Validez (temperatura y humedad)
    - Consistencia (estacion in set)
    - Unicidad ((fecha, estacion))
    - 2 expectativas extra
    """
    # 1. Crear un contexto de datos efímero en memoria
    context = gx.get_context(mode="ephemeral")

    # 2. Configurar la fuente de datos de Pandas y su Asset
    datasource = context.data_sources.add_pandas(name="meteo_datasource")
    asset = datasource.add_dataframe_asset(name="meteo_asset")
    
    # 3. Definir el lote y asociar el DataFrame en memoria
    batch_definition = asset.add_batch_definition_whole_dataframe(
        name="meteo_batch_definition"
    )
    batch_request = batch_definition.build_batch_request(
        batch_parameters={"dataframe": df}
    )

    # 4. SOLUCIÓN AL ERROR: Crear la suite explícitamente y registrarla en el contexto
    suite = gx.ExpectationSuite(name="suite_estaciones_misiones")
    context.suites.add(suite)

    # 5. Ahora sí, pedir el validador vinculándole la suite recién registrada
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite=suite
    )

    # -------------------------------------------------------------------------
    # 1. ESTRUCTURA (1 Expectation)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 2. COMPLETITUD (2 Expectations)
    # -------------------------------------------------------------------------
    validator.expect_column_values_to_not_be_null(column="fecha")
    validator.expect_column_values_to_not_be_null(column="estacion")

    # -------------------------------------------------------------------------
    # 3. VALIDEZ (2 Expectations)
    # -------------------------------------------------------------------------
    validator.expect_column_values_to_be_between(
        column="temperatura", min_value=-40.0, max_value=60.0
    )
    validator.expect_column_values_to_be_between(
        column="humedad", min_value=0.0, max_value=100.0
    )

    # -------------------------------------------------------------------------
    # 4. CONSISTENCIA (1 Expectation)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 5. UNICIDAD (1 Expectation)
    # -------------------------------------------------------------------------
    validator.expect_compound_columns_to_be_unique(
        column_list=["fecha", "estacion"]
    )

    # -------------------------------------------------------------------------
    # 6. EXTRAS / ADICIONALES (3 Expectations)
    # -------------------------------------------------------------------------
    # Extra 1 (Formato): Patrón DD/MM/AAAA para fechas
    validator.expect_column_values_to_match_regex(
        column="fecha", regex=r"^\d{2}/\d{2}/\d{4}$"
    )

    # Extra 2 (Validez de Rango): Presión barométrica regional estándar
    validator.expect_column_values_to_be_between(
        column="presion", min_value=900.0, max_value=1100.0
    )

    # Extra 3 (Tipado): Asegurar que el ID sea numérico entero
    validator.expect_column_values_to_be_in_type_list(
        column="id", type_list=["int", "int64", "integer"]
    )

    # -------------------------------------------------------------------------
    # EJECUCIÓN DE LA VALIDACIÓN
    # -------------------------------------------------------------------------
    resultado_validacion = validator.validate()
    return resultado_validacion


if __name__ == "__main__":
    print("=" * 60)
    print("EJECUTANDO SUITE DE VALIDACIÓN CON GREAT EXPECTATIONS (V1.0+)")
    print("=" * 60)

    if not ruta_dataset.exists():
        print(f"Error: No se encontró el archivo en {ruta_dataset.resolve()}")
    else:
        try:
            df_raw = pd.read_csv(ruta_dataset, encoding="utf-8")
        except UnicodeDecodeError:
            df_raw = pd.read_csv(ruta_dataset, encoding="latin-1")

        # Ejecutar la validación completa
        res = crear_suite_meteo(df_raw)

        # Extraer métricas de resumen de forma segura para GX v1.0+
        success = res.success
        stats = res.statistics

        print(f"¿El dataset pasó la validación completa?: {'SÍ' if success else 'NO'}")
        print(f"Total de reglas evaluadas: {stats.get('evaluated_expectations')}")
        print(f"Reglas exitosas: {stats.get('successful_expectations')}")
        print(f"Reglas falladas: {stats.get('unsuccessful_expectations')}")
        print(f"Porcentaje de éxito: {stats.get('success_percent'):.2f}%")
        print("=" * 60)

        # Exportar JSON técnico detallado para la entrega del TP
        path_json = Path("reportes/resultado_gx.json")
        path_json.parent.mkdir(parents=True, exist_ok=True)
        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(res.to_json_dict(), f, indent=4, ensure_ascii=False)
        print(f"Detalle técnico exportado a: {path_json.resolve()}")