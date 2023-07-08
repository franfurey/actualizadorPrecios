import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from fuzzywuzzy import fuzz

def calculate_similarity(df1, df2):
    df_result = pd.DataFrame(columns=['Identificador de URL', 'canal_Nombre', 'Precio', 'canal_SKU', 
                                      'canal_Código de barras', 'canal_Costo', 'df2_SKU', 'df2_Nombre', 
                                      'df2_Código de barras', 'df2_Costo', 'similarity', 'Marca'])
    for i, row1 in df1.iterrows():
        for j, row2 in df2.iterrows():
            similarity = fuzz.token_set_ratio(row1['Código de barras'], row2['Código de barras'])
            if similarity >= 99:
                df_result.loc[len(df_result)] = [
                    row1['Identificador de URL'], row1['Nombre'], row1['Precio'], row1['SKU'], 
                    row1['Código de barras'], row1['Costo'], row2['SKU'], row2['Nombre'], 
                    row2['Código de barras'], row2['Costo'], similarity, row2.get('Marca', "")
                ]
                break
        else:
            df_result.loc[len(df_result)] = [
                row1['Identificador de URL'], row1['Nombre'], row1['Precio'], row1['SKU'], 
                row1['Código de barras'], row1['Costo'], None, None, None, None, None, None
            ]
    return df_result

def add_non_matching_rows(df_result, df2):
    for i, row2 in df2.iterrows():
        if not df_result['df2_SKU'].isin([row2['SKU']]).any():
            df_result.loc[len(df_result)] = [
                None, None, None, None, None, None, row2['SKU'], row2['Nombre'], 
                row2['Código de barras'], row2['Costo'], None, row2.get("Marca", "")
            ]
    return df_result