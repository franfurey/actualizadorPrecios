# routes/login.py

from flask import request, redirect, url_for, render_template
from werkzeug.security import check_password_hash
from flask_login import login_user
from database import User, session

def login():
    # Procesa la solicitud POST
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Busca el usuario en la base de datos
        user = session.query(User).filter_by(email=email).first()

        # Comprueba si el usuario existe y si la contraseña es correcta
        if user and check_password_hash(user.password, password):
            # Inicia la sesión del usuario
            login_user(user)
            # Redirige al usuario al panel de control
            return redirect(url_for('dashboard'))

        # Si el usuario no existe o la contraseña es incorrecta, recarga la página
        return redirect(url_for('login'))

    # Renderiza la plantilla de inicio de sesión
    return render_template('login.html')
