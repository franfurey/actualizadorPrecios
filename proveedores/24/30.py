# /proveedores/24/30.py
# Este es el archivo del proveedor: Upalala

def process_proveedor_file(df):
    """Filtrar y reformatear un DataFrame de Excel para Upalala"""
    print('formateando UPALALA 30.py')
    df = df.drop(index=range(0))
    df = df.rename(columns={
        df.columns[2]: 'SKU',
        df.columns[0]: 'Código de barras',
        df.columns[3]: 'Nombre',
        df.columns[4]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]
    columna = df.iloc[:, 1]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(int).astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace(r'[.+\-E]', '', regex=True)
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    df['Costo'] = df['Costo'].astype(str).str.split('.', n=1, expand=True)[0]

    return df