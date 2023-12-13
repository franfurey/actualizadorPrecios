#!/bin/bash

# Start Nginx in the background
service nginx start

# Calculate the number of cores
NUM_CORES=$(nproc --all)
# Set a lower number of workers for a t2.micro instance
WORKERS=$((NUM_CORES + 1))

# Start Gunicorn with the specified number of workers
gunicorn -b 0.0.0.0:8000 --log-level debug --workers $WORKERS --worker-class gevent main:app
