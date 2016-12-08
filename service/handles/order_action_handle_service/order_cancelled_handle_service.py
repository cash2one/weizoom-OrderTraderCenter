# -*- coding: utf-8 -*-
"""


@author Victor
"""

from bdem import msgutil


from service.handler_register import register
from order_trade_center_conf import TOPIC
from service.utils import not_retry


@register("order_cancelled")
@not_retry
def process(data, recv_msg=None):
	corp_id = data['corp_id']
	order_id = data['order_id']
	order_bid = data['order_bid']

	from_status = data['from_status']
	to_status = data['to_status']

	# 释放订单资源
	release_order_resource_service = ReleaseOrderResourceService.get(corp)
	release_order_resource_service.release(order_id,from_status,to_status)

	# 更新会员信息

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
