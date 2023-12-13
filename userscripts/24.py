# userscripts/24.py
# Este es el archivo de fran@soycanal.com.ar
import os
import importlib
import traceback
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from .common_utils import adjust_columns_and_center_text, eliminar_formas_no_imagenes, generate_report_and_pdf

#

def rename_files(current_user_id: str, proveedor: object, path: str) -> None:
    """
    Renombra los archivos en un directorio dado según ciertos criterios.

    Args:
    current_user_id (str): El ID del usuario actual.
    proveedor (object): Objeto que representa al proveedor, debe tener un atributo 'nombre'.
    path (str): Ruta del directorio donde se encuentran los archivos a renombrar.
    """
    files = os.listdir(path)

    for file in files:
        if not os.path.isfile(os.path.join(path, file)):
            continue

        file_type = 'canal' if 'canal' in file else 'proveedor'
        extension = '.csv' if file.endswith('.csv') else '.xlsx' if file.endswith(('.xls', '.xlsx')) else None

        if extension:
            new_name = f"{current_user_id}-{proveedor.nombre}-{file_type}{extension}"
            if new_name != file:
                os.rename(os.path.join(path, file), os.path.join(path, new_name))
                print(f"Archivo renombrado a: {new_name}")


#

def leer_archivo(filename, skiprows=0):
    if not os.path.isfile(filename):
        print("El archivo no existe")
        return None, None

    try:
        df = None
        new_filename = filename  # Para no perder el nombre original en caso de que sea CSV
        
        if filename.endswith('.csv'):
            df = pd.read_csv(filename, encoding='ISO-8859-1', sep=';', skiprows=skiprows)
        elif filename.endswith('.xls'):
            df = pd.read_excel(filename, skiprows=skiprows, engine='xlrd')
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filename, skiprows=skiprows, engine='openpyxl')

        if df is not None:
            if filename.endswith('.xls'):
                new_filename = filename.split('.')[0] + '.xlsx'
                df.to_excel(new_filename, index=False, engine='openpyxl')
                if filename != new_filename:
                    os.remove(filename)


            # Eliminar columnas con 'None' como nombre
            df.drop(columns=[col for col in df.columns if col is None], inplace=True)
            
        return df, new_filename

    except Exception as e:
        print(f"Error al leer el archivo: {filename}, {str(e)}")
        traceback.print_exc()
        return None, None

#

def filtrar_y_reformatear_canal(df, mpn_value=None):
    """Filtrar y reformatear un DataFrame"""
    df = df[['Identificador de URL', 'Nombre', 'Precio', 'SKU','Código de barras','MPN (Número de pieza del fabricante)', 'Costo','Categorías', 'Tags', 'Título para SEO', 'Descripción para SEO']]
    if mpn_value is not None:
        df = df[df['MPN (Número de pieza del fabricante)'] == mpn_value]

    # Limpiar la columna Precio
    df['Precio'] = df['Precio'].str.replace('\..*', '', regex=True).str.replace(',', '')
    df['Precio'] = pd.to_numeric(df['Precio'])

    # Extraer la palabra y el número de la columna SKU
    df[['SKU_palabra', 'SKU_num']] = df['SKU'].str.extract(r"(\D+)(\d+)")

    # Convertir la columna SKU_num a números
    df["SKU_num"] = pd.to_numeric(df["SKU_num"], errors="coerce")

    # Ordenar por SKU_num de forma ascendente
    df = df.sort_values(by='SKU_num')
    df['SKU_modificado'] = df['SKU_palabra'] + df['SKU_num'].astype(str)

    # Eliminar la columna SKU_letra
    df.drop(['SKU','SKU_num','SKU_palabra'], axis=1, inplace=True)
    df = df.rename(columns={'SKU_modificado': 'SKU'})
    return df

#

def combine_dataframes(df1, df2):
    rows_list = []
    # Ajustar nombres de columnas en df2
    df2.columns = [col + '_proveedor' if col in df1.columns else col for col in df2.columns]
    
    for i, row1 in df1.iterrows():
        match_found = False
        for j, row2 in df2.iterrows():
            # Inicializar variables
            similarity = 0
            code_match = False
            
            # Calcular similitud en "Código de barras" si está disponible
            if 'Código de barras' in row1 and 'Código de barras_proveedor' in row2:
                similarity = fuzz.token_set_ratio(row1['Código de barras'], row2['Código de barras_proveedor'])

            # Verificar coincidencia de códigos si están disponibles
            if 'SKU_proveedor' in row2 and 'SKU' in row1:
                code_match = row1['SKU'] == row2['SKU_proveedor']
            
            if similarity >= 94 or code_match:
                combined_row = pd.concat([row1, row2])
                combined_row['similarity'] = similarity if similarity >= 94 else 55
                rows_list.append(combined_row)
                match_found = True
                break

        if not match_found:
            rows_list.append(row1)

    # Añadir filas de df2 que no coinciden con ninguna fila de df1
    for i, row2 in df2.iterrows():
        if not any((fuzz.token_set_ratio(row2['Código de barras_proveedor'], row1['Código de barras']) >= 94) or (row2['SKU_proveedor'] == row1['SKU']) for _, row1 in df1.iterrows()):
            rows_list.append(row2)

    result_df = pd.DataFrame(rows_list)
    return result_df

