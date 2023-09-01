# routes/proveedor.py

import os
import json
import boto3
from io import BytesIO
from datetime import datetime
from importlib import import_module
from database import Proveedor, Session
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from flask import Blueprint, Response, request, render_template, flash, redirect, url_for
from routes.s3_utils import upload_file_to_s3, delete_object_from_s3, ensure_directory_exists_in_s3, list_folders_in_directory, list_files_in_folder, download_file_from_s3, download_files_from_folder, upload_files_to_folder, download_file_from_s3_json

s3 = boto3.client('s3', region_name='sa-east-1')  # Asegúrate de ajustar la región según corresponda


# Crea una "blueprint" para las rutas del proveedor
proveedor_blueprint = Blueprint('proveedor_blueprint', __name__)

# Asegúrate de que el directorio para el usuario, proveedor y fecha exista
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

@proveedor_blueprint.route('/<int:proveedor_id>', methods=['GET', 'POST'])
@login_required
def proveedor(proveedor_id):
    session = Session()  # Crea una nueva sesión
    try:
        proveedor = session.query(Proveedor).get(proveedor_id)
        session.commit()

        # Lista de fechas en las que se subieron archivos
        directory = f'clients/{current_user.id}/{proveedor_id}'
        dates = list_folders_in_directory(directory, bucket_name="proveesync")

        try:
            # Convertir las fechas en objetos datetime y ordenar
            if dates:  # Verifica que la lista de fechas no esté vacía
                dates = sorted(dates, key=lambda x: datetime.strptime(x, '%d-%m-%Y'), reverse=True)
        except ValueError:
            print("Error de formato en las fechas.")
            dates = []

        print("Fechas recuperadas:", dates)

        if request.method == 'POST':
            files = request.files.getlist('files[]')
            for file in files:
                if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.csv') or file.filename.endswith('.xls')):
                    filename = secure_filename(file.filename)

                    # Guarda el archivo en un objeto BytesIO en lugar de en el disco
                    file_in_memory = BytesIO()
                    file.save(file_in_memory)

                    # Define el directorio de almacenamiento
                    date = datetime.now().strftime('%d-%m-%Y')
                    directory = f'clients/{current_user.id}/{proveedor_id}/{date}'
                    ensure_directory_exists_in_s3(directory)

                    # Sube el archivo a S3 desde la memoria
                    upload_file_to_s3(file_in_memory, f'{directory}/{filename}')

            flash('Archivos subidos correctamente')
            return redirect(url_for('proveedor_blueprint.proveedor', proveedor_id=proveedor_id))

        return render_template('proveedor.html', proveedor=proveedor, dates=dates)

    except Exception as e:
        print("Error general:", e)  # Imprime el error
        session.rollback()  # Si hay un error, deshaz los cambios
        flash(f'Error al procesar la solicitud: {e}', 'error')  # Muestra un mensaje flash con el error
        return redirect(url_for('proveedor_blueprint.proveedor', proveedor_id=proveedor_id))  # Redirige a otra página

    finally:
        session.close()  # Asegúrate de cerrar la sesión al final




