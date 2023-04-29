FROM grafana/grafana:latest

# Install any additional packages or dependencies here, if needed

# Copy any custom configuration files
COPY ./datasource.yml /etc/grafana/provisioning/datasource.yml

# Set environment variables, if needed

# Expose any required ports
EXPOSE 3000
