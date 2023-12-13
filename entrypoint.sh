#!/bin/bash

# Start Nginx in the background
service nginx start

# Set number of workers to 1
WORKERS=1

# Start Gunicorn with 1 worker
gunicorn -b 0.0.0.0:8000 --log-level debug --workers $WORKERS --worker-class gevent main:app
