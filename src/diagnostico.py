"""
Funciones de diagnóstico de calidad de datos — TP2 (SIN RESOLVER)

Implementar las funciones solicitadas en TP2.MD.
"""

import pandas as pd
from pathlib import Path

ruta_dataset = Path("datos\estaciones_meteo.csv")
df = pd.read_csv(ruta_dataset)

def calcular_completitud(df: pd.DataFrame) -> pd.Series:
    """Retorna tasa de completitud (% no nulos) por columna, redondeada a 2 decimales."""
    if df.empty:
        return pd.Series(0.0, index=df.columns)
    
    # .notnull().mean() calcula la proporción; se multiplica por 100 para obtener la tasa
    tasa_completitud = (df.notnull().mean() * 100).round(2)
    return tasa_completitud


def detectar_duplicados(df: pd.DataFrame, subset: list[str] | None = None) -> dict:
    """Retorna total_filas, duplicados y tasa_unicidad."""
    total_filas = len(df)
    
    if total_filas == 0:
        return {
            "total_filas": 0,
            "duplicados": 0,
            "tasa_unicidad": 100.0
        }
    
    # Suma de registros duplicados excluyendo la primera aparición (keep='first' por defecto)
    duplicados = int(df.duplicated(subset=subset).sum())
    tasa_unicidad = round(((total_filas - duplicados) / total_filas) * 100, 2)
    
    return {
        "total_filas": total_filas,
        "duplicados": duplicados,
        "tasa_unicidad": tasa_unicidad
    }

def detectar_outliers_rango( 
    df: pd.DataFrame,
    columna: str,
    minimo: float,
    maximo: float,
) -> dict:
    """Retorna total, fuera_rango y tasa_validez para una columna."""
    valores_validos = df[columna].dropna()
    total = len(valores_validos)
    
    if total == 0:
        return {
            "total": 0,
            "fuera_rango": 0,
            "tasa_validez": 100.0
        }
    
    # Identificación de registros fuera del intervalo cerrado [mínimo, máximo]
    fuera_rango = int(((valores_validos < minimo) | (valores_validos > maximo)).sum())
    tasa_validez = round(((total - fuera_rango) / total) * 100, 2)
    
    return {
        "total": total,
        "fuera_rango": fuera_rango,
        "tasa_validez": tasa_validez
    }


def detectar_inconsistencias_categoricas(df: pd.DataFrame, columna: str) -> dict:
    """Retorna valores_crudos, valores_normalizados y hay_inconsistencia."""
    valores_validos = df[columna].dropna()
    
    valores_crudos = int(valores_validos.nunique())
    
    # Normalización del texto para identificar colisiones de categorías (ej: "Apostoles " vs "apostoles")
    valores_normalizados = int(
        valores_validos.astype(str)
        .str.lower()
        .str.strip()
        .nunique()
    )
    
    hay_inconsistencia = valores_crudos > valores_normalizados
    
    return {
        "valores_crudos": valores_crudos,
        "valores_normalizados": valores_normalizados,
        "hay_inconsistencia": bool(hay_inconsistencia)
    }



if __name__ == "__main__":
    # 1. Ejecutar diagnósticos utilizando las funciones del Ejercicio 1
    
    # Completitud
    comp = calcular_completitud(df)
    col_mas_afectada = comp.idxmin()
    tasa_comp_min = comp.min()
    
    # Unicidad
    uni = detectar_duplicados(df)
    
    # Validez (Temperatura y Humedad)
    val_temp = detectar_outliers_rango(df, "temperatura", -40.0, 60.0)
    val_hum = detectar_outliers_rango(df, "humedad", 0.0, 100.0)
    
    # Consistencia
    cons = detectar_inconsistencias_categoricas(df, "estacion")
    
    # Actualidad (Cálculo directo sobre la columna fecha)
    df_fechas = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
    fecha_min = df_fechas.min().strftime("%d/%m/%Y") if pd.notnull(df_fechas.min()) else "N/A"
    fecha_max = df_fechas.max().strftime("%d/%m/%Y") if pd.notnull(df_fechas.max()) else "N/A"
    
    # 2. Construcción dinámica del contenido de REPORTE_CALIDAD.md
    contenido_reporte = f"""# Reporte de Calidad de Datos — Estaciones Meteorológicas Misiones

Este reporte presenta el diagnóstico cuantitativo de las dimensiones de calidad analizadas sobre el dataset `datos/estaciones_meteo.csv`.

| Dimensión | Métrica calculada | Valor | Observaciones |
| :--- | :--- | :--- | :--- |
| **Completitud** | Tasa de completitud mínima | {tasa_comp_min}% | La columna más afectada es `{col_mas_afectada}`. |
| **Unicidad** | Tasa de unicidad (filas completas) | {uni['tasa_unicidad']}% | Se detectaron un total de {uni['duplicados']} filas duplicadas. |
| **Validez (temp.)** | Tasa de validez en `temperatura` [-40, 60] | {val_temp['tasa_validez']}% | Existen {val_temp['fuera_rango']} registros fuera del rango físico establecido. |
| **Validez (hum.)** | Tasa de validez en `humedad` [0, 100] | {val_hum['tasa_validez']}% | Existen {val_hum['fuera_rango']} registros con porcentajes de humedad inválidos. |
| **Consistencia** | Inconsistencia en `estacion` | {cons['valores_crudos']} vs {cons['valores_normalizados']} | {'Hay inconsistencias. Existen variantes por tipeo, espacios o mayúsculas.' if cons['hay_inconsistencia'] else 'No se detectaron inconsistencias de escritura.'} |
| **Actualidad** | Rango de fechas del dataset | {fecha_min} — {fecha_max} | Monitorear si el rango cubre el período esperado o incluye años fuera de contexto. |

---
*Reporte generado automáticamente mediante el módulo `src/diagnostico.py`.*
"""

    # 3. Escritura del archivo en la raíz del proyecto
    ruta_reporte = Path("REPORTE_CALIDAD.md")
    with open(ruta_reporte, "w", encoding="utf-8") as f:
        f.write(contenido_reporte)
        
    print(f"Éxito: Se ha generado el archivo '{ruta_reporte.resolve()}' con las métricas calculadas.")