# -*- coding: utf-8 -*-
"""
测试发消息

@author Victor
"""

from eaglet.utils.command import BaseCommand
import logging

from utils import bdem_util

class Command(BaseCommand):
	help = "python manage.py send_message"
	args = ''

	def handle(self, *args, **options):
		topic_name = args[0] if len(args)>0 else 'test-customer-create'
		logging.info("topic name: {}".format(topic_name))

		# 示例数据
		data = {
			'customer': {
				"customer_id": "wzc_123",
				"customer_name": "北京好产品公司",
				"customer_address": "北京市海淀区中关村东路11号恒兴大厦",
				"contact": "周芷若",
				"tel": "13800138000",
				"cell": "010-62971234",
				"email": "zhouzhiruo@163.com",
				"sale_name": "张无忌",
				"sale_id": "saleno_123",
				"sale_agent": "微众直销",
				"description": "公司描述",
			}
		}

		func_name = "customer.add"
		#func_name = "customer.update_or_add"
		bdem_util.send_message(topic_name, func_name, data)
		return
