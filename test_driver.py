import pytest
from unittest.mock import patch, MagicMock
from driver import RabbitMQ_Driver
from requests.auth import HTTPBasicAuth
import datetime

@pytest.fixture(scope='module')
def rqd():
	driver = RabbitMQ_Driver()
	yield driver
	driver.__del__()

def test_create_queue(rqd: RabbitMQ_Driver):
	rqd.create_queue('pytest_create_queue')


def test_get_broker_queues(rqd: RabbitMQ_Driver):
	assert 'pytest_create_queue' in rqd.get_broker_queues(), "Not found at very time created queue 'pytest_create_queue'"


def test_put_message(rqd: RabbitMQ_Driver):
	rqd.put_message(message='test', queue_name='pytest_create_queue')


def test_get_one_message(rqd: RabbitMQ_Driver):
	message = rqd.get_one_message( queue_name='pytest_create_queue')
	assert message == 'test'


def test_delete_queue(rqd: RabbitMQ_Driver):
	rqd.delete_queue('pytest_create_queue')
	assert 'pytest_create_queue' not in rqd.get_broker_queues(), "Found at very time created queue 'pytest_create_queue'"