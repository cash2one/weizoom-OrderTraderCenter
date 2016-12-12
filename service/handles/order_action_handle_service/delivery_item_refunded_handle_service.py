# -*- coding: utf-8 -*-
"""
处理订单的消息service(演示)

@author Victor
"""
import json
from bdem import msgutil

from order_trade_center_conf import TOPIC
from service.handler_register import register
from service.utils import not_retry
from eaglet.utils.resource_client import Resource


@register("delivery_item_refunded")
@not_retry
def process(data, recv_msg=None):
	"""
	已完成
	@param data:
	@param recv_msg:
	@return:
	"""
	corp_id = data['corp_id']
	delivery_item_id = data['delivery_item_id']
	from_status = data['from_status']
	to_status = data['to_status']

	# 订阅快递推送
	topic_name = TOPIC['base_service']
	data = {
		"delivery_item_id": delivery_item_id,
		"corp_id": corp_id
	}
	msgutil.send_message(topic_name, 'send_delivery_item_phone_message_task', data)

	# 释放出货单资源
	Resource.use('gaia').put({
		"resource": 'order.released_delivery_item',
		"data": {
			'corp_id': corp_id,
			'id': delivery_item_id,
			'from_status': from_status,
			'to_status': to_status
		}
	})

# for product in delivery_item_data['products']:
#
# 	# 回退库存
# 	stock_infos = {
# 		'model_id': product['model_id'],
# 		'changed_count': product['count']
# 	}
#
# 	sale_data = {
# 		'id': product['id'],
# 		'stock_infos': json.dumps([stock_infos])
# 	}
#
# 	Resource.use('gaia').post({
# 		'resource': 'product.product_stock',
# 		'data': sale_data
# 	})
#
# 	# 回退销量
#
# 	if from_status != 'created' and product['promotion_info']['type'] != "premium_sale:premium_product":
# 		sale_data = {
# 			'id': product['id'],
# 			'changed_count': 0-product['count']
# 		}
#
# 		Resource.use('gaia').post({
# 			'resource': 'product.product_sale',
# 			'data': sale_data
# 		})
