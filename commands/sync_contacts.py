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


class Command(BaseCommand):
	help = "python manage.py sync_contacts"
	args = ''

	def get_ding_userlist(self):
		# 获取钉钉数据
		self.ding = DingTalk()
		data = self.ding.get_department_list()
		for department in data['department']:
			logging.info(u"{}, {}".format(department['id'], department['name']))
		departments = data['department']

		data = self.ding.get_user_list(1)
		userlist = data['userlist']
		#logging.info(u"{}".format(data))
		#for user in userlist:
		#	logging.info(u"{}, {}, {}".format(user['userid'], user['name'], user['email']))
		return userlist, departments

	def sync_users(self):
		password = '#default_password#'
		depart_name2ids = dict() # depart_name => redmind.user.id
		for ding_user in self.userlist:
			email = unicode(ding_user['email'].strip())
			name = ding_user['name']

			if not email in self.existed_users:
				# 不存在此用户
				login, _ = email.split('@')
				logging.info(u"adding user: {}/{}".format(name, email))
				rm_user = self.rm.user.create(login=login, \
					password=password, \
					firstname=name, \
					lastname='_', \
					mail=email, \
					auth_source_id=1, \
					mail_notification='selected', \
					must_change_passwd=False)
			else:
				logging.info("existed user: {}".format(self.existed_users[email]))
				rm_user = self.existed_users[email]
			
			# 将rm_user.id 加到 depart_name 为key的dict中
			department_ids = ding_user.get('department', [])
			for depart_id in department_ids:
				department = self.id2departments[depart_id]
				depart_name = department['name']
				if not depart_name in depart_name2ids:
					ids = [rm_user.id]
					depart_name2ids[depart_name] = ids
				else:
					depart_name2ids[depart_name].append(rm_user.id)

		# 更新group中userids
		groups = self.rm.group.all()
		for group in groups:
			name = group.name
			if name in depart_name2ids:
				logging.info(u"group {} => {}".format(name, depart_name2ids[name]))
				self.rm.group.update(group.id, user_ids=depart_name2ids[name])

		return depart_name2ids


	def refresh_rm_groups(self):
		self.groups = self.rm.group.all()
		self.name2group = dict({group.name: group for group in self.groups})
		self.id2group = dict({group.id: group for group in self.groups})
		#for group in self.groups:
		#	print group.id, group.name
		return


	def sync_groups(self):
		"""
		同步ding departments => redmine group
		"""
		for depart in self.departments:
			name = depart['name']
			if not name in self.name2group:
				#logging.info(u"not existed group: {}".format(name))
				group = self.rm.group.create(name=name)
		self.refresh_rm_groups()
		logging.info("Redmine: {} groups".format(len(self.name2group)))
		return


	def handle(self, *args, **options):
		self.rm = Redmine(settings.REDMINE_HOST, key=settings.REDMINE_KEY)

		# 从钉钉得到的联系人
		self.userlist, self.departments = self.get_ding_userlist()
		# id->departments
		self.id2departments = dict({depart['id']: depart for depart in self.departments})

		# 同步联系人
		self.rm_userlist = self.rm.user.all()
		self.existed_users = dict({user.mail: user for user in self.rm_userlist})
		
		self.refresh_rm_groups()

		self.sync_groups()

		depart_name2ids = self.sync_users()
		#print existed_users
		return
