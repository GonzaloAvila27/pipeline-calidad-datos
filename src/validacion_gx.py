"""
Validación con Great Expectations — TP2 (SIN RESOLVER)

Implementar crear_suite_meteo() con al menos 10 expectations.
"""

import pandas as pd


def crear_suite_meteo(df: pd.DataFrame) -> dict:
    """
    Debe cubrir al menos:
    - Estructura (columnas obligatorias)
    - Completitud (fecha y estacion)
    - Validez (temperatura y humedad)
    - Consistencia (estacion in set)
    - Unicidad ((fecha, estacion))
    - 2 expectativas extra
    """
    raise NotImplementedError("Implementar crear_suite_meteo")
