# routes/proveedor.py

from flask import request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from database import Proveedor, session
import os
from flask import Blueprint, send_from_directory
from datetime import datetime
import shutil
from userscripts.drogueriamg import rename_files



# Crea una "blueprint" para las rutas del proveedor
proveedor_blueprint = Blueprint('proveedor_blueprint', __name__)

# Asegúrate de que el directorio para el usuario, proveedor y fecha exista
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

@proveedor_blueprint.route('/<int:proveedor_id>', methods=['GET', 'POST'])
@login_required
def proveedor(proveedor_id):
    proveedor = session.query(Proveedor).get(proveedor_id)

    if request.method == 'POST':
        files = request.files.getlist('files[]')
        for file in files:
            if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.csv') or file.filename.endswith('.xls')):
                filename = secure_filename(file.filename)
                
                # Define el directorio de almacenamiento
                date = datetime.now().strftime('%d-%m-%Y')
                directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/{proveedor_id}/{date}'
                ensure_directory_exists(directory)

                # Guarda el archivo
                file.save(os.path.join(directory, filename))
                
        flash('Archivos subidos correctamente')
        return redirect(url_for('proveedor_blueprint.proveedor', proveedor_id=proveedor_id))


    # Lista de fechas en las que se subieron archivos
    directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/{proveedor_id}'
    ensure_directory_exists(directory)  # Asegurarse de que el directorio existe antes de intentar listar sus archivos
    dates = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

    return render_template('proveedor.html', proveedor=proveedor, dates=dates)


# Crea una nueva ruta para manejar las solicitudes de archivos por fecha
@proveedor_blueprint.route('/<int:proveedor_id>/<date>', methods=['GET'])
@login_required
def proveedor_files(proveedor_id, date):
    proveedor = session.query(Proveedor).get(proveedor_id)

    # Obtiene la lista de archivos para la fecha solicitada
    directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/{proveedor_id}/{date}'
    files = [f for f in os.listdir(directory) if f != '.DS_Store']
    return render_template('proveedor_files.html', proveedor=proveedor, date=date, files=files)

# También necesitarás una función para servir los archivos individuales
@proveedor_blueprint.route('/<int:proveedor_id>/<date>/<filename>', methods=['GET'])
@login_required
def serve_file(proveedor_id, date, filename):
    directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/{proveedor_id}/{date}'
    return send_from_directory(directory, filename)

@proveedor_blueprint.route('/<int:proveedor_id>/<date>/delete', methods=['POST'])
@login_required
def delete(proveedor_id, date):
    directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/{proveedor_id}/{date}'
    shutil.rmtree(directory)
    flash('Fecha eliminada correctamente')
    return redirect(url_for('proveedor_blueprint.proveedor', proveedor_id=proveedor_id))


@proveedor_blueprint.route('/<int:proveedor_id>/<date>/rename', methods=['POST'])
@login_required
def rename(proveedor_id, date):
    directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/{proveedor_id}/{date}'
    rename_files(current_user.id, proveedor_id, directory)
    flash('Archivos renombrados correctamente')
    return redirect(url_for('proveedor_blueprint.proveedor_files', proveedor_id=proveedor_id, date=date))
