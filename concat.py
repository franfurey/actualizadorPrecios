import os
from data_saving import save_dataframe_to_excel_with_adjusted_columns, extract_df2_only, save_filtered_df
from data_loading import load_and_prepare_dataframes
from data_processing import calculate_similarity, add_non_matching_rows
from analysis import prepare_result, generate_report


increase_percentage_dict = {
    'algabo': 20,
    'furey': 20,
    'teddy': 10,
    'drimel': 12,
    'upalala': 25
    # Agrega más proveedores y porcentajes aquí...
}

def concat(proveedor):
    archivo1 = f'./procesados/procesadosCanal/{proveedor}.xlsx'
    archivo2 = f'./procesados/{proveedor}.xlsx'
    archivo_resultado = f'./listos/{proveedor}.xlsx'

    df1, df2 = load_and_prepare_dataframes(archivo1, archivo2)
    df_result = calculate_similarity(df1, df2)
    df_result = add_non_matching_rows(df_result, df2)
    df_result = prepare_result(df_result)

    # Extraer filas de df2 que no están en df1
    df2_only = extract_df2_only(df_result)

    # Guarda df_result y df2_only
    save_dataframe_to_excel_with_adjusted_columns(df_result, archivo_resultado)
    save_dataframe_to_excel_with_adjusted_columns(df2_only, f'./listos/nuevos/{proveedor}_only.xlsx')

    # Generar y mostrar estadísticas.
    generate_report(df_result, archivo_resultado)
    
    # Obtén el porcentaje de aumento para este proveedor del diccionario
    increase_percentage = increase_percentage_dict.get(proveedor, 0)

    # Guardar el dataframe filtrado
    save_filtered_df(df_result, proveedor, increase_percentage)  # pass only provider name here

    return df_result






############################################################################# CONCAT ########################################################################################
############################################################################# CONCAT ########################################################################################

# def concat(archivo1, archivo2, archivo_resultado):
#     # Cargar los dos archivos de Excel
#     df1 = pd.read_excel(archivo1)
#     df2 = pd.read_excel(archivo2)

#     # Convertir la columna 'Código de barras' a tipo string en ambos DataFrames
#     df1['Código de barras'] = df1['Código de barras'].astype(str).str.rstrip('.0')
#     df2['Código de barras'] = df2['Código de barras'].astype(str).str.rstrip('.0')


#     # Convertir la columna 'SKU' a tipo string en ambos DataFrames y eliminar '.0' al final si lo hay
#     df1['SKU'] = df1['SKU'].astype(str).str.rstrip('.0')
#     df2['SKU'] = df2['SKU'].astype(str).str.rstrip('.0')

#     # Crear un DataFrame vacío para almacenar las filas de df2 que no están en df1
#     df2_only = pd.DataFrame(columns=['Identificador de URL', 'df2_Nombre', 'Marca', 'df2_SKU', 'df2_Código de barras', 'df2_Costo', 'Precio'])


#     # Crear un DataFrame vacío para almacenar los resultados
#     df_result = pd.DataFrame(columns=['Identificador de URL', 'canal_Nombre', 'Precio', 'canal_SKU', 'canal_Código de barras','canal_Costo',
#                                       'df2_SKU', 'df2_Nombre', 'df2_Código de barras', 'df2_Costo', 'similarity', 'Marca'])

#     # Iterar sobre las filas del primer DataFrame (df1)
#     for i, row1 in df1.iterrows():
#         canal_Nombre = row1['Nombre']
#         Precio = row1['Precio']
#         canal_SKU = row1['SKU']
#         canal_Codigo = row1['Código de barras']
#         canal_Identificador = row1['Identificador de URL']
#         canal_Costo = row1['Costo']
#         found = False

#         # Iterar sobre las filas del segundo DataFrame (df2)
#         for j, row2 in df2.iterrows():
#             df2_Nombre = row2['Nombre']
#             Costo = row2['Costo']
#             df2_SKU = row2['SKU']
#             df2_Codigo = row2['Código de barras']

#             # Calcular la similitud entre los SKUs de df1 y df2 usando FuzzyWuzzy
#             similarity = fuzz.token_set_ratio(canal_Codigo, df2_Codigo)

#             # Si la similitud es mayor o igual al 99%, agregar la fila al DataFrame de resultados
#             if similarity >= 99:
#                 df_result.loc[len(df_result)] = [canal_Identificador, canal_Nombre, Precio, canal_SKU, canal_Codigo, canal_Costo,
#                                                   df2_SKU, df2_Nombre, df2_Codigo, Costo, similarity, row2.get("Marca", "")]
#                 found = True

#         # Si no se encontró una coincidencia, agregar una fila con los datos de df1 y campos vacíos para df2
#         if not found:
#             df_result.loc[len(df_result)] = [canal_Identificador, canal_Nombre, Precio, canal_SKU, canal_Codigo, canal_Costo,
#                                              None, None, None, None, None, None]
            
#     # Iterar sobre las filas del segundo DataFrame (df2) para agregar filas no coincidentes al DataFrame de resultados
#     for i, row2 in df2.iterrows():
#         df2_Nombre = row2['Nombre']
#         Costo = row2['Costo']
#         df2_SKU = row2['SKU']
#         df2_Codigo = row2['Código de barras']
#         found = False

