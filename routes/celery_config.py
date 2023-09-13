# routes/celery_config.py
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv('../db.env')
BROKER_URL = os.getenv('BROKER_URL')

app = Celery('myapp')
app.config_from_object('celery_config')
