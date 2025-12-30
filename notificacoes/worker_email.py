import pika
import sys
import os

def main():
    # Conexão com o RabbitMQ
    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
    )
    channel = connection.channel()

    #Cria a fila 'email_queue' se ela não existir
    channel.queue_declare(queue='email_queue')

    #Função que vvai rodar quando receber uma mensagem
    def callback(ch, method, properties, body):
        mensagem = body.decode('utf-8')
        print(f"Recebido: {mensagem}")
        print("Enviando email... Aguarde... Enviado!")
        print(" --- Esperando a próxima mensagem ---")
    
    channel.basic_consume(queue='email_queue', on_message_callback=callback, auto_ack=True)

    print(" Worker de Email rodando. Esperando mensagem...")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrompido")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
