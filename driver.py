from click import echo, style
import rich
import pika
import configparser
import threading

class RabbitMQ_Driver:
	server_address = ''
	user_name = ''
	user_password = ''
	queue_prefix = ''
	connection = None
	channel = None
	config = configparser.ConfigParser()

	def __init__(self):
		self.config.read('settings.ini')
		self.server_address = self.config["RabbitMQ"]["adress"]
		self.user_name = self.config["RabbitMQ"]["user"]
		self.user_password = self.config["RabbitMQ"]["password"]
		self.queue = self.config["RabbitMQ"]["queue"]
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(	host=self.server_address,
																	  			credentials = pika.PlainCredentials(	username  = self.user_name,
																														 password = self.user_password)))
		self.channel = self.connection.channel()
		rich.print(self.connection)
		rich.print(self.channel)


	def add_queue(self, queue_name:str, callback: callable):
		self.channel.queue_declare(queue=queue_name)
		self.channel.basic_consume(		queue=queue_name,
							 			on_message_callback=callback,
										auto_ack=False)
		self.channel.start_consuming()
		rich.print(f'Add queue: {queue_name}')


	def add_queue_non_blocking(self, queue_name: str, callback: callable):
		self.channel.queue_declare(queue=queue_name)
		self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
		t = threading.Thread(target=self.channel.start_consuming)
		t.daemon = True
		t.start()
		rich.print(f'Add queue: {queue_name}')


	def put_message(self, queue_name, message):
		rich.print(f'Put message: {message} into queue: {queue_name}')
		self.channel.basic_publish(exchange='', routing_key=queue_name, body=message)
		

	def recieve_message(self, ch, method, properties, body:bytes):
		rich.print(f"Received: '{body.decode(encoding='utf8',  errors='ignore')}', ch:{ch}, method:{method}, properties:{properties}")


	def __del__(self):
		self.connection.close()


def my_test_callback(ch, method, properties, body:bytes):
	rich.print(f"From:my_test_callback Received: '{body.decode(encoding='utf8',  errors='ignore')}', ch:{ch}, method:{method}, properties:{properties}")
	ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
	rd = RabbitMQ_Driver()
	rd.add_queue_non_blocking('test', my_test_callback)
	rd.put_message('test', 'test_message_1')

