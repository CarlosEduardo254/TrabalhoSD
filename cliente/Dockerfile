# Imagem base Python leve
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências Python necessárias para os scripts do cliente
RUN pip install --no-cache-dir requests pika

# Copia todos os scripts do cliente para o container
COPY . /app

# Define variáveis de ambiente padrão (podem ser sobrescritas na execução)
ENV API_HOST=host.docker.internal
ENV RABBITMQ_HOST=host.docker.internal

# Comando padrão - mostra ajuda sobre como usar
CMD ["sh", "-c", "echo 'Scripts disponíveis:' && echo '  python admin.py' && echo '  python medico.py' && echo '  python paciente.py' && echo '  python recepcionista.py' && echo '' && echo 'Execute com: docker run -it <imagem> python <script>.py'"]
