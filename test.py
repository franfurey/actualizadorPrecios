from dotenv import load_dotenv
import os

# Cargar las variables de entorno del archivo .env
load_dotenv('db.env')

# Obtener el valor de la variable DATABASE_URL
database_url = os.getenv("DATABASE_URL")

# Imprimir el valor de la variable DATABASE_URL
print(database_url)
