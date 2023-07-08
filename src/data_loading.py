import pandas as pd


def load_and_prepare_dataframes(archivo1, archivo2):
    df1 = pd.read_excel(archivo1)
    df2 = pd.read_excel(archivo2)

    for df in (df1, df2):
        for column in ['Código de barras', 'SKU']:
            df[column] = df[column].astype(str).str.rstrip('.0')

    return df1, df2