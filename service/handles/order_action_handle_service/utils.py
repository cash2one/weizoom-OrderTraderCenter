# -*- coding: utf-8 -*-

from eaglet.utils.resource_client import Resource


def update_member_pay_info(corp_id, order_id, from_status, to_status):
	# order = Resource.use('gaia').get({
	# 	'resource': 'order.order',
	# 	'data': {
	# 		'corp_id': corp_id,
	# 		'id': order_id
	# 	}
	# })

	# member_id = order['member_info']['id']

	Resource.use('gaia').post({
		'resource': 'member.member_pay_info',
		'data': {
			'corp_id': corp_id,
			'order_id': order_id,
			'from_status': from_status,
			'to_status': to_status

		}
	})


def update_member_order_integral(corp_id, order_id, from_status, to_status):
	Resource.use('gaia').post({
		'resource': 'member.member_order_integral',
		'data': {
			'corp_id': corp_id,
			'order_id': order_id,
			'from_status': from_status,
			'to_status': to_status

		}
	})


def update_member_order_spread_integral(corp_id, order_id, from_status, to_status):
	Resource.use('gaia').post({
		'resource': 'member.member_order_spread_integral',
		'data': {
			'corp_id': corp_id,
			'order_id': order_id,
			'from_status': from_status,
			'to_status': to_status

		}
	})


def update_member_order_grade(corp_id, order_id):
	order = Resource.use('gaia').get({
		'resource': 'order.order',
		'data': {
			'corp_id': corp_id,
			'id': order_id
		}
	})

	member_id = order['member_info']['id']

	Resource.use('gaia').post({
		'resource': 'member.member_order_spread_integral',
		'data': {
			'corp_id': corp_id,
			'order_id': member_id,

		}
	})
