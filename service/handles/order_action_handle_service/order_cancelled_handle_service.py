# -*- coding: utf-8 -*-
"""


@author Victor
"""

from bdem import msgutil

from service.handler_register import register
from service.utils import not_retry
from eaglet.utils.resource_client import Resource


@register("order_cancelled")
@not_retry
def process(data, recv_msg=None):
	corp_id = data['corp_id']
	order_id = data['order_id']

	from_status = data['from_status']
	to_status = data['to_status']

	# 释放订单资源
	Resource.use('gaia').put({
		"resource": 'order.released_order',
		"data": {
			'corp_id': corp_id,
			'id': order_id,
			'from_status': from_status,
			'to_status': to_status
		}
	})

# # 发送运营邮件通知
# topic_name = TOPIC['base_service']
# data = {
# 	"type": "order",
# 	"order_id": order_id,
# 	"corp_id": corp.id
# }
# msgutil.send_message(topic_name, 'send_order_email_task', data)
#
# # 发送模板消息
# topic_name = TOPIC['base_service']
# data = {
# 	"order_id": order_id,
# 	"corp_id": corp.id
# }
# msgutil.send_message(topic_name, 'send_order_template_message_task', data)
