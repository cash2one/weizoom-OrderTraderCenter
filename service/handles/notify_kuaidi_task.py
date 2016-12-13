# -*- coding: utf-8 -*-
"""
快递订阅
"""
from service.handler_register import register
from eaglet.utils.resource_client import Resource


@register("notify_kuadi_task")
def process(data, recv_msg=None):
	corp_id = data['corp_id']
	delivery_item_id = data['delivery_item_id']

	data = {
		'corp_id': corp_id,
		'delivery_item_id': delivery_item_id
	}
	Resource.use('gaia').put({
		'resource': 'delivery_item.notify_kuaidi',
		'data': data
	})


	