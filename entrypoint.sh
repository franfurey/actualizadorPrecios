#!/bin/bash

# Start Nginx in the background
service nginx start

# Start Gunicorn on port 8000
gunicorn -b 0.0.0.0:8000 main:app
