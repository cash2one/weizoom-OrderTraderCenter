# -*- coding: utf-8 -*-

from eaglet.utils.resource_client import Resource


def update_member_pay_info(corp_id, order_id,to_status):
	order = Resource.use('gaia').get({
		'resource': 'order.order',
		'data': {
			'corp_id': corp_id,
			'id': order_id
		}
	})

	member_id = order['member_info']['id']


	member_order_statistics = Resource.use('gaia').get({

	})
