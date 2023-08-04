# userscripts/3.py
import importlib
import os
import pandas as pd
import openpyxl
import traceback

def rename_files(current_user_id, proveedor, path):
    # Obtenemos la lista de archivos en el directorio.
    files = os.listdir(path)
    print(f"Archivos en el directorio {path}: {files}")

    for file in files:
        # Procesamos solo los archivos .xls y .xlsx
        if file.endswith('.xls') or file.endswith('.xlsx'):
            print(f"Procesando archivo: {file}")
            try:
                # Leemos las primeras 5 filas del archivo para determinar su tipo.
                df = pd.read_excel(os.path.join(path, file), nrows=5)
                # Dependiendo del contenido, renombramos el archivo.
                if 'Gestión Pedidos/Reposición de Stock' in df.to_string():
                    new_name = f'{current_user_id}-{proveedor.nombre}-stock.xls'
                    # ...
                elif 'Articulos' in df.to_string():
                    new_name = f'{current_user_id}-{proveedor.nombre}-precios.xls'
                    # ...
                else:
                    new_name = f'{current_user_id}-{proveedor.nombre}-proveedor.xls'
                    # ...
                # Renombramos el archivo.
                os.rename(os.path.join(path, file), os.path.join(path, new_name))
                print(f"Archivo renombrado a: {new_name}")
            except Exception as e:
                print("Error en rename_files:")
                traceback.print_exc()

def leer_archivo(filename, skiprows=0, sku_as_str=False):
    """
    Leer un archivo CSV, XLS o XLSX y devuelve un DataFrame.
    La función detecta automáticamente el tipo de archivo y realiza la lectura correspondiente.
    """
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filename, encoding='ISO-8859-1', sep=';', skiprows=skiprows)
        elif filename.endswith('.xls'):
            if sku_as_str:
                df = pd.read_excel(filename, skiprows=skiprows, converters={2: str})
            else:
                df = pd.read_excel(filename, skiprows=skiprows)
            new_filename = filename[:-4] + '.xlsx'  # Crear el nombre del nuevo archivo
            df.to_excel(new_filename, index=False)  # Guardar el DataFrame como .xlsx
            os.remove(filename)  # Eliminar el archivo .xls original
            filename = new_filename  # Actualizar el nombre del archivo para las operaciones siguientes
        elif filename.endswith('.xlsx'):
            if sku_as_str:
                df = pd.read_excel(filename, skiprows=skiprows, converters={2: str})
            else:
                df = pd.read_excel(filename, skiprows=skiprows)
        else:
            print(f"Formato de archivo no soportado: {filename}")
            return None
    except pd.errors.EmptyDataError:
        print(f"El archivo está vacío: {filename}")
        return None
    except FileNotFoundError:
        print(f"El archivo no existe: {filename}")
        return None
    except Exception as e:
        print(f"Error al leer el archivo: {filename}, {str(e)}")
        return None
    
    return df, filename  # Devolver el DataFrame y el nombre del archivo




def eliminar_formas_no_imagenes(filename):
    wb = openpyxl.load_workbook(filename)
    ws = wb.active
    try:
        for shape in ws._shapes:
            if not isinstance(shape, openpyxl.drawing.image.Image):
                ws.remove_shape(shape)
    except AttributeError:
        for image in ws._images:
            ws.remove_image(image)
    wb.save(filename)

def filtrar_y_reformatear_mg_precio(df):
    """Filtrar y reformatear un DataFrame"""
    df = df.iloc[3:]
    df.columns = ['Codigo', 'Nombre', 'SKU', 'Descuento', 'Descuento 2', 'Descuento 3', 'Precio', 'Vendible']
    df = df[['Codigo', 'Nombre', 'SKU', 'Descuento','Descuento 2', 'Descuento 3', 'Precio','Vendible']]
    
    # Convierte la columna 'SKU' a string
    df['SKU'] = df['SKU'].apply(lambda x: '{:.0f}'.format(float(x.replace(" ", ""))) if pd.notnull(x) else 'NaN')
    return df


def filtrar_y_reformatear_mg_stock(df):
    """Filtrar y reformatear un DataFrame"""
    df = df.iloc[3:]
    df.columns = ['Codigo', 'Nombre', 'Stock Actual', 'Stock Max', 'Pto. Repos.']
    df = df[['Codigo', 'Nombre', 'Stock Actual', 'Stock Max', 'Pto. Repos.']]
    return df

from fuzzywuzzy import fuzz
import pandas as pd

