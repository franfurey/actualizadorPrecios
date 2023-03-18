import os
import pandas as pd
import openpyxl
from fuzzywuzzy import fuzz

def clean_canal(filename, new_filename=None,  mpn_value=None):
    # Cargar el archivo de CSV
    df = pd.read_csv(filename)

    df = df[['Identificador de URL', 'Nombre', 'Precio',
              'SKU','Código de barras','MPN (Número de pieza del fabricante)','Costo']]

    # Filtrar por valor específico en la columna MPN
    if mpn_value is not None:
        df = df[df['MPN (Número de pieza del fabricante)'] == mpn_value]

  # Limpiar la columna Precio
    df['Precio'] = df['Precio'].str.replace('\..*', '').str.replace(',', '')
    df['Precio'] = pd.to_numeric(df['Precio'])

    # Separar la columna SKU en dos columnas
    df[['SKU_palabra', 'SKU_num']] = df['SKU'].str.split('-', expand=True)

    # Separar la columna SKU en dos columnas
    df["SKU_num"] = df["SKU_num"].astype(str)
    df[["num", "SKU_letra"]] = df["SKU_num"].str.extract(r"(\d+)(\D*)")

    # Convertir la columna SKU_numero a números
    df["num"] = pd.to_numeric(df["num"], errors="coerce")

    # Ordenar por SKU_numero de forma ascendente
    df = df.sort_values(by='num')

    # Concatenar SKU_numero y SKU_letra dentro de SKU_numero
    df['SKU_numero'] =df['num'].astype(str) + df['SKU_letra']

    # Eliminar la columna SKU_letra
    df.drop(['SKU_letra','SKU','SKU_letra','SKU_num','num','SKU_palabra'], axis=1, inplace=True)
    df = df.rename(columns={'SKU_numero': 'SKU'})

    # Guardar el archivo de Excel modificado en la carpeta "procesados"
    processed_dir = "./procesadosCanal"
    os.makedirs(processed_dir, exist_ok=True)  # crea la carpeta si no existe
    
    if new_filename is None:
        new_filename = os.path.splitext(os.path.basename(filename))[0] + '.xlsx'
    else:
        new_filename = new_filename + '.xlsx'
        
    processed_filename = os.path.join(processed_dir, new_filename)
    df.to_excel(processed_filename, index=False)
    
    print('Archivo limpio guardado como', processed_filename)


def concat(archivo1, archivo2, archivo_resultado):
    # Cargar los dos archivos de Excel
    df1 = pd.read_excel(archivo1)
    df2 = pd.read_excel(archivo2)
    df1['Código de barras'] = df1['Código de barras'].astype(str)
    #
    df2['Código de barras'] = df2['Código de barras'].astype(str)

    df_result = pd.DataFrame(columns=['Identificador de URL','canal_Nombre','canal_Precio','canal_SKU','canal_Código de barras','Costo',
                                      'df2_SKU','df2_Nombre','df2_Código de barras','df2_Precio','similarity'])


    for i, row1 in df1.iterrows():
        canal_Nombre = row1['Nombre']
        canal_Precio = row1['Precio']
        canal_SKU = row1['SKU']
        canal_Codigo = row1['Código de barras']
        canal_Identificador = row1['Identificador de URL']
        canal_costo = row1['Costo']
        found = False

        for j, row2 in df2.iterrows():
            df2_Nombre = row2['Nombre']
            df2_Precio = row2['Precio']
            df2_SKU = row2['SKU']
            df2_Codigo = row2['Código de barras']

            similarity = fuzz.token_set_ratio(canal_SKU, df2_SKU)

            if similarity >= 99:
                df_result.loc[len(df_result)] = [canal_Identificador, canal_Nombre, canal_Precio, canal_SKU, canal_Codigo, canal_costo,
                                                  df2_SKU, df2_Nombre, df2_Codigo, df2_Precio, similarity]
                found = True

        if not found:
            df_result.loc[len(df_result)] = [canal_Identificador, canal_Nombre, canal_Precio, canal_SKU, canal_Codigo, canal_costo, 
                                             None, None, None, None, None]

    for i, row2 in df2.iterrows():
        df2_Nombre = row2['Nombre']
        df2_Precio = row2['Precio']
        df2_SKU = row2['SKU']
        df2_Codigo = row2['Código de barras']
        found = False

        for j, row_result in df_result.iterrows():
            if row_result['df2_SKU'] == df2_SKU:
                found = True
                break
        
        if not found:
            df_result.loc[len(df_result)] = [None, None, None, None, None,None, 
                                             df2_SKU, df2_Nombre, df2_Codigo, df2_Precio, None]
            
    df_result.to_excel(archivo_resultado, index= False, float_format = '%.15g')
    print("Archivo CONCATENADO guardado como",archivo_resultado)