#

def agregar_porcentaje_aumento(df):
    # Convierte toda la columna a cadenas primero para evitar errores con el método `.str`
    df['Costo'] = df['Costo'].astype(str)
    df['Costo_proveedor'] = df['Costo_proveedor'].astype(str)
    
    # Reemplazamos las comas y convertimos a numérico
    df['Costo'] = pd.to_numeric(df['Costo'].str.replace(',', ''), errors='coerce')
    df['Costo_proveedor'] = pd.to_numeric(df['Costo_proveedor'].str.replace(',', ''), errors='coerce')

    # Imprimir valores únicos para depuración
    print("Valores únicos en 'Costo':", df['Costo'].unique())
    print("Valores únicos en 'Costo_proveedor':", df['Costo_proveedor'].unique())
    
    # Reemplazamos los NaN por 0 (o cualquier otro valor que consideres apropiado)
    df['Costo'].fillna(0, inplace=True)
    df['Costo_proveedor'].fillna(0, inplace=True)

    # Calculamos el porcentaje de aumento
    df['Porcentaje_Aumento'] = ((df['Costo_proveedor'] - df['Costo']) / df['Costo']) * 100
    
    # Lidiar con infinitos después de la división (si Costo es 0)
    df['Porcentaje_Aumento'].replace([np.inf, -np.inf], np.nan, inplace=True)
    # Reemplazar NaN con 0 (o cualquier otro valor que consideres apropiado)
    df['Porcentaje_Aumento'].fillna(0, inplace=True)

    # Redondear los números flotantes al entero más cercano
    df['Porcentaje_Aumento'] = df['Porcentaje_Aumento'].round()
    # Imprimir valores únicos en 'Porcentaje_Aumento' para depuración antes de convertir a enteros
    print("Valores únicos en 'Porcentaje_Aumento' antes de convertir a enteros:", df['Porcentaje_Aumento'].unique())
    print("Tipo de datos en 'Porcentaje_Aumento' antes de convertir a enteros:", df['Porcentaje_Aumento'].dtype)

    
    # Convertimos a entero
    df['Porcentaje_Aumento'] = df['Porcentaje_Aumento'].astype(int)
    
    # Ordenamos el DataFrame de forma descendente
    df.sort_values('Porcentaje_Aumento', ascending=False, inplace=True)
    return df


#

def seleccionar_columnas(df_final, proveedor, path, porcentaje_aumento):
    def eliminar_filas_vacias(df):
        return df.dropna(how='all')
    
    print("Tipos de datos antes de la operación:")
    print(df_final.dtypes)
    
    file_name = f"{proveedor.nombre}-PS.xlsx"
    writer = pd.ExcelWriter(os.path.join(path, file_name))
    
    columnas_hoja1 = ["Identificador de URL", "Nombre", "SKU_proveedor", "Código de barras", 'Costo', "Costo_proveedor", "Precio"]
    columnas_hoja2 = ["Identificador de URL", "Nombre", "Código de barras", "Precio"]
    columnas_hoja3 = ["SKU_proveedor", "Nombre_proveedor", 'Código de barras_proveedor', "Costo_proveedor"]

    columnas_hoja1 = [col for col in columnas_hoja1 if col in df_final.columns]
    columnas_hoja2 = [col for col in columnas_hoja2 if col in df_final.columns]
    columnas_hoja3 = [col for col in columnas_hoja3 if col in df_final.columns]
    
    print('df_final')
    print(df_final.columns)
    print(df_final)
    df_hoja1 = eliminar_filas_vacias(df_final[df_final['similarity'] > 50][columnas_hoja1])
    df_hoja1 = agregar_porcentaje_aumento(df_hoja1)
    # Actualizar los precios con el porcentaje de aumento en df_hoja1
    if porcentaje_aumento != 0:
        
        # Verificar si porcentaje_aumento es None o una cadena vacía
        if porcentaje_aumento is None or str(porcentaje_aumento).strip() == '':
            print("Porcentaje de aumento no proporcionado, usando valor por defecto de 0")
            factor_aumento = 1.0
        else:
            try:
                print(f"Valor de porcentaje_aumento: {porcentaje_aumento}")  
                factor_aumento = 1 + (float(porcentaje_aumento) / 100)
                print(f"Valor de factor_aumento: {factor_aumento}")
            except ValueError as e:
                print(f"Error al convertir el porcentaje de aumento a float: {e}")
                factor_aumento = 1.0  # Valor por defecto en caso de error
        
        df_hoja1['Costo_proveedor'] = df_hoja1['Costo_proveedor'].astype(float)
        df_hoja1['Precios_Nuevos'] = round(df_hoja1['Costo_proveedor'] * factor_aumento).astype(int)


        print("Valores de 'Precios_Nuevos' después de la multiplicación:")
        print(df_hoja1['Precios_Nuevos'].head())

    df_hoja1.to_excel(writer, sheet_name='Productos en Común', index=False)
    
    filter_condition_2 = df_final['Código de barras_proveedor'].isnull()
    df_hoja2 = eliminar_filas_vacias(df_final[filter_condition_2][columnas_hoja2])
    df_hoja2.to_excel(writer, sheet_name='Productos Descontinuados', index=False)

    filter_condition_3 = df_final['Código de barras'].isnull()
    df_hoja3 = eliminar_filas_vacias(df_final[filter_condition_3][columnas_hoja3])
    df_hoja3.to_excel(writer, sheet_name='Nuevos Productos', index=False)
    
    writer.save()
    return df_hoja1, df_hoja2, df_hoja3

