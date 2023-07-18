import pandas as pd

def prepare_result(df_result):
    df_result = df_result[['Identificador de URL', 'canal_Nombre', 'df2_Nombre', 'Marca',
                            'canal_SKU', 'df2_SKU', 
                           'canal_Código de barras', 'df2_Código de barras',
                            'canal_Costo', 'df2_Costo', 'Precio', 'similarity',
                           'canal_Categorías','canal_Tags','canal_Título para SEO',
                           'canal_Descripción para SEO','canal_Marca','canal_Descripción']]
    df_result[['canal_Costo', 'df2_Costo']] = df_result[['canal_Costo', 'df2_Costo']].apply(
        lambda x: pd.to_numeric(x.astype(str).str.replace(',', ''), errors='coerce')
    )
    df_result['df2_Costo'] = df_result['df2_Costo'].round()
    df_result['Porcentaje de aumento'] = ((df_result['df2_Costo'] - df_result['canal_Costo']) / df_result['canal_Costo']) * 100
    df_result = df_result.sort_values(by='Porcentaje de aumento', ascending=False)
    df_result['Porcentaje de aumento'] = df_result['Porcentaje de aumento'].round()

    return df_result

def generate_report(df_result, archivo_resultado):
    total_rows = len(df_result)
    exact_match_count = len(df_result[df_result['similarity'] == 100])
    missing_df1_rows = len(df_result[df_result['df2_SKU'].isnull()])
    missing_df2_rows = len(df_result[df_result['canal_SKU'].isnull()])

    # Filtrar el DataFrame para incluir sólo los productos con un aumento mayor a 0%
    increased_products = df_result[df_result['Porcentaje de aumento'] > 0]

    # Calcular el aumento promedio sólo con los productos filtrados
    average_increase = increased_products['Porcentaje de aumento'].mean()
    
    # Calcular la cantidad de productos que sufrieron un aumento
    num_products_with_increase = len(increased_products)

    excessive_threshold = 10
    excessive_increases = df_result[df_result['Porcentaje de aumento'] > excessive_threshold]

    print()
    print(f"En general, los productos aumentaron en un {average_increase:.2f}%.")
    print(f"De los {total_rows} productos, {num_products_with_increase} sufrieron un aumento.")
    print()
    print(f"Total de filas en df_result: {total_rows}")
    print(f"Filas con similaridad del 100%: {exact_match_count}")
    print(f"Filas de CANAL no encontradas en df2: {missing_df1_rows}")
    print(f"Filas de df2 no encontradas en CANAL: {missing_df2_rows}")
    print()
    print("Archivo CONCATENADO guardado como",archivo_resultado)
    print()

    if len(excessive_increases) > 0:
        print(f"Se encontraron {len(excessive_increases)} productos con un aumento excesivo:")
        for idx, row in excessive_increases.iterrows():
            print(f"  - {row['canal_Nombre']} (SKU: {row['canal_SKU']}) aumentó un {row['Porcentaje de aumento']:.2f}%.")
    else:
        print("No se encontraron aumentos excesivos en los productos.")
