FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir confluent-kafka==2.5.3 faker==25.9.2 PyYAML==6.0.1
COPY generator/data_gen.py /app/
COPY config.yml /app/../config.yml
COPY config_loader.py /app/../config_loader.py
CMD ["python","-u","/app/data_gen.py"]