def combine_dataframes(df1, df2):
    df2.columns = [col + '_df2' if col in df1.columns else col for col in df2.columns]
    rows_list = []
    
    for i, row1 in df1.iterrows():
        for j, row2 in df2.iterrows():
            similarity = fuzz.token_set_ratio(row1['Codigo'], row2['Codigo_df2'])  # Aquí cambiamos 'Codigo' a 'Codigo_df2'
            if similarity >= 94:
                combined_row = pd.concat([row1, row2])
                rows_list.append(combined_row)
                break
        else:
            rows_list.append(row1)
    
    for i, row2 in df2.iterrows():
        if not any(fuzz.token_set_ratio(row2['Codigo_df2'], row1['Codigo']) >= 94 for _, row1 in df1.iterrows()):  # Aquí también cambiamos 'Codigo' a 'Codigo_df2'
            rows_list.append(row2)
    
    result_df = pd.DataFrame(rows_list)
    return result_df

def combine_dataframes_sku(df1, df2):
    df2.columns = [col + '_p' if col in df1.columns else col for col in df2.columns]
    rows_list = []
    
    for i, row1 in df1.iterrows():
        for j, row2 in df2.iterrows():
            similarity = fuzz.token_set_ratio(row1['SKU'], row2['SKU_p'])
            if similarity >= 94:
                combined_row = pd.concat([row1, row2])
                rows_list.append(combined_row)
                break
        else:
            rows_list.append(row1)
    
    for i, row2 in df2.iterrows():
        if not any(fuzz.token_set_ratio(row2['SKU_p'], row1['SKU']) >= 94 for _, row1 in df1.iterrows()):
            rows_list.append(row2)
    
    result_df = pd.DataFrame(rows_list)
    return result_df




def process_files(current_user_id, proveedor, path):
    # 1. Renombrar archivos
    rename_files(current_user_id, proveedor, path)
    
    # Inicializar los dataframes como None
    df_precios = None
    df_stock = None
    df_proveedor = None  # Añadido

    # Leer y procesar los archivos
    files = os.listdir(path)
    print(f"Lista de archivos después de renombrar: {files}")  # Añade esta línea

    for file in files:
        if file.endswith('.xls') or file.endswith('.xlsx'):
            print(f"Procesando archivo: {file}")
            try:
                if 'stock' in file or 'precios' in file:
                    df, filename = leer_archivo(os.path.join(path, file), skiprows=3, sku_as_str='precios' in file)
                else:
                    df, filename = leer_archivo(os.path.join(path, file))

                # 3. Eliminar formas no imágenes
                eliminar_formas_no_imagenes(filename)

                print(f"Nombre de archivo después de leer y eliminar formas no imágenes: {filename}")  # Añade esta línea

                # 4. Filtrar y reformatear el DataFrame
                if '-precios.xlsx' in os.path.basename(filename):
                    df_precios = filtrar_y_reformatear_mg_precio(df)
                    df_precios.to_excel(filename, index=False)
                elif '-stock.xlsx' in os.path.basename(filename):
                    df_stock = filtrar_y_reformatear_mg_stock(df)
                    df_stock.to_excel(filename, index=False)

                # Procesar archivos de proveedor
                if '-proveedor.xlsx' in os.path.basename(filename):
                    # Importar el script del proveedor
                    script_proveedor = importlib.import_module(f'proveedores.{current_user_id}.{proveedor.id}')

                    # Añade la impresión del DataFrame aquí antes de la llamada a process_proveedor_file
                    print(f"DataFrame antes de process_proveedor_file para el archivo {files}:")
                    print(df)

                    # Llamar a la función process_proveedor_file en el script del proveedor
                    df_proveedor = script_proveedor.process_proveedor_file(df)  # Cambiado a df_proveedor

                    # Añade la impresión del DataFrame aquí
                    print(f"DataFrame después de process_proveedor_file para el archivo {files}:")
                    print(df_proveedor)
                    df_proveedor.to_excel(filename, index=False)  # Cambiado a df_proveedor
            except Exception as e:
                print(f"Error al procesar el archivo {file}:")
                traceback.print_exc()

    # Combinar los dataframes de precios y stock
    if df_precios is not None and df_stock is not None:
        df_combined = combine_dataframes(df_precios, df_stock)
        df_combined.to_excel(os.path.join(path, "combined.xlsx"), index=False)
    else:
        print("No se encontraron los archivos de precios y stock.")

    # Combinar el dataframe combinado con el dataframe de proveedor
    if df_combined is not None and df_proveedor is not None:
        df_final = combine_dataframes_sku(df_combined, df_proveedor)
        df_final.to_excel(os.path.join(path, "final.xlsx"), index=False)
    else:
        print("No se encontraron los archivos combinados y de proveedor.")
