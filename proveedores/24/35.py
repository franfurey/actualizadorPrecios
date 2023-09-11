# Este es el archivo del proveedor: Teddy
import pandas as pd

def process_proveedor_file(df):
    """Filtrar y reformatear un DataFrame de Excel para Teddy"""
    df = df.drop(index=range(19))
    df = df.rename(columns={
        df.columns[1]: 'SKU',
        df.columns[2]: 'Código de barras',
        df.columns[3]: 'Nombre',
        df.columns[4]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]

    # Continua el proceso de limpieza...
    # ...
    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 1]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(int).astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace(r'[.+\-E]', '', regex=True)
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    # Convertir la columna SKU_numero a números
    df["SKU"] = pd.to_numeric(df["SKU"], errors="coerce")

    # Ordenar por SKU_numero de forma ascendente
    df = df.sort_values(by='SKU')


    df['Costo'] = df['Costo'].replace(',', '', regex=True)

    # Limpiar los valores de la columna "Costo"
    df['Costo'] = df['Costo'].fillna(0).apply(lambda x: int(float(str(x).split('.')[0])))
    return df