# proveedores/3/2.py
# Este es el archivo del proveedor: Distribuidora R3 S.R.L
import pandas as pd

def process_proveedor_file(df):
    # Elimina las primeras 8 filas
    df = df.drop(columns=[df.columns[0],df.columns[2], df.columns[4], df.columns[6], df.columns[7]])
    df = df.drop(range(7))
    # Establece la primera fila como nombres de columnas
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.rename(columns={df.columns[1]: 'Codigo'})

    # Reemplaza los valores NaN con una cadena vacía y luego elimina las filas donde 'Cód. Barras' no es numérico
    df['Cód. Barras'] = df['Cód. Barras'].fillna('')
    df = df[df['Cód. Barras'].str.isnumeric()]
    df = df.rename(columns={'Cód. Barras': 'SKU'})
    return df
