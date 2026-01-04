FROM python:3.9-slim

WORKDIR /app

COPY worker_email.py .

RUN pip install pika

CMD ["python", "worker_email.py"]