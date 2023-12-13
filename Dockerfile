# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn and gevent
RUN pip install gunicorn gevent

# Install Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy the Nginx site configuration file
COPY nginx.conf /etc/nginx/sites-available/app
# Ensure the Nginx site is enabled by creating a symbolic link
RUN ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled

# Remove the default Nginx configuration if it exists
RUN rm /etc/nginx/sites-enabled/default

# Make port 80 and 443 available to the world outside this container
EXPOSE 80 443

# Define environment variable
ENV FLASK_APP=main.py

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Give execution rights on the entrypoint script
RUN chmod +x /entrypoint.sh

# Run the entrypoint script to start Nginx and Gunicorn
ENTRYPOINT ["/entrypoint.sh"]
