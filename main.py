# main.py
# Importa las bibliotecas necesarias
from flask import Flask
from flask_login import LoginManager, login_required, logout_user
from database import User, session
from routes.login import login as login_view
import os
from routes.dashboard import dashboard as dashboard_view
from routes.dashboard import dashboard_blueprint
from routes.proveedor import proveedor as proveedor_view
from routes.proveedor import proveedor_blueprint

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

# Define la función que Flask-Login utiliza para interactuar con los usuarios
@login_manager.user_loader
def load_user(user_id):
    # Busca el usuario en la base de datos
    return session.query(User).get(int(user_id))

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
    return dashboard_view()

@app.route('/proveedor/<int:proveedor_id>', methods=['GET', 'POST'])
@login_required
def proveedor(proveedor_id):
    return proveedor_view(proveedor_id)

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
