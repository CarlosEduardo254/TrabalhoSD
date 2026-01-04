# Use uma imagem leve
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Instala dependências do SO (se precisar compilar algo)
RUN apt-get update && apt-get install -y iputils-ping

# Instala libs Python
RUN pip install flask grpcio grpcio-tools requests pika

# COPIA TODO O PROJETO para dentro do container
# Isso garante que a pasta 'agendamento' enxergue a pasta 'usuarios'
COPY . /app

# Define o PYTHONPATH para a raiz
ENV PYTHONPATH=/app

# O comando final será definido no docker-compose
CMD ["python", "--version"]