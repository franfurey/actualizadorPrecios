# Este es el archivo del proveedor: Drimel
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

def process_proveedor_file():
    session = requests.Session()
    
    # Configurar el User-Agent
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Visitar la página principal para recoger cookies
    session.get('https://drimel.com.ar', headers=headers)

    urls = ['https://drimel.com.ar/categoria/panales/bebes', 'https://drimel.com.ar/categoria/panales/cuidado-del-bebe']
    marcas = ['Algabo', 'Duffy', 'Huggies','Babysec','Caricia','Estrella','Pampers',
              'Candy','Doncella','Deyse','Johnsons','Kimbies','Upa']

    df = pd.DataFrame(columns=['name', 'price','marca','product_id', 'product_sku','url_id','MPN (Número de pieza del fabricante)'])        
    
    for extract_url in urls: 
        page = 1
        while True:
            url = f"{extract_url}/page/{page}"  # Nueva forma de generar la URL
            print(f"Intentando acceder a {url}")

            # Usar la session y los headers para la solicitud
            response = session.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = soup.find_all('div', class_='box-text box-text-products')
            
            if not products:
                break

            for product in products:
                name = product.find('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link').text.strip()
                price = product.find('span', class_='woocommerce-Price-amount amount').text.strip()[1:]
                price = price.replace('"', '').replace('.', '').split(',')[0]
                
                marca = ''
                for m in marcas:
                    if m.lower() in name.lower():
                        marca = m
                        break

                add_to_cart_button = product.find('a', class_='add_to_cart_button')
                product_id = add_to_cart_button.get('data-product_id', '')
                product_sku = add_to_cart_button.get('data-product_sku', '')
                url_id = re.sub('[^a-zA-Z0-9]+', '-', name).strip('-')
                url_id = url_id.replace(' ', '-')
                
                df = df[(df['marca'] != 'Algabo') & (df['marca'] != 'Upa')]

                MPN = 'Drimel'
                df.loc[len(df)] = [name, price, marca, product_id, product_sku, url_id, MPN]
            page += 1

    df = df.rename(columns={'name': 'Nombre', 'price': 'Costo',
                             'product_id': 'SKU', 'product_sku': 'Código de barras',
                               'url_id':'Identificador de URL', 'marca':'Marca'})
    
    df['Costo'] = pd.to_numeric(df['Costo'])
    df['Costo'] = df['Costo'].apply(lambda x: round(x*0.9))

    df['SKU'] = df['SKU'].astype(int)
    df = df.sort_values('SKU', ascending=True)
    print('DRIMEL DF')
    print(df)
    print(df.columns)

    return df
