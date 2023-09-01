# userscripts/24.py
# Este es el archivo de fran@soycanal.com.ar
import os
import importlib
import traceback
import pandas as pd
from fuzzywuzzy import fuzz
from .common_utils import adjust_columns_and_center_text, eliminar_formas_no_imagenes, generate_report_and_pdf

#

def rename_files(current_user_id, proveedor, path):
    files = os.listdir(path)
    print("Archivos en el directorio:", files)
    
    for file in files:
        if os.path.isfile(os.path.join(path, file)):  # Añadido para verificar que es un archivo
            new_name = ""
            
            if file.endswith('.csv'):
                new_name = f"{current_user_id}-{proveedor.nombre}-{'canal' if 'canal' in file else 'proveedor'}.csv"
            elif file.endswith('.xls') or file.endswith('.xlsx'):
                new_name = f"{current_user_id}-{proveedor.nombre}-{'canal' if 'canal' in file else 'proveedor'}.xlsx"
            
            # Verificar si el archivo ya ha sido renombrado
            if new_name and new_name != file:  # Modificado para asegurarse de que new_name no esté vacío
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

########################################################################################################################################################################

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

########################################################################################################################################################################

def combine_dataframes(df1, df2):
    df1 = df1.copy()  # Copiar df1 para evitar cambios en el original
    df2 = df2.copy()  # Copiar df2 para evitar cambios en el original
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

########################################################################################################################################################################

def seleccionar_columnas(df_final, proveedor, path):
    def eliminar_filas_vacias(df):
        return df.dropna(how='all')

    file_name = f"{proveedor.nombre}.xlsx"
    writer = pd.ExcelWriter(os.path.join(path, file_name))

    columnas_hoja1 = ["Identificador de URL", "Nombre", "SKU_proveedor", "Código de barras", 'Costo', "Costo_proveedor", "Precio"]
    columnas_hoja2 = ["Identificador de URL", "Nombre", "Código de barras", "Precio"]
    columnas_hoja3 = ["SKU_proveedor", "Nombre_proveedor",'Código de barras_proveedor', "Costo_proveedor"]

    columnas_hoja1 = [col for col in columnas_hoja1 if col in df_final.columns]
    columnas_hoja2 = [col for col in columnas_hoja2 if col in df_final.columns]
    columnas_hoja3 = [col for col in columnas_hoja3 if col in df_final.columns]

    df_hoja1 = eliminar_filas_vacias(df_final[df_final['similarity'] > 50][columnas_hoja1])
    df_hoja1.to_excel(writer, sheet_name='Productos en Común', index=False)

    # Para la Hoja 2, usamos directamente la columna 'SKU_proveedor'
    filter_condition_2 = df_final['Código de barras_proveedor'].isnull()
    df_hoja2 = eliminar_filas_vacias(df_final[filter_condition_2][columnas_hoja2])
    df_hoja2.to_excel(writer, sheet_name='Productos Descontinuados', index=False)

    # Para la Hoja 3, usamos directamente la columna 'Código de barras'
    filter_condition_3 = df_final['Código de barras'].isnull()
    df_hoja3 = eliminar_filas_vacias(df_final[filter_condition_3][columnas_hoja3])
    df_hoja3.to_excel(writer, sheet_name='Nuevos Productos', index=False)

    writer.save()
    return df_hoja1, df_hoja2, df_hoja3  # Nueva línea al final para devolver los dataframes

#     
def process_files(current_user_id, proveedor, path):
    print("Iniciando process_files 24.py")
    rename_files(current_user_id, proveedor, path)
    df_canal, df_proveedor = None, None
    files = os.listdir(path)
    
    mpn_value = proveedor.nombre  # Asumiendo que "nombre" es el atributo que guarda el nombre del proveedor
    print('Proveedor: ', mpn_value)
    print(f"Lista de archivos después de renombrar: {files}")

    for file in files:
        ext = os.path.splitext(file)[1]
        if ext in ['.xls', '.xlsx', '.csv']:
            print(f"Procesando archivo: {file}")
            try:
                df, filename = leer_archivo(os.path.join(path, file))

                eliminar_formas_no_imagenes(filename)

                if 'canal.csv' in os.path.basename(filename):
                    print(f"DataFrame antes de filtrar_y_reformatear_canal para el archivo {file}:")
                    print(df.head(10))
                    df_canal = filtrar_y_reformatear_canal(df, mpn_value=mpn_value)
                    print(f"DataFrame después de filtrar_y_reformatear_canal para el archivo {file}:")
                    print(df_canal.head(10))
                    df_canal.to_csv(filename, index=False)
                if 'proveedor.xlsx' in os.path.basename(filename):
                    script_proveedor = importlib.import_module(f'proveedores.{current_user_id}.{proveedor.id}')
                    print(f"DataFrame antes de process_proveedor_file para el archivo {file}:")
                    print(df.head(10))
                    df_proveedor = script_proveedor.process_proveedor_file(df)
                    print(f"DataFrame después de process_proveedor_file para el archivo {file}:")
                    print(df_proveedor.head(10))
                    df_proveedor.to_excel(filename, index=False)
            except Exception as e:
                print(f"Error al procesar el archivo {file}: {e}")
                traceback.print_exc()

    if df_canal is not None and df_proveedor is not None:
        df_final = combine_dataframes(df_canal, df_proveedor)
        df_final.to_excel(os.path.join(path, "final.xlsx"), index=False)
        df_hoja1, df_hoja2, df_hoja3 = seleccionar_columnas(df_final, proveedor, path)  # Guardamos los tres dataframes
        adjust_columns_and_center_text(path)

        # Pasamos los dataframes como argumentos adicionales
        generate_report_and_pdf(df_final, path, proveedor.nombre, df_hoja1, df_hoja2, df_hoja3)
