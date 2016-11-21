# -*- coding: utf-8 -*-
"""
处理demo_data_created消息(演示)

@author Victor
"""

from eaglet.utils.resource_client import Resource

import logging
from service.handler_register import register

@register("demo_data_created")
def handler(data, recv_msg=None):
	"""
	演示接收消息
	"""
	logging.info("processing message data: {}".format(data))
	print('$$$$$$$$$$$$$$$$$$$$')
	print(data)
	print('$$$$$$$$$$$$$$$$$$$$')


	# 如果需要访问其他api service
	# data = {
	# 	'corp_id': request.user.corp.id
	# }
	# resp = Resource.use('zeus').put({
	# 	'resource': 'mall.categories',
	# 	'data': data
	# })
	# if resp and resp['code'] == 200:
	#	......


	# 如果需要访问来自阿里云中间件的原始消息内容
	# logging.info("ReceiptHandle: {}".format(recv_msg.receipt_handle))
	# logging.info("MessageBody: {}".format(recv_msg.message_body))
	# logging.info("MessageID: {}".format(recv_msg.message_id))
