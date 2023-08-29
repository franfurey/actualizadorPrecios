# main.py
# Importa las bibliotecas necesarias
import os
from database import User, Session
from sqlalchemy.exc import SQLAlchemyError
from routes.login import login as login_view
from routes.dashboard import dashboard_blueprint
from routes.proveedor import proveedor_blueprint
from routes.dashboard import dashboard as dashboard_view
from routes.proveedor import proveedor as proveedor_view
from flask import Flask, redirect, session, url_for, render_template
from flask_login import LoginManager, login_required, logout_user, login_user, current_user

app = Flask(__name__)
app.register_blueprint(proveedor_blueprint, url_prefix='/proveedor')
app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

# Establece la clave secreta para tu aplicación Flask
# La clave secreta se utiliza para mantener las sesiones seguras
app.secret_key = os.getenv('SECRET_KEY')

# Inicializa el administrador de inicio de sesión para Flask
# Flask-Login se encarga de las sesiones de los usuarios
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    session = Session()  # Crea una nueva sesión

    try:
        # Busca al usuario en la base de datos
        user = session.get(User, int(user_id))
        session.expunge(user)  # Desvincula el objeto user de la sesión
        session.commit()
        return user
    except SQLAlchemyError as e:
        session.rollback()  # Si hay algún error, deshaz los cambios en la base de datos
        print(e)  # Imprime el error
    finally:
        session.close()  # Asegúrate de cerrar la sesión al final


# Define la ruta para la página de inicio
@app.route('/', methods=['GET', 'POST'])
def home():
    return login_view()

# Define la ruta para la página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_view()


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))  # redirige al admin_dashboard si es admin
    return dashboard_view()  # si no es admin, muestra la vista regular

@app.route('/proveedor/<int:proveedor_id>', methods=['GET', 'POST'])
@login_required
def proveedor(proveedor_id):
    return proveedor_view(proveedor_id)

@app.route('/impersonate/<int:user_id>')
@login_required
def impersonate(user_id):
    if current_user.is_admin:
        session['original_user_id'] = current_user.id  # Guardar el id del admin
        user_to_impersonate = load_user(user_id)  # Cargar el usuario a impersonar
        login_user(user_to_impersonate)  # Loguear como el nuevo usuario
        return redirect(url_for('dashboard'))  # Redirigir al dashboard o donde quieras
    else:
        return "No tienes permisos para hacer esto."


@app.route('/stop_impersonate')
@login_required
def stop_impersonate():
    original_user_id = session.pop('original_user_id', None)
    if original_user_id:
        original_user = load_user(original_user_id)
        login_user(original_user)
        return redirect(url_for('dashboard'))
    else:
        return "No estás suplantando a nadie."
    
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return "No tienes permisos para ver esta página."
    
    session = Session()  # Abre una nueva sesión
    users = session.query(User).all()  # Consulta para obtener todos los usuarios
    session.close()  # Cierra la sesión

    return render_template('admin_dashboard.html', users=users)


# Define la ruta para cerrar la sesión del usuario
@app.route('/logout')
@login_required
def logout():
    # Cierra la sesión del usuario
    logout_user()
    return 'Logged out'

# Corre la aplicación
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5555)
