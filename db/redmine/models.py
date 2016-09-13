#coding: utf8
"""
可以作为other_db的示例
"""
from eaglet.core.db import models
#import eaglet.peewee as peewee
# from playhouse.db_url import connect
from eaglet.core.hack_peewee import connect
import settings

import datetime


DB = settings.DATABASES['redmine']
db_redmine = None

if not db_redmine:
	DB_URL = '%s://%s:%s@%s/%s' % (DB['ENGINE'], DB['USER'], DB['PASSWORD'], \
		"%s:%s" % (DB['HOST'], DB['PORT']) if len(DB['PORT'])>0 else DB['HOST'], DB['NAME'])
	db_redmine = connect(DB_URL)
	db_redmine.connect()


PROJECT_STATUS_ACTIVE = 1
PROJECT_STATUS_CLOSED = 5 # 已关闭
PROJECT_STATUS_ARCHIVED = 9 # 已存档

class Project(models.Model):
	"""
	把Customer看做Project

	"""
	name = models.CharField(max_length=255, default='')
	description = models.TextField()
	homepage =models.CharField(max_length=255, default='')
	is_public = models.BooleanField(default=False)
	parent_id = models.IntegerField()
	created_on = models.DateTimeField(default=datetime.datetime.now)
	updated_on = models.DateTimeField(default=datetime.datetime.now)
	identifier = models.CharField(max_length=255)
	status = models.IntegerField(default=1)
	lft = models.IntegerField()
	rgt = models.IntegerField()
	inherit_members = models.BooleanField(default=False)
	default_version_id = models.IntegerField()

	class Meta:
		database = db_redmine
		db_table = "projects"


class News(models.Model):
	"""
	Redmine中的"日志"
	"""
	project_id = models.IntegerField(default=0)
	title = models.CharField(max_length=60, default='')
	summary = models.CharField(max_length=255, default='')
	description = models.TextField(default='')
	author_id = models.IntegerField()
	created_on = models.DateTimeField(default=datetime.datetime.now)
	comments_count = models.IntegerField(default=0)

	class Meta:
		database = db_redmine
		db_table = 'news'
		verbose_name = "Customer's Log"
		verbose_name_plural = "Customer's Log"
