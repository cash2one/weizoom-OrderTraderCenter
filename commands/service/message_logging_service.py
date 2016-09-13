# -*- coding: utf-8 -*-
"""
记录MNS消息的service

@author Victor
"""

import logging

from commands.service_register import register


@register("message.log")
def customer_add_service(data, recv_msg=None):
	"""
	记录MNS message

	"""
	logging.info("ReceiptHandle:%s MessageBody:%s MessageID:%s" % (\
		recv_msg.receipt_handle, \
		recv_msg.message_body, \
		recv_msg.message_id))
	return
