"""
Funciones de diagnóstico de calidad de datos — TP2 (SIN RESOLVER)

Implementar las funciones solicitadas en TP2.MD.
"""

import pandas as pd


def calcular_completitud(df: pd.DataFrame) -> pd.Series:
    """Retorna tasa de completitud (% no nulos) por columna, redondeada a 2 decimales."""
    raise NotImplementedError("Implementar calcular_completitud")


def detectar_duplicados(df: pd.DataFrame, subset: list[str] | None = None) -> dict:
    """Retorna total_filas, duplicados y tasa_unicidad."""
    raise NotImplementedError("Implementar detectar_duplicados")


def detectar_outliers_rango(
    df: pd.DataFrame,
    columna: str,
    minimo: float,
    maximo: float,
) -> dict:
    """Retorna total, fuera_rango y tasa_validez para una columna."""
    raise NotImplementedError("Implementar detectar_outliers_rango")


def detectar_inconsistencias_categoricas(df: pd.DataFrame, columna: str) -> dict:
    """Retorna valores_crudos, valores_normalizados y hay_inconsistencia."""
    raise NotImplementedError("Implementar detectar_inconsistencias_categoricas")
