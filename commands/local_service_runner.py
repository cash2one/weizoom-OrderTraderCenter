# -*- coding: utf-8 -*-
"""
同步联系人

@author Victor
"""

import datetime
import array

from eaglet.utils.command import BaseCommand

from eaglet.core.cache import utils as cache_util
from bson import json_util
import json

import settings

from redmine import Redmine
from redmine.exceptions import ResourceNotFoundError

from ding.dingtalk import DingTalk

from eaglet.core.exceptionutil import unicode_full_stack
import logging

import service
from service import service_register

class DummyMessage():
	receipt_handle = 'handle'
	message_body = None
	message_id = None

	def __init__(self):
		pass


class Command(BaseCommand):
	help = "python manage.py sync_contacts"
	args = ''


	def handle(self, *args, **options):
		if len(args)<1:
			print "usage: <json file>"
			return

		with open(args[0]) as data_file:
			data = json.load(data_file)
			logging.info("data: {}".format(data))

			func_name = data['function']
			logging.info("Function: {}".format(func_name))
			logging.info(service_register.SERVICE_LIST)
			func = service_register.SERVICE_LIST.get(func_name)
			logging.info("func: {}".format(func))

			fake_msg = DummyMessage()
			fake_msg.message_body = data
			fake_msg.message_id = '0'
		
			func(data['args'], fake_msg)
		return
