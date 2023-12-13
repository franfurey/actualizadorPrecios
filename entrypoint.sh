#!/bin/bash

# Start Nginx in the background
service nginx start

# Calculate the number of cores
NUM_CORES=$(nproc --all)
# Calculate the number of workers based on the number of cores
WORKERS=$((NUM_CORES * 2 + 1))

# Start Gunicorn on port 8000 with debug logging and multiple workers with gevent
gunicorn -b 0.0.0.0:8000 --log-level debug --workers $WORKERS --worker-class gevent main:app
