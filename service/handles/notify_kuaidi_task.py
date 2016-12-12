# -*- coding: utf-8 -*-
"""
处理已支付的订单
"""
import time


from service.handler_register import register




@register("notify_kuadi_task")
def process(data, recv_msg=None):
	return
	corp_id = data['corp_id']
	delivery_item_id = data['delivery_item_id']

	corp = Corporation(corp_id)

	delivery_item = corp.delivery_item_repository.get_delivery_item(delivery_item_id)
	if delivery_item.with_logistics_trace:
		# 发送快递订阅
		is_success = ExpressService(delivery_item).get_express_poll()
		if not is_success:
			raise Exception(u'快递订阅异常')
