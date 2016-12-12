# -*- coding: utf-8 -*-
"""


@author Victor
"""

from bdem import msgutil
from service.handler_register import register
from order_trade_center_conf import TOPIC
from service.utils import not_retry
import utils


@register("order_refunded")
@not_retry
def process(data, recv_msg=None):
	corp_id = data['corp_id']
	order_id = data['order_id']
	order_bid = data['order_bid']

	from_status = data['from_status']
	to_status = data['to_status']

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

	# fill_options = {
	# 	'with_member': True
	# }
	# order = corp.order_repository.get_order(order_id, fill_options)
	# member = corp.member_repository.get_member_by_id(order.member_info['id'])
	# member.update_pay_info(order, from_status, to_status)
	utils.update_member_pay_info(corp_id, order_id, from_status, to_status)
