from click import echo, style
import rich
import pika
import configparser
import requests
from requests.auth import HTTPBasicAuth


class RabbitMQ_Driver:
	server_address = ''
	server_port = ''
	user_name = ''
	user_password = ''
	queue_prefix = ''
	connection = None
	channel = None
	config = configparser.ConfigParser()

	def __init__(self):
		self.config.read('settings.ini')
		self.server_address = self.config["RabbitMQ"]["adress"]
		self.port = self.config["RabbitMQ"]["port"]
		self.user_name = self.config["RabbitMQ"]["user"]
		self.user_password = self.config["RabbitMQ"]["password"]
		self.queue = self.config["RabbitMQ"]["queue"]
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(	host=self.server_address,
																	  			credentials = pika.PlainCredentials(	username  = self.user_name,
																														 password = self.user_password)))
		self.channel = self.connection.channel()


	def create_queue(self, queue_name:str):
		self.channel.queue_declare(queue=queue_name, durable=True)
		rich.print(f'Create queue: {queue_name}')


	def add_queue_non_blocking(self, queue_name: str, callback: callable):
		self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
		self.channel.start_consuming()

	def put_message(self, queue_name, message):
		rich.print(f'Put message: {message} into queue: {queue_name}')
		self.channel.basic_publish(exchange='', routing_key=queue_name, body=message)
		

	def recieve_message(self, ch, method, properties, body:bytes):
		rich.print(f"Received: '{body.decode(encoding='utf8',  errors='ignore')}', ch:{ch}, method:{method}, properties:{properties}")

	def get_broker_queues(self):
		response = requests.get(f'http://{self.server_address}:{self.port}/api/queues', auth=HTTPBasicAuth(self.user_name, self.user_password))
		if response.status_code == 200:
			queues = response.json()
			return [queue['name'] for queue in queues]
		else:
			print(f"Не удалось получить список очередей. Статус код: {response.status_code}\nПричина: {response.text}")
			return []

	def __del__(self):
		try:
			self.connection.close()
		except:
			...


def my_test_callback(ch, method, properties, body:bytes):
	rich.print('consume:')
	rich.print(f"From:my_test_callback Received: '{body.decode(encoding='utf8',  errors='ignore')}', ch:{ch}, method:{method}, properties:{properties}")


if __name__ == '__main__':
	...
	# rd = RabbitMQ_Driver()
	# for i in range(10): rd.put_message('test', f'test_message_{i}')
	# rd.add_queue_non_blocking('test', my_test_callback)
	

