# database.py

import os
import boto3
import requests
from github import Github
from dotenv import load_dotenv
from flask_login import UserMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from routes.s3_utils import upload_file_to_s3
from werkzeug.security import generate_password_hash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

load_dotenv('db.env')
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")


def enviar_correo_mailgun(email, username, company):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": "Tu Nombre <tu_email@tu_dominio.com>",
            "to": "Francisco Furey <franciscofurey@gmail.com>",
            "subject": "Nuevo usuario creado",
            "text": f"Se ha creado un nuevo usuario.\nEmail: {email}\nUsername: {username}\nCompany: {company}"
        }
    )


db_connection_string = os.getenv("DATABASE_URL")

engine = create_engine(db_connection_string,
                      connect_args={
                        "ssl":{
                          "ssl_ca": "/etc/ssl/cert.pem"
                        }
                      },
                      pool_timeout=60)

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
    is_admin = Column(Boolean, default=False)  # Nueva línea para saber si es administrador
    company = Column(String(255))  # Aquí está tu nueva columna

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
    user_id = Column(Integer, ForeignKey('users.id'))

def create_user(username, password, company):
    session = Session()  # Crea una nueva sesión
    # Crear un cliente S3
    s3_client = boto3.client('s3', region_name='sa-east-1')
    # Token de acceso personal de GitHub
    github_token = os.getenv("GITHUB_TOKEN")
    # Crear una instancia de Github con tu token
    g = Github(github_token)
    # Obtener el repositorio en el que quieres trabajar
    repo = g.get_repo("franfurey/actualizadorPrecios")

    try:
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=username, password=hashed_password, company=company)
        session.add(new_user)
        session.commit()

        # Simular la creación de una carpeta del cliente en S3
        client_directory_key = f'clients/{new_user.id}/'
        s3_client.put_object(Bucket='proveesync', Key=client_directory_key)

        # Contenido del archivo de usuario
        user_script_file_content = f"# Este es el archivo de {new_user.email}"
        # Ruta donde quieres crear el archivo en tu repositorio
        user_script_file_path = f'userscripts/{new_user.id}.py'
        # Crear el archivo en GitHub
        repo.create_file(user_script_file_path, f"Creando archivo para el usuario {new_user.id}", user_script_file_content)

        # Aquí reemplazas la parte del correo
        enviar_correo_mailgun(new_user.email, new_user.email.split('@')[0], company)


    except SQLAlchemyError as e:
        session.rollback()  # Si hay algún error, deshaz los cambios en la base de datos
        print(e)  # Imprime el error
    finally:
        session.close()  # Asegúrate de cerrar la sesión al final

def create_admin_user(email, password):
    session = Session()
    try:
        hashed_password = generate_password_hash(password, method='sha256')
        admin_user = User(email=email, password=hashed_password, is_admin=True)
        session.add(admin_user)
        session.commit()
        print(f"Admin user {email} created.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()
