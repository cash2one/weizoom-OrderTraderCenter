# -*- coding: utf-8 -*-
"""


@author Victor
"""

from bdem import msgutil
from service.handler_register import register
from order_trade_center_conf import TOPIC
from service.utils import not_retry
import utils


@register("order_refunded")
@not_retry
def process(data, recv_msg=None):
	corp_id = data['corp_id']
	order_id = data['order_id']
	order_bid = data['order_bid']

	from_status = data['from_status']
	to_status = data['to_status']

	utils.update_member_pay_info(corp_id, order_id, from_status, to_status)
