# -*- coding: utf-8 -*-
"""
处理demo_data_created消息(演示)

@author Victor
"""

import logging
from service.handler_register import register

@register("demo_data_created")
def handler(data, recv_msg=None):
	"""
	演示接收消息
	"""
	logging.info("processing message data: {}".format(data))
	# logging.info("ReceiptHandle: {}".format(recv_msg.receipt_handle))
	# logging.info("MessageBody: {}".format(recv_msg.message_body))
	# logging.info("MessageID: {}".format(recv_msg.message_id))
