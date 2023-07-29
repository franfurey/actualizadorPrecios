# Este es el archivo proveesync.py

import os
import pandas as pd
import openpyxl
import pandas as pd

def leer_archivo(filename):
    """
    Leer un archivo CSV, XLS o XLSX y devuelve un DataFrame.
    La función detecta automáticamente el tipo de archivo y realiza la lectura correspondiente.
    """
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filename, encoding='ISO-8859-1', sep=';')
        elif filename.endswith(('.xls', '.xlsx')):
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
    
    return df


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