#         # Verificar si el SKU de df2 ya está en el DataFrame de resultados
#         for j, row_result in df_result.iterrows():
#             if row_result['df2_SKU'] == df2_SKU:
#                 found = True
#                 break

#         # Si no se encontró una coincidencia, agregar una fila con los datos de df2 y campos vacíos para df1
#         if not found:
#             df_result.loc[len(df_result)] = [None, None, None, None, None, None, 
#                                              df2_SKU, df2_Nombre, df2_Codigo, Costo, None, row2.get("Marca", "")]
#             df2_only.loc[len(df2_only)] = [None, df2_Nombre, row2.get("Marca", ""), df2_SKU, df2_Codigo, Costo, None]    

#     # Iterar sobre las filas del segundo DataFrame (df2) para agregar filas no coincidentes al DataFrame de resultados
#     for i, row2 in df2.iterrows():
#         df2_Nombre = row2['Nombre']
#         Costo = row2['Costo']
#         df2_SKU = row2['SKU']
#         df2_Codigo = row2['Código de barras']
#         found = False

#         # Verificar si el SKU de df2 ya está en el DataFrame de resultados
#         for j, row_result in df_result.iterrows():
#             if row_result['df2_SKU'] == df2_SKU:
#                 found = True
#                 break

#         # Si no se encontró una coincidencia, agregar una fila con los datos de df2 y campos vacíos para df1
#         if not found:
#             df_result.loc[len(df_result)] = [None, None, None, None, None, None, 
#                                              df2_SKU, df2_Nombre, df2_Codigo, Costo, None, row2.get("Marca", "")]

#     df_result = df_result[['Identificador de URL', 'canal_Nombre','df2_Nombre', 'Marca', 'canal_SKU','df2_SKU', 'canal_Código de barras',
#                             'df2_Código de barras','canal_Costo','df2_Costo', 'Precio', 'similarity']]
    

#     # Reemplazar las comas por un espacio vacío en las columnas 'canal_Costo' y 'df2_Costo'
#     df_result['canal_Costo'] = df_result['canal_Costo'].astype(str).str.replace(',', '')
#     df_result['df2_Costo'] = df_result['df2_Costo'].astype(str).str.replace(',', '')
#     # Redondear los valores en la columna 'df2_Costo' y convertirlos a enteros y luego a string
    


#     df_result['canal_Costo'] = pd.to_numeric(df_result['canal_Costo'], errors='coerce')
#     df_result['df2_Costo'] = pd.to_numeric(df_result['df2_Costo'], errors='coerce')
#     df_result['df2_Costo'] = df_result['df2_Costo'].round()


#     df_result['Porcentaje de aumento'] = ((df_result['df2_Costo'] - df_result['canal_Costo']) / df_result['canal_Costo']) * 100

#     # Ordenar el DataFrame 'df_result' de forma decreciente según la columna 'Porcentaje de aumento'
#     df_result = df_result.sort_values(by='Porcentaje de aumento', ascending=False)

#     # Redondear los números de la columna 'Porcentaje de Aumento' a enteros
#     df_result['Porcentaje de aumento'] = df_result['Porcentaje de aumento'].round()

#     # Guardar el DataFrame en el archivo de Excel
#     save_dataframe_to_excel_with_adjusted_columns(df_result, archivo_resultado)

#     # Guardar el DataFrame df2_only en un archivo de Excel
#     save_dataframe_to_excel_with_adjusted_columns(df2_only, './listos/nuevos/df2_only.xlsx')
    


#     total_rows = len(df_result)
#     exact_match_count = len(df_result[df_result['similarity'] == 100])
#     missing_df1_rows = len(df_result[df_result['df2_SKU'].isnull()])
#     missing_df2_rows = len(df_result[df_result['canal_SKU'].isnull()])


#     # Filtrar el DataFrame para incluir sólo los productos con un aumento mayor a 0%
#     increased_products = df_result[df_result['Porcentaje de aumento'] > 0]

#     # Calcular el aumento promedio sólo con los productos filtrados
#     average_increase = increased_products['Porcentaje de aumento'].mean()
    
#     # Calcular la cantidad de productos que sufrieron un aumento
#     num_products_with_increase = len(increased_products)

#     excessive_threshold = 10
#     excessive_increases = df_result[df_result['Porcentaje de aumento'] > excessive_threshold]

#     print()
#     print(f"En general, los productos aumentaron en un {average_increase:.2f}%.")
#     print(f"De los {total_rows} productos, {num_products_with_increase} sufrieron un aumento.")
#     print()
#     print(f"Total de filas en df_result: {total_rows}")
#     print(f"Filas con similaridad del 100%: {exact_match_count}")
#     print(f"Filas de CANAL no encontradas en df2: {missing_df1_rows}")
#     print(f"Filas de df2 no encontradas en CANAL: {missing_df2_rows}")
#     print()
#     print("Archivo CONCATENADO guardado como",archivo_resultado)
#     print()

#     if len(excessive_increases) > 0:
#         print(f"Se encontraron {len(excessive_increases)} productos con un aumento excesivo:")
#         for idx, row in excessive_increases.iterrows():
#             print(f"  - {row['canal_Nombre']} (SKU: {row['canal_SKU']}) aumentó un {row['Porcentaje de aumento']:.2f}%.")
#     else:
#         print("No se encontraron aumentos excesivos en los productos.")
#     return df_result