@login_required
@proveedor_blueprint.route('/<int:proveedor_id>/<date>', methods=['GET'])
def proveedor_files(proveedor_id, date):
    session = Session()  # Crea una nueva sesión
    proveedor = None
    try:
        proveedor = session.query(Proveedor).get(proveedor_id)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        directory = f'clients/{current_user.id}/{proveedor_id}/{date}'
        excluded_files = ['combined.xlsx', 'final.xlsx']
        excluded_extensions = ['.json']
        allowed_extensions = ['.xlsx', '.xls', '.csv','.pdf']

        files_in_directory = list_files_in_folder(bucket_name="proveesync", folder_path=directory)

        # Añade lógica para excluir archivos renombrados
        renamed_files = [f"{current_user.id}-{proveedor.nombre}-{'canal' if 'canal' in file else 'proveedor'}.{ext}"
                         for file in files_in_directory for ext in ['csv', 'xlsx', 'xls']
                        ]

        excluded_files += renamed_files  # Añade los archivos renombrados a la lista de exclusión

        filtered_files = [os.path.basename(f) for f in files_in_directory
                          if os.path.basename(f) not in excluded_files and
                          os.path.splitext(f)[1] in allowed_extensions and
                          f != '.DS_Store']

        proveedor_file = os.path.basename(f"{proveedor.nombre}.xlsx")
        report_file = os.path.basename("report.pdf")

        files_to_show = []
        if proveedor_file in filtered_files:
            files_to_show.append(proveedor_file)
            filtered_files.remove(proveedor_file)
        if report_file in filtered_files:
            files_to_show.append(report_file)
            filtered_files.remove(report_file)

        files_to_show += filtered_files

        report_data_path = os.path.join(directory, "report_data.json")
        report_data = {}

        # En tu bloque try
        try:
            report_data_content = download_file_from_s3_json(bucket_name="proveesync", object_name=report_data_path)
            report_data = json.loads(report_data_content)
            print("Report Data:", report_data)  
        except Exception as e:
            print("Error al cargar el archivo JSON:", e)


        result = render_template('proveedor_files.html', proveedor=proveedor, date=date, files=files_to_show, report_data=report_data)
        session.close()
        return result


@proveedor_blueprint.route('/<int:proveedor_id>/<date>/<filename>', methods=['GET'])
@login_required
def serve_file(proveedor_id, date, filename):
    bucket_name = "proveesync"
    object_key = f'clients/{current_user.id}/{proveedor_id}/{date}/{filename}'

    # Descargar el archivo desde S3
    file_obj = s3.get_object(Bucket=bucket_name, Key=object_key)
    file_data = file_obj['Body'].read()

    # Crear una respuesta con los datos del archivo
    response = Response(file_data, content_type='application/octet-stream')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'

    return response


@proveedor_blueprint.route('/<int:proveedor_id>/<date>/delete', methods=['POST'])
@login_required
def delete(proveedor_id, date):
    session = Session()  # Crea una nueva sesión
    try:
        object_key = f'clients/{current_user.id}/{proveedor_id}/{date}'
        
        # Eliminar la carpeta en S3
        delete_object_from_s3(object_key, bucket_name="proveesync")

        flash('Fecha eliminada correctamente')
        return redirect(url_for('proveedor_blueprint.proveedor', proveedor_id=proveedor_id))
    except Exception as e:  # Cambié esto a Exception, ya que no estamos interactuando con SQLAlchemy aquí
        print(e)  # Imprime el error

@proveedor_blueprint.route('/<int:proveedor_id>/<date>/rename', methods=['POST'])
@login_required
def rename(proveedor_id, date):
    print(f"Procesando rename para proveedor: {proveedor_id}, fecha: {date}")
    session = Session()
    try:
        proveedor = session.query(Proveedor).get(proveedor_id)
        assert proveedor is not None, "Proveedor no encontrado"

        object_key_prefix = f'clients/{current_user.id}/{proveedor_id}/{date}'
        local_directory = f'/tmp/clients/{current_user.id}/{proveedor_id}/{date}'
        download_files_from_folder(bucket_name="proveesync", folder_path=object_key_prefix, local_path=local_directory)

        downloaded_files = os.listdir(local_directory)
        print(f"Archivos descargados en {local_directory}: {downloaded_files}")

        module_name = f"userscripts.{current_user.id}"
        module = import_module(module_name)
        print(f"Módulo importado: {module}")

        module.process_files(current_user.id, proveedor, local_directory)

        print(f"Subiendo archivos procesados desde {local_directory} a {object_key_prefix}")
        upload_files_to_folder(bucket_name="proveesync", folder_path=object_key_prefix, local_path=local_directory)

        flash('Archivos renombrados correctamente')
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        # Eliminar los archivos temporales
        for file in os.listdir(local_directory):
            file_path = os.path.join(local_directory, file)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"No se pudo eliminar {file_path}: {e}")

    return redirect(url_for('proveedor_blueprint.proveedor_files', proveedor_id=proveedor_id, date=date))
