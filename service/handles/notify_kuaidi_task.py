# -*- coding: utf-8 -*-
"""
快递订阅
"""
from service.handler_register import register
from eaglet.utils.resource_client import Resource
from eaglet.core import watchdog

@register("notify_kuaidi_task")
def process(data, recv_msg=None):
	corp_id = data['corp_id']
	delivery_item_id = data['delivery_item_id']
	data = {
		'corp_id': corp_id,
		'delivery_item_id': delivery_item_id
	}
	result = Resource.use('gaia').put({
		'resource': 'delivery_item.notify_kuaidi',
		'data': data
	})
	if resp and resp['code'] == 500:
		watchdog.error(u'快递订阅失败，corp_id:{}, delivery_item_id:{}'.format(corp_id,delivery_item_id) )


	