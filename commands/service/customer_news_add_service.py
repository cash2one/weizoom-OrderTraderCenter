# -*- coding: utf-8 -*-
"""
创建客户的日志(News)

@author Victor
"""

import settings

from redmine import Redmine
#from redmine.exceptions import ResourceNotFoundError
import logging
from commands.service_register import register
from db.redmine import models as redmine_models
import datetime
import pytz


UTC = pytz.timezone('UTC')
CST = pytz.timezone('Asia/Shanghai')

def redmine_add_news(project_id, author_id, title, summary, description):
	"""
	创建Redmine中的news(Redmine没有提供API)
	"""
	now = datetime.datetime.now()
	now_utc = CST.localize(now).astimezone(UTC)
	news = redmine_models.News.create(
		project_id = project_id,
		title = title,
		summary = summary,
		description = description,
		author_id = author_id,
		created_on = now_utc,
		)
	return news


@register('customer_news.add')
def customer_news_add_service(data, raw_msg=None):
	"""
	更新或创建customer

	data格式:
	```
	{
		'news': {
			'author_username': 'gaoliqi',
			'author_name': '高立琦',
			'title': u'日志标题',
			'summary': u'日志摘要',
			'description': u'日志内容',
			'customer_id': 'wzc_123',
			'customer_name': u'北京好产品公司'
		}
	}
	```
	"""

	"""
	data = {
		'news': {
			'author_username': 'gaoliqi',
			'author_name': u'高立琦',
			'title': u'日志标题123',
			'summary': u'日志摘要',
			'description': u'这里是日志内容！',
			'customer_id': 'wzc_123',
			'customer_name': u'北京好产品公司'
		}
	}
	"""
	args = data['news']
	rm = Redmine(settings.REDMINE_HOST, key=settings.REDMINE_KEY)

	customer_id = args.get('customer_id')
	if customer_id:
		customer = rm.project.get(customer_id)
	else:
		customer_name = args.get('customer_name')
		customers = filter(lambda x: x.name == customer_name, rm.project.all())
		customer = None
		if len(customers)>0:
			customer = customers[0]
	# 如果没有给定customer_id，则用名字查

	# 获取用户
	users = rm.user.filter(name=args.get('author_username') or args.get('author_name'))
	if len(users)>0:
		user = users[0]
	else:
		user = None
	logging.info("customer: {}, author: {}".format(customer, user))

	# 创建news记录
	if customer and user:
		redmine_add_news(customer.id, user.id, args.get('title'), args.get('summary'), args.get('description'))
		logging.info("added news for customer [{}]".format(customer_id))

	#all_news = redmine_models.News.select()
	#for news in all_news:
	#	logging.info(u"title:{}, description:{}, author_id:{}".format(news.title, news.description, news.author_id))
	return
