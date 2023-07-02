import os
import pandas as pd
import openpyxl
import pandas as pd

def leer_archivo(filename):
    """
    Leer un archivo CSV o de Excel y devuelve un DataFrame.
    La función detecta automáticamente el tipo de archivo y realiza la lectura correspondiente.
    """
    try:
        df = pd.read_csv(filename, encoding='ISO-8859-1', sep=';')
    except pd.errors.EmptyDataError:
        try:
            df = pd.read_excel(filename)
        except FileNotFoundError:
            print("El archivo no existe.")
            return None
        except Exception as e:
            print(f"Error al leer el archivo de Excel: {str(e)}")
            return None
    except Exception as e:
        print(f"Error al leer el archivo CSV: {str(e)}")
        return None
    
    return df

def eliminar_formas_no_imagenes(filename):
    """Elimina las formas que no son imágenes en la hoja de cálculo"""
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

def guardar_archivo(df, filename, new_filename=None):
    """Guarda un DataFrame modificado en un nuevo archivo de Excel"""
    processed_dir = "./procesados/procesadosCanal"
    os.makedirs(processed_dir, exist_ok=True)  # crea la carpeta si no existe
    
    if new_filename is None:
        new_filename = os.path.splitext(os.path.basename(filename))[0] + '.xlsx'
    else:
        new_filename = new_filename + '.xlsx'
        
    processed_filename = os.path.join(processed_dir, new_filename)
    df.to_excel(processed_filename, index=False)
    print('Archivo limpio guardado como', processed_filename)

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

def clean_canal(filename, new_filename=None, mpn_value=None):
    df = leer_archivo(filename)
    df = filtrar_y_reformatear_canal(df, mpn_value)
    guardar_archivo(df, filename, new_filename)

def filtrar_y_reformatear_algabo(df):
    """Filtrar y reformatear un DataFrame de Excel"""
    df = df.drop(index=range(16))
    df = df.rename(columns={
        df.columns[1]: 'SKU',
        df.columns[2]: 'Código de barras',
        df.columns[5]: 'Nombre',
        df.columns[26]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]

    # Continua el proceso de limpieza...
    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 1]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(int).astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace(r'[.+\-E]', '', regex=True)
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    # Separar la columna SKU en dos columnas
    df["SKU"] = df["SKU"].astype(str)
    df[["num", "SKU_letra"]] = df["SKU"].str.extract(r"(\d+)(\D*)")

    # Convertir la columna SKU_numero a números
    df["num"] = pd.to_numeric(df["num"], errors="coerce")

    # Ordenar por SKU_numero de forma ascendente
    df = df.sort_values(by='num')

    # Concatenar SKU_numero y SKU_letra dentro de SKU_numero
    df['SKU'] =df['num'].astype(str) + df['SKU_letra']
    df = df.drop(columns=['num', 'SKU_letra'])

    # Aplicar un 15% de descuento a la columna Costo
    df['Costo'] = df['Costo'] * 0.85

    # Aplicar un 21% de aumento a la columna Costo
    df['Costo'] = df['Costo'] * 1.21
    
    return df

def clean_algabo(filename, new_filename=None):
    df = leer_archivo(filename)
    df = filtrar_y_reformatear_algabo(df)
    guardar_archivo(df, filename, new_filename)
    eliminar_formas_no_imagenes(filename)

def filtrar_y_reformatear_furey(df):
    """Filtrar y reformatear un DataFrame de Excel para Furey"""
    df = df.drop(index=range(6))
    df = df.rename(columns={
        df.columns[0]: 'SKU',
        df.columns[1]: 'Código de barras',
        df.columns[2]: 'Nombre',
        df.columns[3]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]

    # Continua el proceso de limpieza...
    # ...
    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 0]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace(r'[.+\-E]', '', regex=True)
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    # Separar la columna SKU en dos columnas
    df["SKU"] = df["SKU"].astype(str)
    df[["num", "SKU_letra"]] = df["SKU"].str.extract(r"(\d+)(\D*)")

    # Convertir la columna SKU_numero a números
    df["num"] = pd.to_numeric(df["num"], errors="coerce")

    # Ordenar por SKU_numero de forma ascendente
    df = df.sort_values(by='num')

    # Concatenar SKU_numero y SKU_letra dentro de SKU_numero
    df['SKU'] =df['num'].astype(str) + df['SKU_letra']
    df = df.drop(columns=['num', 'SKU_letra'])
    df['Costo'] = df['Costo'].astype(str)
    df['Costo'] = df['Costo'].str.replace(',', '').str.replace('\..*', '', regex=True)

    # DESCUENTOS 
    df['Costo'] = pd.to_numeric(df['Costo'])
    df['Costo'] = df['Costo'].apply(lambda x: round(x*0.83))
    return df

def clean_furey(filename, new_filename=None):
    df = leer_archivo(filename)
    df = filtrar_y_reformatear_furey(df)
    guardar_archivo(df, filename, new_filename)
    eliminar_formas_no_imagenes(filename)


def filtrar_y_reformatear_teddy(df):
    """Filtrar y reformatear un DataFrame de Excel para Teddy"""
    df = df.drop(index=range(19))
    df = df.rename(columns={
        df.columns[1]: 'SKU',
        df.columns[2]: 'Código de barras',
        df.columns[3]: 'Nombre',
        df.columns[4]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]

    # Continua el proceso de limpieza...
    # ...
    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 1]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(int).astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace(r'[.+\-E]', '', regex=True)
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    # Convertir la columna SKU_numero a números
    df["SKU"] = pd.to_numeric(df["SKU"], errors="coerce")

    # Ordenar por SKU_numero de forma ascendente
    df = df.sort_values(by='SKU')


    df['Costo'] = df['Costo'].replace(',', '', regex=True)

    # Limpiar los valores de la columna "Costo"
    df['Costo'] = df['Costo'].fillna(0).apply(lambda x: int(float(str(x).split('.')[0])))
    return df

def clean_teddy(filename, new_filename=None):
    df = leer_archivo(filename)
    df = filtrar_y_reformatear_teddy(df)
    guardar_archivo(df, filename, new_filename)
    eliminar_formas_no_imagenes(filename)

def filtrar_y_reformatear_upalala(df):
    """Filtrar y reformatear un DataFrame de Excel para Upalala"""
    df = df.drop(index=range(0))
    df = df.rename(columns={
        df.columns[2]: 'SKU',
        df.columns[0]: 'Código de barras',
        df.columns[3]: 'Nombre',
        df.columns[4]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]

    # Continua el proceso de limpieza...
    # ...
    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 1]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(int).astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace(r'[.+\-E]', '', regex=True)
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    df['Costo'] = df['Costo'].astype(str).str.split('.', n=1, expand=True)[0]

    return df

def clean_upalala(filename, new_filename=None):
    df = leer_archivo(filename)
    df = filtrar_y_reformatear_upalala(df)
    guardar_archivo(df, filename, new_filename)
    eliminar_formas_no_imagenes(filename)

