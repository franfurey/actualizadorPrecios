import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import os

def extract_df2_only(df_result):
    df2_only = df_result[df_result['Identificador de URL'].isna() & df_result['df2_Nombre'].notna()]
    df2_only = df2_only[['df2_Nombre', 'df2_SKU', 'df2_Código de barras', 'df2_Costo']]
    return df2_only


def save_filtered_df(df, proveedor, increase_percentage):
    filename = f'./listos/tiendaNube/{proveedor}'

    # Filtrar las filas con un aumento
    increased_df = df[df['Porcentaje de aumento'] > 0].copy()

    # Calcular el nuevo precio
    increased_df.loc[:, 'Precio'] = increased_df['df2_Costo'] * (1 + increase_percentage / 100)

    # Redondear y convertir a entero los valores de la columna 'Precio'
    increased_df.loc[:, 'Precio'] = increased_df['Precio'].round().astype(int)

    # Seleccionar las columnas deseadas
    columns = ['Identificador de URL', 'df2_Costo', 'Precio', 'Porcentaje de aumento']
    filtered_df = increased_df[columns]

    # Guardar el DataFrame en un nuevo archivo de Excel
    save_dataframe_to_excel_with_adjusted_columns(filtered_df, filename + '.xlsx')

    # Preparar el DataFrame para el archivo CSV: eliminar la columna 'Porcentaje de aumento' y renombrar 'df2_Costo' a 'Costo'
    csv_df = filtered_df.drop(columns='Porcentaje de aumento')
    csv_df = csv_df.rename(columns={'df2_Costo': 'Costo'})

    # Guardar el DataFrame en un nuevo archivo CSV
    csv_file = filename + '.csv'
    csv_df.to_csv(csv_file, index=False)

    # Imprimir la ruta absoluta del archivo CSV
    print("El archivo CSV se ha guardado en: " + os.path.abspath(csv_file))





def save_dataframe_to_excel_with_adjusted_columns(dataframe, file_path):
    # Crear un nuevo libro de trabajo de openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active

    # Convertir el DataFrame en filas de openpyxl y agregarlas a la hoja de trabajo
    for r in dataframe_to_rows(dataframe, index=False, header=True):
        ws.append(r)

    # Centrar el texto y ajustar el ancho de las columnas según el contenido
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Obtener la letra de la columna
        for cell in col:
            # Centrar el texto de todas las celdas, incluidos los encabezados
            cell.alignment = openpyxl.styles.Alignment(horizontal='center')
            max_length = max(max_length, len(str(cell.value)))

        # Cambiar el formato de la celda del encabezado
        col[0].font = openpyxl.styles.Font(bold=True)

        # Ajustar el ancho de la columna
        adjusted_width = max_length + 1
        ws.column_dimensions[column].width = adjusted_width

    # Guardar el libro de trabajo en el archivo de Excel
    wb.save(file_path)