#

def generar_csv(path, proveedor):
    # Construye el nombre del archivo Excel y del archivo CSV
    file_name_xlsx = f"{proveedor.nombre}-PS.xlsx"
    file_name_csv = f"{proveedor.nombre}-TiendaNube-PS.csv"

    # Define la ruta completa al archivo Excel
    full_path_xlsx = os.path.join(path, file_name_xlsx)
    # Define la ruta completa donde se guardará el archivo CSV
    full_path_csv = os.path.join(path, file_name_csv)
    
    # Lee la hoja 'Productos en Común' del archivo Excel
    df = pd.read_excel(full_path_xlsx, sheet_name='Productos en Común')
    
    # Filtra los productos donde Porcentaje_Aumento es diferente de 0
    df_filtered = df[df["Porcentaje_Aumento"] != 0]
    
    # Selecciona las columnas deseadas
    df_selected = df_filtered[["Identificador de URL", "Costo_proveedor", "Precios_Nuevos"]]
    
    # Renombra las columnas
    df_selected.rename(columns={"Costo_proveedor": "Costo", "Precios_Nuevos": "Precio"}, inplace=True)
    
    # Guarda el DataFrame en un archivo CSV
    df_selected.to_csv(full_path_csv, index=False)

# 
    
def process_files(current_user, current_user_id, proveedor, path, porcentaje_aumento):
    print("Iniciando la función process_files...")
    
    rename_files(current_user_id, proveedor, path)
    df_canal, df_proveedor = None, None
    
    files = os.listdir(path)
    porcentaje_aumento = porcentaje_aumento  # Esto parece redundante, considera eliminarlo
    mpn_value = proveedor.nombre
    
    print('Proveedor: ', mpn_value)
    print(f"Lista de archivos después de renombrar: {files}")

    

    for file in files:
        print(f"Evaluando el archivo: {file}")
        ext = os.path.splitext(file)[1]
        
        if ext in ['.xls', '.xlsx', '.csv']:
            print(f"Procesando archivo: {file}")
            try:
                df, filename = leer_archivo(os.path.join(path, file))
                print(f"DataFrame leído desde {filename}, primeras filas:")
                print(df.head(10))
                
                eliminar_formas_no_imagenes(filename)

                if 'canal.csv' in os.path.basename(filename):
                    print(f"Archivo {file} identificado como canal.csv")
                    df_canal = filtrar_y_reformatear_canal(df, mpn_value=mpn_value)
                    print(f"DataFrame después de filtrar_y_reformatear_canal:")
                    print(df_canal.head(10))
                    df_canal.to_csv(filename, index=False)
                
                if 'proveedor.xlsx' in os.path.basename(filename):
                    print(f"Archivo {file} identificado como proveedor.xlsx")
                    script_proveedor = importlib.import_module(f'proveedores.{current_user_id}.{proveedor.id}')
                    df_proveedor = script_proveedor.process_proveedor_file(df)
                    print(f"DataFrame después de process_proveedor_file:")
                    print(df_proveedor.head(10))
                    df_proveedor.to_excel(filename, index=False)

                else:
                    try:
                        print("Intentando importar módulo de proveedor por defecto.")
                        script_proveedor = importlib.import_module(f'proveedores.{current_user_id}.{proveedor.id}')
                        df_proveedor = script_proveedor.process_proveedor_file()
                        print(f"DataFrame después de process_proveedor_file con módulo importado por defecto:")
                        print(df_proveedor.head(10))
                    except ImportError:
                        print(f"No se pudo importar el módulo para el proveedor {proveedor.id}")

            except Exception as e:
                print(f"Error al procesar el archivo {file}: {e}")
                traceback.print_exc()

    if df_canal is not None and df_proveedor is not None:
        print("Combinando DataFrames...")
        df_final = combine_dataframes(df_canal, df_proveedor)
        df_final.to_excel(os.path.join(path, "final.xlsx"), index=False)
        
        print("Seleccionando columnas...")
        df_hoja1, df_hoja2, df_hoja3 = seleccionar_columnas(df_final, proveedor, path, porcentaje_aumento)
        
        adjust_columns_and_center_text(path)
        generate_report_and_pdf(df_final, path, proveedor.nombre, df_hoja1, df_hoja2, df_hoja3, porcentaje_aumento=porcentaje_aumento, user=current_user)
        
        print("Generando CSV...")
        generar_csv(path, proveedor)
    
    print("Finalizando la función process_files.")
