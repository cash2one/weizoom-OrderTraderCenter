# -*- coding: utf-8 -*-
"""
创建/更新客户的信息

@author Victor
"""

import settings

from redmine import Redmine
from redmine.exceptions import ResourceNotFoundError

import logging

from db.redmine import models as rmdb

from commands.service_register import register
from eaglet.utils import dateutil
import datetime
import pytz

GROUP_ZHIXIAO = 9 # 直销部
GROUP_CAIXIAO = 80 # 采销中心
GROUP_KEFUTONGZHI = 285 # 客服通知组

XUNENG_GROUP = 44	#续能组
QUDAO_GROUP = 14	#渠道管理组

CUSTOM_FIELD_SALEAGENT = 1
CUSTOM_FIELD_SALENAME = 3

UTC = pytz.timezone('UTC')
CST = pytz.timezone('Asia/Shanghai')

def assign_customer_service_group(rm, customer, args):
	customer_id = args['customer_id']

	# 分配销售组信息
	try:
		agent_name = args.get('agent', '')
		if agent_name == u'微众直销' and agent_name == u'微众采销':
			user_id = XUNENG_GROUP
		else:
			user_id = QUDAO_GROUP

		# 清除membership关系
		memberships = rm.project_membership.filter(project_id=customer_id)
		if len(memberships)==0:
			# 新分配分组
			try:
				rm.project_membership.create(project_id=customer_id, user_id=user_id, role_ids=[3])
				logging.info("[{}] is assigned to '{}'".format(user_id, customer_id))
			except Exception as e:
				logging.info("Failed to add membership: {}".format(e))
	except Exception as e:
		logging.info("identifier:{}, exception: {}".format(customer_id, e))	


def assign_sale_group(rm, customer, args):
	"""
	添加直销group
	"""
	sale_agent = args.get('sale_agent')
	customer_id = args['customer_id']

	# 分配销售组信息
	if customer and sale_agent == u'微众直销':
		user_id = GROUP_ZHIXIAO
	elif customer and (sale_agent == u'微众采销' or sale_agent == u'聚能团队'):
		user_id = GROUP_CAIXIAO
	else:
		user_id = 0

	if user_id>0:
		try:
			membership = rm.project_membership.create(project_id=customer.id, user_id=user_id, role_ids=[6])
			logging.info("[{}] is assigned to '{}'".format(user_id, customer_id))
		except Exception as e:
			try:
				memberships = rm.project_membership.filter(project_id=customer.id)
				selected = filter(lambda x:hasattr(x, 'group') and x.group['id'] == user_id, memberships)
				if len(selected)>0:
					membership = selected[0]
					#membership = memberships.get(0)
					membership.role_ids = [6]
					membership.save()
					logging.info("found existed membership {}".format(membership.id))
				else:
					logging.info("Failed to add membership: {}".format(e))
					membership = None
			except Exception as e:
				logging.info("Failed to add membership: {}".format(e))
				membership = None
	else:
		logging.info(u"Unassigned agent: {}".format(sale_agent))


def assign_operation_informing_group(rm, customer, args):
	"""
	添加运营通知组
	"""
	customer_id = args['customer_id']

	# 分配销售组信息
	user_id = GROUP_KEFUTONGZHI
	try:
		membership = rm.project_membership.create(project_id=customer.id, user_id=user_id, role_ids=[5]) # 5-报告人员
		logging.info("[{}] is assigned to '{}'".format(user_id, customer_id))
	except Exception:
		memberships = rm.project_membership.filter(project_id=customer.id)
		selected = filter(lambda x:hasattr(x, 'group') and x.group['id'] == user_id, memberships)
		if len(selected)>0:
			membership = selected[0]
			membership.role_ids = [5]
			membership.save()
			logging.info("[{}] is re-assigned to '{}'".format(user_id, customer_id))
	return

def set_customer_status(args):
	customer_status = args.get('status', 1) # 表示是否签约
	if customer_status==0:
		status = rmdb.PROJECT_STATUS_CLOSED
		# 更新customer.status(处于ARCHIVED的不改)
		query = rmdb.Project.update(status=status).dj_where(identifier=args['customer_id'], \
			status=rmdb.PROJECT_STATUS_ACTIVE)
		query.execute()
	else:
		status = rmdb.PROJECT_STATUS_ACTIVE
		query = rmdb.Project.update(status=status).dj_where(identifier=args['customer_id'], \
			status=rmdb.PROJECT_STATUS_CLOSED)
		query.execute()
	logging.info("set customer '{}' status to {}".format(args['customer_id'], status))
	return

