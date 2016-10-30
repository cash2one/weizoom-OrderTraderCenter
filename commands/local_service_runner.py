# -*- coding: utf-8 -*-
"""
同步联系人

@author Victor
"""

import json
import logging

from eaglet.utils.command import BaseCommand
from eaglet.core.cache import utils as cache_util
from eaglet.core.exceptionutil import unicode_full_stack

import settings
import service #load all message handlers
from service import handler_register

class DummyMessage():
	receipt_handle = 'handle'
	message_body = None
	message_id = None

	def __init__(self):
		pass


class Command(BaseCommand):
	help = "python manage.py local_service_runner"
	args = ''


	def handle(self, *args, **options):
		if len(args)<1:
			print "usage: <json file>"
			return

		with open(args[0]) as data_file:
			data = json.load(data_file)
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
		return
