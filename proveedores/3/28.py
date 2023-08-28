# Este es el archivo del proveedor: ORTOPEDICOS ALFOLATEX
import pandas as pd
import numpy as np

def process_proveedor_file(df):
    # Trabaja con una copia para evitar advertencias
    df = df.copy()
    # Quita los espacios en blanco de los nombres de las columnas que son cadenas
    df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]

    # Verifica si las columnas existen antes de intentar eliminarlas
    columns_to_drop = ['Empresa', 'Unidad']
    columns_to_drop = [col for col in columns_to_drop if col in df.columns]

    # Elimina las columnas si existen
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
    # Renombra las columnas según lo requerido
    df = df.rename(columns={'Cód. Artículo': 'Codigo', 'Descripción artículo': 'Nombre', 'Precio': 'Costo'})

    # Reemplaza los valores '#N/A' con NaN
    df['Costo'] = df['Costo'].replace('#N/A', np.nan)

    # Convierte la columna "Costo" a tipo float
    df['Costo'] = df['Costo'].replace(',', '.', regex=True).astype(float)

    return df
