# FROM python:3.7

# COPY . /app
# WORKDIR /app
# RUN pip install -r requirements.txt
# RUN pip install gunicorn
# ENV FLASK_APP /app/server.py

# CMD gunicorn --bind 0.0.0.0:5001 wsgi:api

# EXPOSE 5001

# Use Python 3.9 as the base image
FROM python:3.7

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port Prometheus will use to scrape metrics
EXPOSE 8080

# Start the application
CMD ["python", "server.py"]