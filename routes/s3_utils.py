# routes/s3_utils.py
import os
import boto3
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('db.env')
# Configurar la sesión con las credenciales de AWS
session = boto3.Session(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='sa-east-1'  # Ajusta la región según corresponda
)

# Crear un cliente S3 usando la sesión
s3_client = session.client('s3')

def upload_file_to_s3(file_obj, object_name, bucket_name="proveesync"):
    if file_obj == "":
        s3_client.put_object(Bucket=bucket_name, Key=f"{object_name}/")
    elif isinstance(file_obj, BytesIO):
        file_obj.seek(0)  # Asegurarse de que el cursor está al inicio del objeto en memoria
        s3_client.upload_fileobj(file_obj, bucket_name, object_name)
    else:
        s3_client.upload_file(file_obj, bucket_name, object_name)



def download_file_from_s3(file_path, object_name, bucket_name="proveesync"):
    s3_client.download_file(bucket_name, object_name, file_path)

def list_files_in_folder(bucket_name="proveesync", folder_path=""):
    result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    files = []
    if 'Contents' in result:
        for item in result['Contents']:
            files.append(item['Key'])
    return files

def delete_object_from_s3(object_key, bucket_name="proveesync"):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=object_key)
    
    for item in response.get('Contents', []):
        s3_client.delete_object(Bucket=bucket_name, Key=item['Key'])
    
    # Eliminar el objeto en sí
    s3_client.delete_object(Bucket=bucket_name, Key=object_key)


def list_folders_in_directory(directory_path, bucket_name="proveesync"):
    if not directory_path.endswith('/'):
        directory_path += '/'

    result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=directory_path, Delimiter='/')
    folders = []

    for item in result.get('CommonPrefixes', []):
        folder_name = item['Prefix'].replace(directory_path, '', 1).rstrip('/')

        if folder_name:  # Verifica que no sea una cadena vacía
            try:
                # Intenta convertir el nombre de la carpeta a una fecha, si eso es lo que esperas
                datetime.strptime(folder_name, '%d-%m-%Y')
            except ValueError:
                print(f"Error de formato en la fecha: {folder_name}")
                continue  # Salta esta iteración y continua con la próxima
            
            folders.append(folder_name)
            
    return folders


def ensure_directory_exists_in_s3(directory_path, bucket_name="proveesync"):
    directory_key = f'{directory_path}/'
    s3_client.put_object(Bucket=bucket_name, Key=directory_key)

def download_files_from_folder(bucket_name, folder_path, local_path):
    print(f"Descargando archivos desde el folder {folder_path} en el bucket {bucket_name} a {local_path}")
    files = list_files_in_folder(bucket_name=bucket_name, folder_path=folder_path)
    
    # Filtrar solo los objetos que no sean directorios
    files = [f for f in files if not f.endswith('/')]

    print(f"Archivos encontrados en el folder: {files}")

    # Asegurarse de que el directorio local exista
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    
    # Descargar cada archivo en el directorio local
    for file_key in files:
        local_file_path = os.path.join(local_path, os.path.basename(file_key))
        print(f"Descargando archivo {file_key} a {local_file_path}")
        download_file_from_s3(file_path=local_file_path, object_name=file_key, bucket_name=bucket_name)


def upload_files_to_folder(bucket_name, folder_path, local_path):
    print(f"Subiendo archivos desde el folder local {local_path} al bucket {bucket_name} en la ruta {folder_path}")
    files = os.listdir(local_path)

    # Subir cada archivo en el directorio local a S3
    for file_name in files:
        local_file_path = os.path.join(local_path, file_name)
        object_key = os.path.join(folder_path, file_name)
        print(f"Subiendo archivo {local_file_path} a {object_key}")
        upload_file_to_s3(file_obj=local_file_path, object_name=object_key, bucket_name=bucket_name)
