import requests
from requests.auth import HTTPBasicAuth

# Настройки подключения
rabbitmq_host = '192.168.0.112'
rabbitmq_port = 15672
username = 'user'
password = 'password'
# URL для получения списка очередей
url = f'http://{rabbitmq_host}:{rabbitmq_port}/api/queues'
# Выполняем запрос к RabbitMQ Management API
response = requests.get(url, auth=HTTPBasicAuth(username, password))
if response.status_code == 200:
	queues = response.json()
	print("Список очередей:")
	for queue in queues:
		print(queue['name'])
else:
	print(f"Не удалось получить список очередей. Статус код: {response.status_code}")
	print(f"Причина: {response.text}")