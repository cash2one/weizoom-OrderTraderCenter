# -*- coding: utf-8 -*-
"""
添加客户的信息

@author Victor
"""

import settings

from redmine import Redmine
#from redmine.exceptions import ResourceNotFoundError

import logging

from commands.service_register import register
from customer_update_service import CUSTOM_FIELD_SALEAGENT, CUSTOM_FIELD_SALENAME


XUNENG_GROUP = 44	#续能组
QUDAO_GROUP = 14	#渠道管理组


@register("customer.add")
def customer_add_service(data, raw_msg=None):
	"""
	创建用户的service

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
		}			
	}
	```

	@param args dict格式的参数
	"""
	rm = Redmine(settings.REDMINE_HOST, key=settings.REDMINE_KEY)

	args = data['customer']

	# 自定义属性
	custom_fields = []
	if 'sale_agent' in args:
		custom_fields.append({'id': CUSTOM_FIELD_SALEAGENT, 'value': args.get('sale_agent', '')}) # '销售代理'
	if 'sale_name' in args:
		custom_fields.append({'id': CUSTOM_FIELD_SALENAME, 'value': args.get('sale_name')}) # 销售
	
	customer_id = args['customer_id']
	customer = rm.project.create(
		name=args['customer_name'],
		identifier=customer_id, 
		description=args.get('description', ''),
		homepage=args.get('homepage', ''), 
		is_public=args.get('is_public', False),
		inherit_members=True,
		custom_fields = custom_fields,
	)

	logging.info("customer {} info: {}".format(customer.identifier, customer))
	
	# TODO: 添加联系人信息
	contact_name = args.get('contact')
	if contact_name:
		rm.contact.create(
			project_id = customer.id,
			first_name = contact_name,
			company = args['customer_name'],
			phones = list(set([args.get('tel', ''), args.get('cell', '')])),
			emails = args.get('email', ''),
			is_company = False,
			visibility = 0, # 0-project, 1-public, 2-private
		)

	# 分配销售组信息
	try:
		agent_name = args.get('agent', '')
		if agent_name == u'微众直销' and agent_name == u'微众采销':
			user_id = XUNENG_GROUP
		else:
			user_id = QUDAO_GROUP

		# 清除membership关系
		memberships = rm.project_membership.filter(project_id=customer_id)
		need_assign_group = True
		for membership in memberships:
			if hasattr(membership, 'group'):
				logging.info("customer_id: {}, group: {}/{}".format(customer_id, membership.group['id'], membership.group['name'].encode('utf8')))
				if membership.group['id'] == user_id:
					# 如果已经有了此组ID，无需更新
					need_assign_group = False
					logging.info("{} is already assigned to '{}'".format(user_id, customer_id))
				else:
					# 删除非此user_id的其他group
					try:
						rm.project_membership.delete(membership.id)
					except Exception as e:
						logging.info("cleaning memberships, customer_id {}, exception: {}".format(customer_id, e))
		
		if need_assign_group:
			try:
				membership = rm.project_membership.create(project_id=customer_id, user_id=user_id, role_ids=[3])
				logging.info("[{}] is assigned to '{}'".format(user_id, customer_id))
			except Exception as e:
				logging.info("Failed to add membership: {}".format(e))
				membership = None
	except Exception as e:
		logging.info("identifier:{}, exception: {}".format(customer_id, e))
	return
