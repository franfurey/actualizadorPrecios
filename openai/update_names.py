import re

def obtener_nombre_ecommerce(texto):
    matches_simple = re.findall(r"'([^']*)'", texto)  # Encuentra textos en comillas simples
    matches_double = re.findall(r'"([^"]*)"', texto)  # Encuentra textos en comillas dobles
    matches = matches_simple + matches_double  # Combina los resultados
    if matches:
        # Retorna el último match
        result = matches[-1]
    else:
        # Si no hay comillas, retorna el texto original
        result = texto

    # Define los prefijos a eliminar
    prefixes = ["Marca - ", "Nombre del producto - ", "Cantidad - ", "Color - ", "Otras características relevantes - "]

    # Elimina cada prefijo si está presente
    for prefix in prefixes:
        if result.startswith(prefix):
            result = result[len(prefix):]  # El prefijo tiene un número de caracteres igual a su longitud

    # Si el resultado contiene la línea de cabecera, la elimina
    header = "Marca - Nombre del producto - Cantidad - Color - Otras características relevantes:"
    if header in result:
        result = result.replace(header, "").strip()  # Elimina la cabecera y los espacios en blanco al principio y al final

    return result