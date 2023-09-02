# Este es el archivo del proveedor: Furey
import pandas as pd

def process_proveedor_file(df):
    """Filtrar y reformatear un DataFrame de Excel para Furey"""
    df = df.drop(index=range(6))
    df = df.rename(columns={
        df.columns[0]: 'SKU',
        df.columns[1]: 'Código de barras',
        df.columns[2]: 'Nombre',
        df.columns[3]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]

    # Continua el proceso de limpieza...
    # ...
    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 0]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace(r'[.+\-E]', '', regex=True)
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    # Separar la columna SKU en dos columnas
    df["SKU"] = df["SKU"].astype(str)
    df[["num", "SKU_letra"]] = df["SKU"].str.extract(r"(\d+)(\D*)")

    # Convertir la columna SKU_numero a números
    df["num"] = pd.to_numeric(df["num"], errors="coerce")

    # Ordenar por SKU_numero de forma ascendente
    df = df.sort_values(by='num')

    # Concatenar SKU_numero y SKU_letra dentro de SKU_numero
    df['SKU'] =df['num'].astype(str) + df['SKU_letra']
    df = df.drop(columns=['num', 'SKU_letra'])
    df['Costo'] = df['Costo'].astype(str)
    df['Costo'] = df['Costo'].str.replace(',', '').str.replace('\..*', '', regex=True)

    # DESCUENTOS 
    df['Costo'] = pd.to_numeric(df['Costo'])
    df['Costo'] = df['Costo'].apply(lambda x: round(x*0.83))
    return df