def clean_algabo(filename, new_filename=None):
    # Cargar el archivo de Excel
    df = pd.read_excel(filename)
    df = df.drop(index=range(16))

    df = df.rename(columns={
        df.columns[1]: 'SKU',
        df.columns[2]: 'Código de barras',
        df.columns[5]: 'Nombre',
        df.columns[26]: 'Costo'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Costo']]

    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 1]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(int).astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace('.', '').str.replace('+', '').str.replace('E', '').str.replace('-', '')
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

    # Guardar el archivo de Excel modificado en la carpeta "procesados"
    processed_dir = os.path.join(os.path.dirname(filename), "./procesados/")
    os.makedirs(processed_dir, exist_ok=True)  # crea la carpeta si no existe
    
    if new_filename is None:
        new_filename = os.path.basename(filename)
    else:
        _, file_extension = os.path.splitext(filename)
        new_filename = new_filename + file_extension
        
    processed_filename = os.path.join(processed_dir, new_filename)
    df.to_excel(processed_filename, index=False)

    print('Archivo limpio guardado como', processed_filename)

    # Eliminar las formas que no son imágenes
    wb = openpyxl.load_workbook(processed_filename)
    ws = wb.active

    # Iterar sobre todas las formas en la hoja de cálculo
    try:
        # Iterar sobre todas las formas en la hoja de cálculo
        for shape in ws._shapes:
            # Eliminar la forma si no es un gráfico
            if not isinstance(shape, openpyxl.drawing.image.Image):
                ws.remove_shape(shape)
    except AttributeError:
        # Si no se puede acceder a _shapes, usar _images en su lugar
        for image in ws._images:
            # Eliminar la imagen
            ws.remove_image(image)

    wb.save(processed_filename)


def clean_furey(filename, new_filename=None):
    # Cargar el archivo de Excel
    df = pd.read_excel(filename, dtype={'Código de barras': str})
    df = df.drop(index=range(6))

    df = df.rename(columns={
        df.columns[0]: 'SKU',
        df.columns[1]: 'Código de barras',
        df.columns[2]: 'Nombre',
        df.columns[3]: 'Precio'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Precio']]

    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 0]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace('.', '').str.replace('+', '').str.replace('E', '').str.replace('-', '')
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
    df['Precio'] = df['Precio'].astype(str)
    df['Precio'] = df['Precio'].str.replace(',', '').str.replace('\..*', '', regex=True)

    # Guardar el archivo de Excel modificado en la carpeta "procesados"
    processed_dir = "./procesados"
    os.makedirs(processed_dir, exist_ok=True)  # crea la carpeta si no existe
    
    if new_filename is None:
        new_filename = os.path.basename(filename)
    else:
        _, file_extension = os.path.splitext(filename)
        new_filename = new_filename + file_extension
        
    processed_filename = os.path.join(processed_dir, new_filename)
    df.to_excel(processed_filename, index=False)

    print('Archivo limpio guardado como', processed_filename)

    # Eliminar las formas que no son imágenes
    wb = openpyxl.load_workbook(processed_filename)
    ws = wb.active

    # Iterar sobre todas las formas en la hoja de cálculo
    try:
        # Iterar sobre todas las formas en la hoja de cálculo
        for shape in ws._shapes:
            # Eliminar la forma si no es un gráfico
            if not isinstance(shape, openpyxl.drawing.image.Image):
                ws.remove_shape(shape)
    except AttributeError:
        # Si no se puede acceder a _shapes, usar _images en su lugar
        for image in ws._images:
            # Eliminar la imagen
            ws.remove_image(image)

    wb.save(processed_filename)


def clean_teddy(filename, new_filename=None):
    # Cargar el archivo de Excel
    df = pd.read_excel(filename)


    df = df.drop(index=range(19))

    df = df.rename(columns={
        df.columns[1]: 'SKU',
        df.columns[2]: 'Código de barras',
        df.columns[3]: 'Nombre',
        df.columns[4]: 'Precio'
    })
    df = df[['SKU', 'Código de barras', 'Nombre', 'Precio']]

    # Eliminar filas sin un código asociado
    columna = df.iloc[:, 1]
    df = df.dropna(subset=[df.columns[1]])
    df['Código de barras'] = df['Código de barras'].astype(int).astype(str)
    df['Código de barras'] = df['Código de barras'].str.replace('.', '').str.replace('+', '').str.replace('E', '').str.replace('-', '')
    df['Código de barras'] = df['Código de barras'].str.zfill(13)

    # Convertir la columna SKU_numero a números
    df["SKU"] = pd.to_numeric(df["SKU"], errors="coerce")

    # Ordenar por SKU_numero de forma ascendente
    df = df.sort_values(by='SKU')


    df['Precio'] = df['Precio'].replace(',', '', regex=True)

    # Limpiar los valores de la columna "Precio"
    df['Precio'] = df['Precio'].apply(lambda x: int(float(str(x).split('.')[0])))

    # Guardar el archivo de Excel modificado en la carpeta "procesados"
    processed_dir = os.path.join(os.path.dirname(filename), "./procesados/")
    os.makedirs(processed_dir, exist_ok=True)  # crea la carpeta si no existe
    
    if new_filename is None:
        new_filename = os.path.basename(filename)
    else:
        _, file_extension = os.path.splitext(filename)
        new_filename = new_filename + file_extension
        
    processed_filename = os.path.join(processed_dir, new_filename)
    df.to_excel(processed_filename, index=False)

    print('Archivo limpio guardado como', processed_filename)

    # Eliminar las formas que no son imágenes
    wb = openpyxl.load_workbook(processed_filename)
    ws = wb.active

    # Iterar sobre todas las formas en la hoja de cálculo
    try:
        # Iterar sobre todas las formas en la hoja de cálculo
        for shape in ws._shapes:
            # Eliminar la forma si no es un gráfico
            if not isinstance(shape, openpyxl.drawing.image.Image):
                ws.remove_shape(shape)
    except AttributeError:
        # Si no se puede acceder a _shapes, usar _images en su lugar
        for image in ws._images:
            # Eliminar la imagen
            ws.remove_image(image)

            #

    wb.save(processed_filename)
    print('Imágenes eliminadas del archivo', processed_filename)