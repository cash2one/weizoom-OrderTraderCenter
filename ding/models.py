#coding: utf8

#from datetime import datetime

try:
	import settings
	from eaglet.core.db import models
except Exception as e:
	print(e)
	from django.conf import settings
	from django.db import models
#from django.contrib.auth.models import User
#from datetime import datetime
#import json
#import time


class Token(models.Model):
	"""
	DingTalk API token
	"""
	token_name = models.CharField(max_length=50, db_index=True)
	access_token = models.CharField(max_length=100)
	is_deleted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = "ding_token"
		#db_index = ('token_name',)


class DingAuthToken(models.Model):
	"""
	通过钉钉免密码登录（只有通过钉钉的jsapi openLink才可以）
	"""
	access_token = models.CharField(max_length=50, db_index=True)
	user_id = models.IntegerField(default=0)
	is_used = models.BooleanField(default=False) # 是否使用过（一次性）
	used_count = models.IntegerField(default=0) # 使用过次数
	expire_time = models.DateTimeField() # 失效时间

	class Meta(object):
		db_table = "ding_auth_token"
		#db_index = ('token_name',)
