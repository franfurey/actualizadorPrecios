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