# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
from sqlalchemy.orm import relationship
from flask_login import UserMixin

load_dotenv('db.env')

db_connection_string = os.getenv("DATABASE_URL")

ssl_args = {
    'ssl': {
        "ca": "/etc/ssl/cert.pem"
    }
}

engine = create_engine(
    db_connection_string,
    connect_args=ssl_args)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

Base = declarative_base()

class User(UserMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True)
    password = Column(String(128))
    is_active = Column(Boolean, default=True)

    # Relación uno a muchos con la tabla Proveedores
    proveedores = relationship("Proveedor", backref="user", primaryjoin="User.id == foreign(Proveedor.user_id)")

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

class Proveedor(Base):
    __tablename__ = 'proveedores'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    user_id = Column(Integer)

def create_user(username, password):
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(email=username, password=hashed_password)
    session.add(new_user)
    session.commit()

    # Crear la estructura de carpetas y archivos después de que se haya creado el usuario
    client_directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/clients/{new_user.id}'
    os.makedirs(client_directory, exist_ok=True)  # Crea la carpeta del cliente si no existe

    userscripts_directory = f'/Users/franciscofurey/00DataScience/Canal/actualizadorPrecios/userscripts'
    os.makedirs(userscripts_directory, exist_ok=True)  # Crea la carpeta userscripts si no existe

    user_script_file = os.path.join(userscripts_directory, f'{new_user.id}.py')
    with open(user_script_file, 'w') as f:  # Crea el archivo .py del usuario
        f.write(f"# Este es el archivo de {new_user.email}")  # Aquí se usa el username registrado

    proveedores_directory = os.path.join(client_directory, 'proveedores')
    os.makedirs(proveedores_directory, exist_ok=True)  # Crea la carpeta proveedores si no existe

    for proveedor in new_user.proveedores:
        proveedor_file = os.path.join(proveedores_directory, f'{proveedor.id}.py')
        with open(proveedor_file, 'w') as f:  # Crea el archivo del proveedor
            f.write(f"# Este es el archivo del proveedor: {proveedor.nombre}")



Base.metadata.create_all(engine)