# -*- coding: utf-8 -*-
"""
处理已支付的订单
"""
import time

from eaglet.core.sendmail import sendmail
from service.handler_register import register
from eaglet.utils.resource_client import Resource

ORDER_STATUS2NOTIFY_STATUS = {
	mall_models.ORDER_STATUS_NOT: mall_models.PLACE_ORDER,
	mall_models.ORDER_STATUS_PAYED_NOT_SHIP: mall_models.PAY_ORDER,
	mall_models.ORDER_STATUS_PAYED_SHIPED: mall_models.SHIP_ORDER,
	mall_models.ORDER_STATUS_SUCCESSED: mall_models.SUCCESSED_ORDER,
	mall_models.ORDER_STATUS_CANCEL: mall_models.CANCEL_ORDER
}


def __send_email(emails, content_described, content):
	for email in emails:
		sendmail(email, content_described, content)


@register("notify_kuadi_task")
def process(data, recv_msg=None):
	return
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


	