import os
import pandas as pd
import openpyxl



current_user = 'drogueriamg'
proveedor_id = 1

def rename_files(path):
    files = os.listdir(path)

    for file in files:
        if file.endswith('.xls') or file.endswith('.xlsx'):
            try:
                df = pd.read_excel(os.path.join(path, file), nrows=5)
                if 'Gestión Pedidos/Reposición de Stock' in df.to_string():
                    new_name = f'{current_user}-{proveedor_id}-stock.xls'
                    os.rename(os.path.join(path, file), os.path.join(path, new_name))
                elif 'Articulos' in df.to_string():
                    new_name = f'{current_user}-{proveedor_id}-precios.xls'
                    os.rename(os.path.join(path, file), os.path.join(path, new_name))
                else:
                    new_name = f'{current_user}-{proveedor_id}-proveedor.xls'
                    os.rename(os.path.join(path, file), os.path.join(path, new_name))
            except Exception as e:
                print(f"Error al leer o renombrar el archivo: {file}, {str(e)}")

def leer_archivo(filename):
    """
    Leer un archivo CSV, XLS o XLSX y devuelve un DataFrame.
    La función detecta automáticamente el tipo de archivo y realiza la lectura correspondiente.
    """
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filename, encoding='ISO-8859-1', sep=';')
        elif filename.endswith('.xls'):
            df = pd.read_excel(filename)
            new_filename = filename[:-4] + '.xlsx'  # Crear el nombre del nuevo archivo
            df.to_excel(new_filename, index=False)  # Guardar el DataFrame como .xlsx
            filename = new_filename  # Actualizar el nombre del archivo para las operaciones siguientes
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filename)
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

def filtrar_y_reformatear_mg_sin_cod(df):
    """Filtrar y reformatear un DataFrame"""
    # Supongamos que tu DataFrame se llama df
    df = df.drop(index=range(3))
    df = df.rename(columns={
        df.columns[0]: 'Codigo',
        df.columns[1]: 'Nombre',
        df.columns[2]: 'Stock Actual',
        df.columns[3]: 'Stock Max',
        df.columns[4]: 'Pto. Repos.'
    })
    df = df[['Codigo', 'Nombre', 'Stock ACtual',
             'Stock Max', 'Pto. Repos.']]

    return df