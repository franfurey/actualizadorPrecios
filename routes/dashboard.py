# routes/dashboard.py

import os
import shutil
from github import Github
from database import Proveedor, Session
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user
from routes.s3_utils import upload_file_to_s3, delete_object_from_s3
from flask import Blueprint, render_template, request, flash, redirect, url_for

dashboard_blueprint = Blueprint('dashboard_blueprint', __name__)

@dashboard_blueprint.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    session = Session()  # Crea una nueva sesión

    try:
        if request.method == 'POST':
            nombre_proveedor = request.form['nombre_proveedor']

            nuevo_proveedor = Proveedor(nombre=nombre_proveedor, user_id=current_user.id)
            session.add(nuevo_proveedor)
            session.commit()

            # Crear el archivo Python del proveedor en GitHub
            github_token = os.getenv("GITHUB_TOKEN")
            g = Github(github_token)
            repo = g.get_repo("franfurey/actualizadorPrecios")

            proveedor_file_content = f"# Este es el archivo del proveedor: {nuevo_proveedor.nombre}"
            proveedor_file_path = f'proveedores/{current_user.id}/{nuevo_proveedor.id}.py'
            repo.create_file(proveedor_file_path, f"Creando archivo para el proveedor {nuevo_proveedor.id}", proveedor_file_content)

            # Crear el directorio del proveedor en AWS S3
            client_directory_key = f'clients/{current_user.id}/{nuevo_proveedor.id}/'
            upload_file_to_s3('', client_directory_key)  # Crea un objeto en la carpeta del proveedor en S3

            return redirect(url_for('dashboard_blueprint.dashboard'))

        proveedores = [{'id': proveedor.id, 'nombre': proveedor.nombre, 'url': url_for('proveedor_blueprint.proveedor', proveedor_id=proveedor.id)} for proveedor in session.query(Proveedor).filter_by(user_id=current_user.id).all()]

        return render_template('dashboard.html', proveedores=proveedores)
    except SQLAlchemyError as e:
        session.rollback()  # Si hay algún error, deshaz los cambios en la base de datos
        print(e)  # Imprime el error
    finally:
        session.close()  # Asegúrate de cerrar la sesión al final



@dashboard_blueprint.route('/delete/<int:proveedor_id>', methods=['POST'])
@login_required
def delete(proveedor_id):
    session = Session()  # Crea una nueva sesión

    try:
        proveedor = session.query(Proveedor).get(proveedor_id)
        if proveedor:
            # Ruta al archivo .py del proveedor en GitHub
            github_token = os.getenv("GITHUB_TOKEN")
            g = Github(github_token)
            repo = g.get_repo("franfurey/actualizadorPrecios")
            proveedor_file_path = f'proveedores/{current_user.id}/{proveedor.id}.py'

            # Eliminar el archivo del proveedor en GitHub si existe
            try:
                content = repo.get_contents(proveedor_file_path)
                repo.delete_file(content.path, f"Eliminando archivo del proveedor {proveedor.id}", content.sha)
            except:
                pass  # Si el archivo no existe, continuar

            # Ruta a la carpeta del proveedor en AWS S3
            proveedor_directory_key = f'clients/{current_user.id}/{proveedor.id}/'
            delete_object_from_s3(proveedor_directory_key)  # Eliminar el objeto en la carpeta del proveedor en S3

            # Eliminar el proveedor de la base de datos
            session.delete(proveedor)
            session.commit()
            flash('Proveedor eliminado correctamente')
        else:
            flash('Proveedor no encontrado')
        return redirect(url_for('dashboard_blueprint.dashboard'))
    except SQLAlchemyError as e:
        session.rollback()  # Si hay algún error, deshaz los cambios en la base de datos
        print(e)  # Imprime el error
    finally:
        session.close()  # Asegúrate de cerrar la sesión al final
