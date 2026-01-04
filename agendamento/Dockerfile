FROM python:3.11-slim
WORKDIR /app
COPY *.py ./
COPY usuario.proto .
RUN pip install --no-cache-dir grpcio grpcio-tools pika mysql-connector-python requests
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. usuario.proto
EXPOSE 5000
CMD ["python", "servico_agendamento.py"]