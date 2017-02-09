# -*- coding: utf-8 -*-
"""
用于BDD调用中的入口文件
"""
import json
import logging
import base64

from eaglet.utils.command import BaseCommand

from commands.local_service_runner import DummyMessage

import service  # load all message handlers
from service import handler_register

class Command(BaseCommand):
	help = "python manage.py call_service_runner"
	args = ''

	def handle(self, *args, **options):
		data = json.loads(base64.b64decode(args[0]))
		logging.info("data: {}".format(data))
		msg_name = data['name']
		logging.info("message name: {}".format(msg_name))
		func = handler_register.find_message_handler(msg_name)
		if func:
			logging.info("service function: {}".format(func))

			fake_msg = DummyMessage()
			fake_msg.message_body = data
			fake_msg.message_id = '0'

			func(data['data'], fake_msg)
		else:
			logging.error("NO handler for message: %s", msg_name)


