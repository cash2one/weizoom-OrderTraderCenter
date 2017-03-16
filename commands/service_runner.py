# -*- coding: utf-8 -*-
"""
基于MNS的创建service runner

启动之后，不断轮询队列

@author Victor
"""
from eaglet.core.debug import get_uncaught_exception_data
from eaglet.utils.command import BaseCommand
from eaglet.core import watchdog
#from eaglet.core.cache import utils as cache_util
import json

import settings

from eaglet.core.exceptionutil import unicode_full_stack
import logging

from mns.account import Account
from mns.queue import *
from mns.topic import *
from mns.subscription import *

import time
import service  #load all message handlers
from service import handler_register


WAIT_SECONDS = 10
SLEEP_SECONDS = 10

VALID_BROKERS = set(['redis', 'mns'])

class Command(BaseCommand):
	help = "python manage.py service_runner"
	args = ''

	def get_message_broker(self):
		"""
		获取message broker

		如果是无效的broker，则返回None
		"""
		if hasattr(settings, 'MESSAGE_BROKER'):
			broker = getattr(settings, 'MESSAGE_BROKER')
		else:
			if hasattr(settings, 'MESSAGE_DEBUG_MODE') and settings.MESSAGE_DEBUG_MODE:
				broker = 'redis'
			else:
				broker = 'mns'

		if not broker in VALID_BROKERS:
			logging.error('invalid message broker: %s' % broker)
			broker = None

		return broker

	def create_queue(self, broker):
		"""
		根据broker类型，创建相应的queue对象
		"""
		if broker == 'redis':
			#创建redis queue
			from util import redis_queue
			queue = redis_queue.get_queue(settings.SUBSCRIBE_QUEUE_NAME)
		elif broker == 'mns':
			#创建aliyun mns queue
			self.mns_account = Account(\
				settings.MNS_ENDPOINT, \
				settings.MNS_ACCESS_KEY_ID, \
				settings.MNS_ACCESS_KEY_SECRET, \
				settings.MNS_SECURITY_TOKEN)

			queue = self.mns_account.get_queue(settings.SUBSCRIBE_QUEUE_NAME)
		else:
			queue = None

		return queue

	def handle(self, *args, **options):
		message_broker = self.get_message_broker()
		if not message_broker:
			logging.error('abort!!')
			return
		logging.info("message broker: {}".format(message_broker))

		queue = self.create_queue(message_broker)
		if not queue:
			logging.error('invalid queue, abort!!')
			return
		logging.info("receive message from queue: {}".format(settings.SUBSCRIBE_QUEUE_NAME))

		# TODO: 改成LongPoll更好
		while True:
			message_data = {}
			handler_func = None
			handle_success = False
			#读取消息
			message_name = ''
			try:
				recv_msg = queue.receive_message(WAIT_SECONDS)
				logging.info("Receive Message Succeed! ReceiptHandle:%s MessageBody:%s MessageID:%s" % (recv_msg.receipt_handle, recv_msg.message_body, recv_msg.message_id))

				# 处理消息(consume)
				data = json.loads(recv_msg.message_body)
				message_name = data['name']
				handler_func = handler_register.find_message_handler(message_name)
				if handler_func:
					try:
						message_data = data['data']
						response = handler_func(message_data, recv_msg)
						logging.info("service response: {}".format(response))
						handle_success = True

						#只有正常才能删除消息，否则消息仍然在队列中
						try:
							queue.delete_message(recv_msg.receipt_handle)
							logging.debug("Delete Message Succeed!  ReceiptHandle:%s" % recv_msg.receipt_handle)
						except MNSExceptionBase,e:
							logging.debug("Delete Message Fail! Exception:%s\n" % e)
					except:
						traceback = unicode_full_stack()
						logging.info(u"Service Exception: {}".format(traceback))
						message = {
							'message_id': recv_msg.message_id,
							'message_body_md5': '',
							'data': message_data,
							'queue_name': settings.SUBSCRIBE_QUEUE_NAME,
							'msg_name': message_name,
							'handel_success': handle_success,
						}
						uncaught_exception_data = get_uncaught_exception_data(None, message)
						if settings.MODE == 'deploy':
							watchdog.critical(uncaught_exception_data, 'Uncaught_Exception')
						else:
							print('**********Uncaught_Exception**********')
							print(json.dumps(uncaught_exception_data, indent=2))
							print('**********Uncaught_Exception**********\n')
				else:
					logging.warn(u"Warn: no such service found : {}".format(message_name))
					try:
						queue.delete_message(recv_msg.receipt_handle)
						logging.debug("Delete Message Succeed!  ReceiptHandle:%s" % recv_msg.receipt_handle)
					except MNSExceptionBase, e:
						logging.debug("Delete Message Fail! Exception:%s\n" % e)

			except MNSExceptionBase as e:
				if e.type == "QueueNotExist":
					logging.debug("Queue not exist, please create queue before receive message.")
					break
				elif e.type == "MessageNotExist":
					logging.debug("Queue is empty! Waiting...")
				else:
					logging.debug("Receive Message Fail! Exception:%s\n" % e)
				time.sleep(SLEEP_SECONDS)
				continue
			except Exception as e:
				traceback = unicode_full_stack()
				logging.info(u"Service Exception: {}".format(traceback))
			try:
				if handler_func:
					message = {
						'message_id': recv_msg.message_id,
						'message_body_md5': '',
						'data': message_data,
						'queue_name': settings.SUBSCRIBE_QUEUE_NAME,
						'msg_name': message_name,
						'handel_success': handle_success,
					}
					if handle_success:
						watchdog.info(message, log_type='MNS_RECEIVE_LOG')
					else:
						watchdog.critical(message, log_type='MNS_RECEIVE_LOG')

			except:
				print(unicode_full_stack())

		return
