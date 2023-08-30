# userscripts/common_utils.py
import os
import openpyxl
import traceback
#

def eliminar_formas_no_imagenes(filename):
    ext = os.path.splitext(filename)[1]
    if ext not in ['.xlsx', '.xlsm']:
        print(f"Omitiendo {filename}, ya que no es un archivo Excel soportado.")
        return
    
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

#

def adjust_columns_and_center_text(path):
    try:
        # Obtenemos la lista de archivos en el directorio
        files = os.listdir(path)
        print(f"Archivos en el directorio {path}: {files}")

        for file in files:
            # Procesamos solo los archivos .xlsx
            if file.endswith('.xlsx'):
                print(f"Procesando archivo: {file}")
                try:
                    # Abrimos el archivo usando openpyxl
                    workbook = openpyxl.load_workbook(os.path.join(path, file))

                    # Iteramos a través de todas las hojas en el archivo
                    for sheet_name in workbook.sheetnames:
                        sheet = workbook[sheet_name]

                        # Iteramos a través de todas las columnas en la hoja
                        for col in sheet.columns:
                            max_length = 0
                            column = col[0].column_letter  # Obtenemos la letra de la columna

                            # Encontramos el máximo ancho de la columna
                            for cell in col:
                                try:
                                    max_length = max(max_length, len(str(cell.value)))
                                    # Centramos el texto en la celda
                                    cell.alignment = openpyxl.styles.Alignment(horizontal='center')
                                except:
                                    print("Error al ajustar celda:", cell)
                                    pass

                            # Ajustamos el ancho de la columna
                            adjusted_width = (max_length + 2)
                            sheet.column_dimensions[column].width = adjusted_width

                    # Guardamos los cambios en el archivo
                    workbook.save(os.path.join(path, file))
                    print(f"Archivo ajustado y centrado: {file}")
                except Exception as e:
                    print("Error en el archivo:", file)
                    traceback.print_exc()
    except Exception as e:
        print("Error en adjust_columns_and_center_text:")
        traceback.print_exc()