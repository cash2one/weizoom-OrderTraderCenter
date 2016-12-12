# -*- coding: utf-8 -*-
"""
处理订单的消息service(演示)

@author Victor
"""

from bdem import msgutil
from eaglet.utils.resource_client import Resource
from service.handler_register import register
from order_trade_center_conf import TOPIC
from service.utils import not_retry


@register("order_paid")
@not_retry
def process(data, recv_msg=None):
	"""
	处理支付订单消息
	"""
	corp_id = data['corp_id']
	order_id = data['order_id']
	order_bid = data['order_bid']
	from_status = data['from_status']
	to_status = data['to_status']

	print('-----order_id', order_id, corp_id)

	resp = Resource.use('gaia').get({
		'resource': "order.order",
		'data': {
			'id': order_id,
			'corp_id': int(corp_id)
		}
	})
	order_data = resp['data']['order']
	products = []
	for delivery_item in order_data['delivery_items']:
		for p in delivery_item['products']:
			if p['promotion_info']['type'] != "premium_sale:premium_product":
				products.append(p)

	for product in products:
		sale_data = {
			'id': product['id'],
			'changed_count': product['count']
		}

		Resource.use('gaia').post({
			'resource': 'product.product_sale',
			'data': sale_data
		})

	# # 发送运营邮件通知
	# topic_name = TOPIC['base_service']
	# data = {
	# 	"type": "order",
	# 	"order_id": order.id,
	# 	"corp_id": corp.id
	# }
	# msgutil.send_message(topic_name, 'send_order_email_task', data)
	#
	# # 发送模板消息
	# topic_name = TOPIC['base_service']
	# data = {
	# 	"order_id": order.id,
	# 	"corp_id": corp.id
	# }
	# msgutil.send_message(topic_name, 'send_order_template_message_task', data)
