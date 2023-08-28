# proveedores/3/2.py
# Este es el archivo del proveedor: Distribuidora R3 S.R.L
import pandas as pd

def process_proveedor_file(df):
    # Trabaja con una copia para evitar advertencias
    df = df.copy()
    # Elimina las primeras 8 filas
    df = df.drop(columns=[df.columns[0], df.columns[2], df.columns[4], df.columns[6], df.columns[7]])
    df = df.drop(range(7))
    # Establece la primera fila como nombres de columnas
    df.columns = df.iloc[0]
    df = df[1:]

    # Renombrar columnas
    df = df.rename(columns={df.columns[1]: 'Codigo', 'P. Neto': 'Costo', 'Descripción': 'Nombre', 'Cód. Barras': 'SKU'})

    # Asigna "000000000000" a SKU si Codigo tiene un valor y SKU está vacío
    df['SKU'] = df.apply(lambda row: "000000000000" if pd.notnull(row['Codigo']) and pd.isnull(row['SKU']) else row['SKU'], axis=1)

    # Rellena los valores NaN en SKU con una cadena vacía
    df['SKU'] = df['SKU'].fillna('')

    # Elimina las filas donde SKU no es numérico
    df = df[df['SKU'].str.isnumeric()]

    # Reemplaza "000000000000" en SKU con una cadena vacía
    df['SKU'] = df['SKU'].replace("000000000000", '')

    return df
