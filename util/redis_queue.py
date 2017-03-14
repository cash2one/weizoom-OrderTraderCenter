#!/usr/bin/python
# -*- coding: UTF-8 -*-

import redis
import settings
import json
import time
import logging

VisibilityTimeout = 10  # 取出消息隐藏时长

REDIS_QUEUE_DB = 8 #redis db for simulate <topic, queue>

class Message(object):
	def __init__(self, message):
		self.message_body = message['message_body']
		self.message_id = message['message_id']
		self.receipt_handle = self
		self.queue_value = json.dumps(message)


class Queue(object):
	def __init__(self, queue_name):
		self.queue_name = queue_name
		logging.info("connect redis: redis://%s:%s/%s" % (settings.REDIS_HOST, settings.REDIS_PORT, REDIS_QUEUE_DB))
		self.redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=REDIS_QUEUE_DB)

	def receive_message(self, WAIT_SECONDS):
		while True:
			#use timeout, to support Ctrl+C brek
			_message = self.redis.brpop(self.queue_name, 5)
			if not _message:
				continue

			_message = _message[1]
			message = json.loads(_message)
			status = message.setdefault('status', 'waiting')
			if status == 'waiting':
				message['status'] = 'processing'
				message['processing_from'] = time.time()
				self.redis.lpush(self.queue_name, json.dumps(message))

				return Message(message)
			elif status == 'processing':
				if message['processing_from'] + VisibilityTimeout < time.time():
					message['status'] = 'waiting'

				self.redis.lpush(self.queue_name, json.dumps(message))

	def get_attributes(self):
		return self

	def delete_message(self, receipt_handle):
		self.redis.lrem(self.queue_name, receipt_handle.queue_value)


def get_queue(name):
	return Queue(name)
