"""
Pipeline ETL con patrón Gate — TP2 (SIN RESOLVER)

Implementar ejecutar_pipeline(ruta_csv: str) -> dict según TP2.MD.
"""


def ejecutar_pipeline(ruta_csv: str) -> dict:
    """
    Debe:
    1. EXTRAER CSV
    2. VALIDAR con GX (Gate)
    3. Si falla: exito=False + expectations fallidas
    4. Si pasa: transformar (normalizar estacion, eliminar duplicados,
       reemplazar centinelas)
    5. Guardar datos/meteo_limpio.csv
    6. Retornar métricas de ejecución
    """
    raise NotImplementedError("Implementar ejecutar_pipeline")
