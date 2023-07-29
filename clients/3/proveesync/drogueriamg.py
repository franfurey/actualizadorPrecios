import pandas as pd

def filtrar_y_reformatear_mg_cod(df):
    """Filtrar y reformatear un DataFrame"""
    # Supongamos que tu DataFrame se llama df
    df = df.drop(index=range(3))
    df = df.rename(columns={
        df.columns[0]: 'Codigo',
        df.columns[1]: 'Nombre',
        df.columns[2]: 'SKU',
        df.columns[3]: 'Descuento',
        df.columns[4]: 'Descuento 2',
        df.columns[5]: 'Descuento 3',
        df.columns[6]: 'Precio',
        df.columns[7]: 'Vendible'
    })
    df = df[['Codigo', 'Nombre', 'SKU',
            'Descuento','Descuento 2', 'Descuento 3',
            'Precio','Vendible']]

    return df