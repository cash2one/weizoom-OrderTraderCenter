# -*- coding: utf-8 -*-
"""
创建新用户service

@author Victor
"""

import logging
import string
import random
import logging
import settings

from redmine import Redmine
#from redmine.exceptions import ResourceNotFoundError

from commands.service_register import register

_DEFAULT_PASSWORD_LENGTH = 20

def _add_user(rm, info):
	#userid = info['userid']
	name = info.get('name')
	email = unicode(info.get('email').strip())

	password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in 
range(_DEFAULT_PASSWORD_LENGTH)),

	if email:
		try:
			# 不存在此用户
			login, _ = email.split('@')
			logging.info(u"adding user: {}/{}".format(name, email))
			rm_user = rm.user.create(login=login, \
				password=password, \
				firstname=name, \
				lastname='_', \
				mail=email, \
				auth_source_id=1, \
				mail_notification='selected', \
				must_change_passwd=False)
			logging.info(u"added user: {}/{}, id: {}".format(name, email, rm_user.id))
		except Exception as e:
			logging.info(e)

	# TODO: 增加分组信息
	return


@register("employee.add")
def employee_add_service(args, recv_msg=None):
	"""
	创建新用户

	```
	{"user_info": [{"userid": "01606068572211", "name": "\u5c0f\u5fae\u673a\u5668\u4eba", "email": "noreply@weizoom.com"}], "event_type": "user_modify_org"}
	```
	"""
	rm = Redmine(settings.REDMINE_HOST, key=settings.REDMINE_KEY)

	# TODO: 用userid
	for info in args['user_info']:
		_add_user(rm, info)
	return
