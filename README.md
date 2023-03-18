This Python script includes three functions to clean and manipulate data from different sources.

clean_canal
This function takes a CSV file as input and cleans it by selecting specific columns, filtering by a given value in the MPN column, cleaning and formatting the Price and SKU columns, and concatenating the SKU_num and SKU_letra columns into a new SKU_numero column. Finally, it saves the cleaned data in an Excel file in the "procesadosCanal" folder.

Parameters
filename: The name of the CSV file to be cleaned.
new_filename: The name of the new Excel file to be saved. If not provided, the name will be the same as the original CSV file but with an Excel extension.
mpn_value: The value to filter the MPN column by.
concat
This function takes two Excel files as input and concatenates them based on the similarity of the SKU column. The resulting file includes information from both input files, as well as a similarity score calculated using the fuzzywuzzy library. The function saves the concatenated data in a new Excel file.

Parameters
archivo1: The name of the first Excel file to be concatenated.
archivo2: The name of the second Excel file to be concatenated.
archivo_resultado: The name of the new Excel file to be saved.
clean_algabo
This function takes an Excel file as input and cleans it by selecting specific columns, removing rows without a code associated, cleaning and formatting the Código de barras column, and concatenating the num and SKU_letra columns into a new SKU column. The function also applies a 15% discount and a 21% increase to the Costo column. Finally, it saves the cleaned data in an Excel file in the "procesados" folder and removes any non-image shapes from the file.

Parameters
filename: The name of the Excel file to be cleaned.
new_filename: The name of the new Excel file to be saved. If not provided, the name will be the same as the original file.


Función clean_furey
Esta función recibe como entrada el nombre de un archivo Excel y opcionalmente un nuevo nombre para el archivo procesado. La función carga el archivo Excel usando la librería Pandas y realiza una serie de operaciones de limpieza y transformación de los datos:

Elimina las primeras 6 filas del archivo.
Renombra las columnas SKU, Código de barras, Nombre y Costo.
Elimina las filas que no tienen un código de barras asociado.
Limpia el campo Código de barras eliminando los caracteres ".", "+", "E" y "-" y luego rellena el número con ceros a la izquierda hasta completar 13 caracteres.
Divide la columna SKU en dos columnas: una con el número y otra con las letras.
Convierte la columna SKU número en tipo numérico y la ordena de forma ascendente.
Concatena la columna SKU número y SKU letra en la columna SKU número.
Convierte la columna Costo en tipo string y elimina la coma y cualquier dígito después del punto.
Guarda el archivo procesado en la carpeta "procesados".
Elimina las formas que no son imágenes del archivo procesado.
Función clean_teddy
Esta función recibe como entrada el nombre de un archivo Excel y opcionalmente un nuevo nombre para el archivo procesado. La función carga el archivo Excel usando la librería Pandas y realiza una serie de operaciones de limpieza y transformación de los datos:

Elimina las primeras 19 filas del archivo.
Renombra las columnas SKU, Código de barras, Nombre y Costo.
Elimina las filas que no tienen un código de barras asociado.
Limpia el campo Código de barras eliminando los caracteres ".", "+", "E" y "-" y luego rellena el número con ceros a la izquierda hasta completar 13 caracteres.
Convierte la columna SKU en tipo numérico y la ordena de forma ascendente.
Elimina las comas de la columna Costo.
Limpia los valores de la columna Costo para dejar únicamente el número entero.
Guarda el archivo procesado en la carpeta "procesados".
Elimina las formas que no son imágenes del archivo procesado.
Función scrape_drimel
Esta función recibe como entrada una lista de URLs de la tienda en línea Drimel. La función realiza una petición HTTP a cada URL, extrae la información de los productos de la página y la guarda en un DataFrame de Pandas. Luego realiza una serie de operaciones de limpieza y transformación de los datos:

Filtra los productos que no contienen ninguna de las marcas especificadas en la lista marcas.
Limpia el campo price eliminando el signo "$", las comillas, el punto y cualquier dígito después de la coma.
Convierte el campo product_id en tipo entero y lo usa como SKU.
Limpia el campo Costo para dejar únicamente el número entero.
Renombra las columnas name, price, product_id, product_sku, url_id y marca a Nombre, Costo, SKU, Código de barras, `Identificador de