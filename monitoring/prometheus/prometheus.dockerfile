FROM prom/prometheus:latest

COPY prometheus-config.yml /etc/prometheus/prometheus-config.yml

CMD [ "--config.file=/etc/prometheus/prometheus-config.yml" ]