# -*- coding: utf-8 -*-
"""
短信发送
"""
from service.handler_register import register
from eaglet.utils.resource_client import Resource


@register("send_delivery_item_phone_message_task")
def process(data, recv_msg=None):
	corp_id = data['corp_id']
	delivery_item_id = data['delivery_item_id']

	data = {
		'corp_id': corp_id,
		'delivery_item_id': delivery_item_id
	}
	Resource.use('gaia').put({
		'resource': 'delivery_item.phone_message',
		'data': data
	})

