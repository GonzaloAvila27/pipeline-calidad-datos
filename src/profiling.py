"""
Script de Data Profiling — TP2 (SIN RESOLVER)

Objetivo:
1. Cargar datos/estaciones_meteo.csv
2. Generar ProfileReport
3. Guardar en reportes/profiling_meteo.html
"""
"""
Módulo: src/profiling.py
Descripción: Script para la generación automatizada de reportes descriptivos 
             de calidad de datos en formato HTML.
"""

import pandas as pd
from pathlib import Path
from ydata_profiling import ProfileReport

def generar_profiling(
    ruta_csv: str = "datos/estaciones_meteo.csv",
    ruta_reporte: str = "reportes/profiling_meteo.html",
) -> None:
    """
    Carga el dataset de estaciones meteorológicas, genera un reporte de profiling
    exhaustivo y lo almacena en formato HTML.
    """
    path_csv = Path(ruta_csv)
    path_reporte = Path(ruta_reporte)

    # Validar existencia del archivo de origen
    if not path_csv.exists():
        raise FileNotFoundError(f"No se encontró el dataset en la ruta: {path_csv.resolve()}")

    # Asegurar la existencia del directorio de reportes (reportes/)
    path_reporte.parent.mkdir(parents=True, exist_ok=True)

    # Cargar el dataset controlando la codificación
    try:
        df = pd.read_csv(path_csv, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path_csv, encoding="latin-1")

    print(f"Carga exitosa. Procesando perfil estadístico para: {path_csv.name}")

    # Inicializar y construir el reporte
    profile = ProfileReport(
        df,
        title="Reporte de Data Profiling - Estaciones Meteorológicas Misiones",
        explorative=True
    )

    # Exportar a ruta destino
    profile.to_file(path_reporte)
    print(f"Proceso finalizado. Reporte exportado en: {path_reporte.resolve()}")


if __name__ == "__main__":
    generar_profiling()
