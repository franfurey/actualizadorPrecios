import pandas as pd
from fuzzywuzzy import fuzz

def calculate_similarity(df1, df2):
    rows_list = []
    
    df1 = df1.copy()  # Hacer una copia para evitar advertencias
    df2 = df2.copy()  # Hacer una copia para evitar advertencias

    for i, row1 in df1.iterrows():
        for j, row2 in df2.iterrows():
            similarity = fuzz.token_set_ratio(row1['Código de barras'], row2['Código de barras'])
            if similarity >= 99:
                row_dict = {
                    'Identificador de URL': row1['Identificador de URL'], 
                    'canal_Nombre': row1['Nombre'], 
                    'Precio': row1['Precio'], 
                    'canal_SKU': row1['SKU'], 
                    'canal_Código de barras': row1['Código de barras'], 
                    'canal_Costo': row1['Costo'], 
                    'df2_SKU': row2['SKU'], 
                    'df2_Nombre': row2['Nombre'], 
                    'df2_Código de barras': row2['Código de barras'], 
                    'df2_Costo': row2['Costo'], 
                    'similarity': similarity, 
                    'Marca': row2.get('Marca', ""), 
                    'canal_Categorías': row1['Categorías'], 
                    'canal_Tags': row1['Tags'], 
                    'canal_Título para SEO': row1['Título para SEO'], 
                    'canal_Descripción para SEO': row1['Descripción para SEO'], 
                    'canal_Descripción': row1['Descripción'], 
                    'canal_Marca': row1['Marca']
                }
                rows_list.append(row_dict)
                break
        else:
            row_dict = {
                'Identificador de URL': row1['Identificador de URL'], 
                'canal_Nombre': row1['Nombre'], 
                'Precio': row1['Precio'], 
                'canal_SKU': row1['SKU'], 
                'canal_Código de barras': row1['Código de barras'], 
                'canal_Costo': row1['Costo'], 
                'df2_SKU': None, 
                'df2_Nombre': None, 
                'df2_Código de barras': None, 
                'df2_Costo': None, 
                'similarity': None, 
                'Marca': None, 
                'canal_Categorías': row1['Categorías'], 
                'canal_Tags': row1['Tags'], 
                'canal_Título para SEO': row1['Título para SEO'], 
                'canal_Descripción para SEO': row1['Descripción para SEO'], 
                'canal_Descripción': row1['Descripción'], 
                'canal_Marca': row1['Marca']
            }
            rows_list.append(row_dict)
    
    df_result = pd.DataFrame(rows_list)
    return df_result


def add_non_matching_rows(df_result, df2):
    rows_list = []
    df2 = df2.copy()  # Hacer una copia para evitar advertencias

    for i, row2 in df2.iterrows():
        if not df_result['df2_SKU'].isin([row2['SKU']]).any():
            row_dict = {
                'Identificador de URL': None, 
                'canal_Nombre': None, 
                'Precio': None, 
                'canal_SKU': None, 
                'canal_Código de barras': None, 
                'canal_Costo': None, 
                'df2_SKU': row2['SKU'], 
                'df2_Nombre': row2['Nombre'], 
                'df2_Código de barras': row2['Código de barras'], 
                'df2_Costo': row2['Costo'], 
                'similarity': None, 
                'Marca': row2.get("Marca", ""), 
                'canal_Categorías': None, 
                'canal_Tags': None, 
                'canal_Título para SEO': None, 
                'canal_Descripción para SEO': None, 
                'canal_Descripción': None, 
                'canal_Marca': None
            }
            rows_list.append(row_dict)
    
    df_result = pd.concat([df_result, pd.DataFrame(rows_list)], ignore_index=True)
    return df_result

########################################################################################################################################################################

brand_keywords = {
    'Algabo': ['alg', 'alga', 'algabo'],
    'Tablada': ['tablada'],
    'Chapoteando': ['ch '],
    'Furey': ['furey'],
    'Coronet': ['coronet'],
    'Ibc': ['ibc'],
    'Jessamy': ['jmy', 'jessamy'],
    'O2+': ['o2+'],
    'Drogal': ['drogal'],
    'Dexal': ['dexal'],
    'Hipoalergic': ['hipo'],
    'Trux': ['trux'],
    'Mary bosques': ['mb ', 'mary bosques'],
    'Nonisec': ['nonisec'],
    'Repuesto service': ['rep '],
    'Bremen': ['bremen'],
    'Neojet': ['neojet'],
    'Jactans': ['jac ', 'jactans'],
    'Disney': ['dis ', 'disney'],
    'Mas': ['ms ', 'mas'],
    'Pademed': ['pademed'],
    'Mac gregor': ['mac '],
    'Porta': ['porta'],
    'Silfab': ['silfab'],
    'Lenox': ['lx ', 'lenox'],
    'Dismar': ['dismar'],
    'Vertice': ['vertice'],
    'Exatherm': ['exatherm'],
    'Otowil': ['oto '],
    'Xzn': ['xzn '],
    'Doncella': ['don '],
    'Vais': ['vais']
}

def assign_brand(proveedor):
    path = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/data/proveedor/{proveedor}/listos/{proveedor}.xlsx'

    # Leer el archivo de Excel
    df = pd.read_excel(path, usecols=['Identificador de URL', 'canal_Marca', 'df2_Nombre'])

    # Eliminar filas con valores nulos en 'df2_Nombre' o 'Identificador de URL'
    df = df.dropna(subset=['df2_Nombre', 'Identificador de URL'])

    # Contar el número de filas con valores vacíos en 'canal_Marca'
    total_empty = df['canal_Marca'].isna().sum()
    print('Cantidad de productos sin Marca definida: ', total_empty)

    # Asignar marca a cada producto
    for i in df.index:
        product_name = df.loc[i, 'df2_Nombre'].lower()
        for brand, keywords in brand_keywords.items():
            for keyword in keywords:
                if keyword.lower() in product_name:
                    df.loc[i, 'canal_Marca'] = brand
                    break

    # Guardar el DataFrame resultante en un nuevo archivo de Excel
    df.to_excel(path.replace('.xlsx', '_updated.xlsx'), index=False)

    return None