def update_customer_created_on(args):
	if 'created_at' in args:
		# 参数传的是UST+8的，Redmine中记录UST+0时间
		created_at = dateutil.parse_datetime(args['created_at'])
		created_on = CST.localize(created_at).astimezone(UTC)
		query = rmdb.Project.update(created_on=created_on).dj_where(identifier=args['customer_id'])
		query.execute()
		logging.info("set customer '{}' created_on to {}".format(args['customer_id'], created_on))
	return

def create_or_update_customer(rm, args):
	# 自定义属性
	custom_fields = []
	if 'sale_agent' in args:
		custom_fields.append({'id': CUSTOM_FIELD_SALEAGENT, 'value': args.get('sale_agent', '')}) # '销售代理'
	if 'sale_name' in args:
		custom_fields.append({'id': CUSTOM_FIELD_SALENAME, 'value': args.get('sale_name')}) # 销售

	customer = None
	try:
		set_customer_status(args)

		customer = rm.project.get(args['customer_id'])
		customer.name = args['customer_name'].strip()
		customer.description = args.get('description', customer.description)
		customer.homepage = args.get('homepage', customer.homepage)
		if 'is_public' in args:
			customer.is_public = args['is_public']
		customer.custom_fields = custom_fields
		customer.save()
		logging.info("update customer : {}".format(customer))
	except ResourceNotFoundError:
		# customer不存在
		try:
			customer = rm.project.create(
				name=args['customer_name'].strip(),
				identifier=args['customer_id'],
				description=args.get('description', ''),
				homepage=args.get('homepage', ''),
				is_public=args.get('is_public', False),
				inherit_members=True,
				custom_fields = custom_fields
			)
			logging.info("add customer : {}".format(customer))

			set_customer_status(args)
		except Exception as e:
			logging.info("identifier:{}, exception: {}".format(args['customer_id'], e))
			customer = None
	except Exception as e:
		logging.info("customer_id: {}, exception: {}".format(args['customer_id'], e))

	# 更新created_on
	update_customer_created_on(args)
	return customer


def create_or_update_contact(rm, customer, args):
	contact_name = args.get('contact')
	contact = None
	if contact_name:
		# 如果有，则更新
		try:
			contacts = rm.contact.filter(project_id=customer.id, first_name = contact_name)
			contact = None
			if contacts and len(contacts)>0:
				contact = contacts[0]
				contact.company = args['customer_name'].strip()
				contact.phones = list(set([args.get('tel', ''), args.get('cell', '')]))
				contact.emails = [args.get('email', ''),]
				contact.save()
				logging.info("updated contact: {}".format(contact))
		except ResourceNotFoundError:
			contact = None

		if not contact:
			contact = rm.contact.create(
				project_id = customer.id,
				first_name = contact_name,
				company = args['customer_name'].strip(),
				phones = list(set([args.get('tel', ''), args.get('cell', '')])),
				emails = [args.get('email', '')],
				is_company = False,
				visibility = 0, # 0-project, 1-public, 2-private
			)
			logging.info("add contact: {}".format(contact))
	return contact

@register('customer.update_or_add')
def customer_update_or_add(data, raw_msg=None):
	"""
	更新或创建customer

	args格式
	```
	{
		'customer': {
			"customer_id": customer_id,
			"customer_name": cus.name.strip(),
			"customer_address": cus.address,
			"contact": cus.contact,
			"tel": cus.tel,
			"cell": cus.contact_tel,
			"email": cus.email,
			"sale_name": sale_name,
			"sale_id": str(cur_sale.id) if cur_sale else '-',
			"sale_agent": agent_name,
			"description": description,
			"status": 1,
			"created_on": "2016-09-01 12:34:56"
		}			
	}	
	"""
	rm = Redmine(settings.REDMINE_HOST, key=settings.REDMINE_KEY)
	args = data['customer']
	
	# 获取customer，不存在则创建
	customer = create_or_update_customer(rm, args)
	if customer and args.get('status', 1):
		# 分配客服
		assign_customer_service_group(rm, customer, args)

		# 分配直销
		assign_sale_group(rm, customer, args)
		
		# 添加"运营通知组"
		assign_operation_informing_group(rm, customer, args)

		# 添加/更新联系人信息
		create_or_update_contact(rm, customer, args)
	return
