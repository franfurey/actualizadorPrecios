import os
from data_saving import save_dataframe_to_excel_with_adjusted_columns, extract_df2_only, save_filtered_df, crear_directorios_y_rutas
from data_loading import load_and_prepare_dataframes
from data_processing import calculate_similarity, add_non_matching_rows
from analysis import prepare_result, generate_report


increase_percentage_dict = {
    'algabo': 20,
    'furey': 20,
    'teddy': 10,
    'drimel': 12,
    'upalala': 25
    # Agrega más proveedores y porcentajes aquí...
}

def concat(proveedor):
    archivo1, archivo2, archivo_resultado, archivo_tiendaNube = crear_directorios_y_rutas(proveedor)

    df1, df2 = load_and_prepare_dataframes(archivo1, archivo2)
    df_result = calculate_similarity(df1, df2)
    df_result = add_non_matching_rows(df_result, df2)
    df_result = prepare_result(df_result)

    # Extraer filas de df2 que no están en df1
    df2_only = extract_df2_only(df_result)

    # Guarda df_result y df2_only
    save_dataframe_to_excel_with_adjusted_columns(df_result, archivo_resultado)
    save_dataframe_to_excel_with_adjusted_columns(df2_only, f'proveedor/{proveedor}/listos/nuevos/{proveedor}_only.xlsx')

    # Generar y mostrar estadísticas.
    generate_report(df_result, archivo_resultado)
    
    # Obtén el porcentaje de aumento para este proveedor del diccionario
    increase_percentage = increase_percentage_dict.get(proveedor, 0)

    # Llamar a save_filtered_df con la ruta correcta
    save_filtered_df(df_result, archivo_tiendaNube, increase_percentage)

    return df_result