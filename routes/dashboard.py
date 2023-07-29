# routes/dashboard.py

from flask import request, redirect, url_for, render_template
from flask_login import login_required, current_user
from database import Proveedor, session
import os

@login_required
def dashboard():
    if request.method == 'POST':
        nombre_proveedor = request.form['nombre_proveedor']

        nuevo_proveedor = Proveedor(nombre=nombre_proveedor, user_id=current_user.id)
        session.add(nuevo_proveedor)
        session.commit()

        # Crear el archivo Python del proveedor después de agregar el nuevo proveedor
        proveedores_directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/proveesync/proveedores'
        proveedor_file = os.path.join(proveedores_directory, f'{nuevo_proveedor.id}.py')
        with open(proveedor_file, 'w') as f:
            f.write(f"# Este es el archivo del proveedor: {nuevo_proveedor.nombre}")

        # Crea el directorio del proveedor
        proveedor_directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{current_user.id}/{nuevo_proveedor.id}'
        os.makedirs(proveedor_directory, exist_ok=True)

        return redirect(url_for('dashboard'))

    proveedores = session.query(Proveedor).filter_by(user_id=current_user.id).all()
    # Asegúrate de que los nombres de los proveedores sean clickeables
    proveedores = [{'nombre': proveedor.nombre, 'url': url_for('proveedor', proveedor_id=proveedor.id)} for proveedor in session.query(Proveedor).filter_by(user_id=current_user.id).all()]

    return render_template('dashboard.html', proveedores=proveedores)
