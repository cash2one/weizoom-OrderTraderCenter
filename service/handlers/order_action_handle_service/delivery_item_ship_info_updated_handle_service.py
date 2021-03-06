# -*- coding: utf-8 -*-
"""
处理订单的消息service(演示)

@author Victor
"""

import logging

from bdem import msgutil

from service.handler_register import register
from order_trade_center_conf import TOPIC
from service.utils import not_retry


@register("delivery_item_ship_info_updated")
@not_retry
def process(data, recv_msg=None):
	"""
	已完成
	发货出货单的消息处理
	"""

	corp_id = data['corp_id']
	delivery_item_id = data['delivery_item_id']

	# 订阅快递推送
	topic_name = TOPIC['base_service']
	data = {
		"delivery_item_id": delivery_item_id,
		"corp_id": corp_id
	}
	msgutil.send_message(topic_name, 'notify_kuaidi_task', data)
