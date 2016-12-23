# -*- coding: utf-8 -*-
"""
处理demo_data_created消息(演示)

@author Victor
"""
import os
import sys
import xlsxwriter
import time
import json
import re

from eaglet.utils.resource_client import Resource
from eaglet.core import watchdog, upyun_util
from eaglet.core.exceptionutil import unicode_full_stack

from django.conf import settings

import logging
from datetime import datetime
from service.handler_register import register
from db import models

COUNT_PER_PAGE = 100


@register("order_export_job_created")
def handler(data, recv_msg=None):
	"""
	订单导出
	"""
	logging.info("processing message data: {}".format(data))
	job_id = data['job_id']

	job = models.ExportJob.select().dj_where(id=job_id).first()
	if not job:
		return
	data = {
		'filters': job.param if job.param else '{}',
		'corp_id': job.woid,
		'count_per_page': COUNT_PER_PAGE
	}

	cur_page = 1
	
	total_order_count = 0
	finished_order_count = 0
	total_product_money = 0
	total_pay_money = 0
	total_cash = 0
	total_weizoom_card_money = 0
	total_premium_product = 0
	total_integral_money = 0
	total_coupon_money = 0
	total_refunded_cash = 0
	total_refunded_weizoom_card_money = 0
	total_refunded_coupon_money = 0
	total_refunded_integral_money = 0

	payment_type = {
		'unknown': u'',
		'alipay': u'支付宝',
		'weixin_pay': u'微信支付',
		'weizoom_coin': u'微众卡支付',
		'cod': u'货到付款',
		'preference': u'优惠抵扣',
		'best_pay': u'翼支付',
		'kangou_pay': u'看购支付',
	}

	status_code_type = {
		'created': u'待支付',
		'cancelled': u'已取消',
		'paid': u'待发货',
		'shipped': u'已发货',
		'finished': u'已完成',
		'refunding': u'退款中',
		'refunded': u'退款成功'
	}

	orders_title = [u'订单号', u'下单时间', u'付款时间', u'来源' , u'商品名称', u'规格',
		 u'商品单价', u'商品数量', u'销售额', u'商品总重量（斤）', u'支付方式', u'支付金额',
		 u'现金支付金额', u'微众卡', u'运费', u'积分抵扣金额', u'优惠券金额',
		 u'优惠券名称', u'订单状态', u'购买人', u'收货人', u'联系电话', u'收货地址省份',
		 u'收货地址', u'发货人', u'发货人备注',u'物流公司', u'快递单号',
		 u'发货时间',u'商家备注',u'用户备注', u'是否首单']
	mall_type = True
	if mall_type:
		orders_title[3] = u"供货商"
		orders_title[13] = u"微众卡支付金额"
		#退现金金额
		total_refund_money = 0.0
		#退微众卡金额
		total_refund_weizoom_card_money = 0.0
		#退优惠券金额
		total_refund_coupon_money = 0.0
		#退积分抵扣金额
		total_refund_integral_money = 0.0
		for i in [u'退积分抵扣金额', u'退优惠券金额', u'退微众卡金额', u'退现金金额']:
			orders_title.insert(19, i)

	has_supplier = False
	if mall_type:
		has_supplier = True

	filename = "order_{}.xlsx".format(job_id)
	dir_path_excel = "excel"
	PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))
	UPLOAD_DIR = os.path.join(PROJECT_HOME, '..','static', 'upload')
	dir_path = os.path.join(UPLOAD_DIR, dir_path_excel)
	file_path = "{}/{}".format(dir_path,filename)
	workbook   = xlsxwriter.Workbook(file_path)
	table = workbook.add_worksheet()

	table.write_row('A1', orders_title)
	tmp_line = 2
	processed_count = 0
	#try:
	while True:
		data['cur_page'] = cur_page
		orders = []
		resp = Resource.use('gaia').get({
			'resource': 'order.orders',
			'data': data
		})

		orders.extend(resp['data']['orders'])

		page_info = resp['data']['page_info']
		job.count=page_info.get('object_count',0)
		job.save()
		
		for order in orders:
			
			#统计信息
			final_price = order['final_price']
			weizoom_card_money = order['weizoom_card_money']
			pay_money = order['pay_money']
			integral_money = order['integral_money']
			coupon_money = order['coupon_money']
			if order['status_code'] != 'cancelled' and order['status_code'] != 'created':
				#现金支付金额
				total_cash += float(final_price)
				#微众卡支付总金额
				total_weizoom_card_money += float(weizoom_card_money)
				#支付总额
				total_pay_money += float(pay_money) 
				#积分抵扣总金额
				total_integral_money += float(integral_money)
				#优惠劵价值总额
				total_coupon_money += float(coupon_money)
			# 商品金额（总金额）
			product_price = order['product_price']
			total_product_money += float(product_price)

			created_at = order['created_at']
			pay_interface_type_code = payment_type.get(order['pay_interface_type_code'], u'')

			#购买人
			if order['member_info']:
				member_name = order['member_info']['name'].encode('utf8') if order['member_info']['name'] else '-'
				username = re.sub((r'\<span.*?\<\/span\>'),'口',member_name)
				buyer_name = username.decode('utf8')
			else:
				buyer_name = u'未知'
			#收货人信息
			ship_name = order['ship_name']
			ship_tel = order['ship_tel']
			ship_area = order['ship_area_text']
			ship_address = order['ship_address']

			#商家备注
			remark = u'-'

			if order['refunding_info']:
				#订单退款信息（已成功）
				refunding_info = order['refunding_info']

				refund_weizoom_card_money = refunding_info['weizoom_card_money']
				refund_coupon_money = refunding_info['coupon_money']
				refund_integral_money = refunding_info['integral_money']
				refund_money = refunding_info['cash']

				#退款金额统计
				total_refunded_cash += refund_money
				total_refunded_weizoom_card_money += refund_weizoom_card_money
				total_refunded_coupon_money += refund_coupon_money
				total_refunded_integral_money += refund_integral_money
			
			#是否首单
			is_first_order = u'首单' if order['is_first_order'] else u'非首单'

			#订单统计
			order_status_code = order['status_code']
			if order_status_code == 'finished':
				#已完成订单
				finished_order_count += 1
			#总订单	
			total_order_count += 1

			supplier_list = []
			order_count = 0
			for delivery_item in order['delivery_items']:

				delivery_bid = delivery_item['bid']

				#供货商信息
				if delivery_item['supplier_info']:
					supplier_info = delivery_item['supplier_info']
					supplier_name = supplier_info['name']
				
				#订单状态
				status_code = status_code_type.get(delivery_item['status_code'], u'失败')

				#发货人信息
				if delivery_item['leader_name']:
					leader_info = delivery_item['leader_name'].split('|')
				else:
					leader_info = ['-','-']
				leader_name = leader_info[0]
				leader_remark = leader_info[1] if len(leader_info)==2 else '-'
				#leader_remark = leader_info[1]
 				express_company_name_value = delivery_item['express_company_name_text'] if delivery_item['with_logistics'] else '-'
				express_number = delivery_item['express_number'] if delivery_item['with_logistics'] else '-'
				postage_time = delivery_item['created_at'] if delivery_item['with_logistics'] else '-'

				#缺的字段  '商品重量' '采购价' '赠品'

				#详细物流信息
				# express_details = delivery_item['express_details']
				# if express_details:
				# 	print "=============",express_details
				# 	1/0
				# ?采购价（不确定）
				# total_purchase_price = order['total_purchase_price']
				# if total_purchase_price:
				# 	print ">>>>>>>>>>>>>>>>>>>>",total_purchase_price
				# 	1/0

				#出货单退款信息
				refunding_info = delivery_item['refunding_info']

				refund_weizoom_card_money = refunding_info['weizoom_card_money']
				refund_coupon_money = refunding_info['coupon_money']
				refund_integral_money = refunding_info['integral_money']
				refund_money = refunding_info['cash']
				refund_is_finished = refunding_info['finished']
				i = 0
				for product in delivery_item['products']:
					name = product['name']
					origin_price = product['origin_price']
					count = product['count']
					# 销售额
					sales= product['sale_price']*product['count']
					# 商品总重量
					total_product_height = int(product['weight'] or 0)*product['count']


					#赠品
					promotion_info = product['promotion_info']
					if promotion_info['type'] == 'premium_sale:premium_product':
						total_premium_product += 1

					#商品规格
					product_model = ''
					if product['product_model_name_texts']:
						product_model_len = len(product['product_model_name_texts'])
						for i in range(0,product_model_len):
							tmp_product_model = product['product_model_name_texts'][i]
							product_model += tmp_product_model
					#支付金额
					pay_money = u'-'
					#微众卡支付金额
					weizoom_card_money = u'-'
					#运费
					postage = u'-'
					#积分抵扣金额
					integral_money = u'-'
					#优惠券金额
					coupon_money = u'-'
					#优惠券名称
					coupon_name = u'-'
					#用户备注
					customer_message = u'-'
					#付款时间
					payment_time = u'-'

					#某些信息只在第一个出货单上显示
					if order_count == 0:
						pay_money = order['pay_money']
						final_price = order['final_price']
						weizoom_card_money = order['weizoom_card_money']
						postage = order['postage']
						integral_money = order['integral_money']
						coupon_money = order['coupon_money']
						payment_time = order['payment_time']
						extra_coupon_info = order['extra_coupon_info']

						if extra_coupon_info:
							if extra_coupon_info['type'] == "multi_products_coupon":
								coupon_name = extra_coupon_info['name'] + u'（多品券）'
							elif extra_coupon_info['type'] == "all_products_coupon":
								coupon_name = extra_coupon_info['name'] + u'（通用券）'
							else:
								coupon_name = u'无'
						else:
							coupon_name = u'无'

						#判断订单状态是否为已取消
						if delivery_item['status_code'] == 'cancelled':
							payment_time = '-'
							# final_price = u'0'
							coupon_money = u'0'
							coupon_name = u'无'
						if delivery_item['status_code'] == 'created':
							weizoom_card_money = u'0'
							integral_money = u'0'
							payment_time = u'-'

						remark = order['remark'] if order['remark'] else u'-'
					else:
						#现金支付金额
						final_price = u'-'

					#用户备注（留言）处理
					customer_message = delivery_item['customer_message'] if delivery_item['customer_message'] else u'-'
					# if order['customer_message'] != '{}' and order['customer_message'] != '':
					# 	de_bid = delivery_bid.split('^')[1]
					# 	dev_customer_message = json.loads(order['customer_message'])
					# 	if de_bid in dev_customer_message:
					# 		#print dev_customer_message,de_bid
					# 		customer_message = dev_customer_message.get(de_bid, u'-')['customer_message']
					# 		#print customer_message
					# 	else:
					# 		customer_message = u'-'
					if i==0:
						tmp_order = [
							delivery_bid, 
							created_at, 
							payment_time, 
							supplier_name, 
							name,
							product_model,
							origin_price,
							count,
							sales,
							total_product_height,
							pay_interface_type_code,
							pay_money,
							final_price,
							weizoom_card_money,
							postage, 
							integral_money,
							coupon_money,
							coupon_name,
							status_code,
							buyer_name,
							ship_name,
							ship_tel,
							ship_area,
							ship_address,
							leader_name,
							leader_remark,
							express_company_name_value,
							express_number,
							postage_time,
							remark,
							customer_message,
							is_first_order,
						]
					else:
						tmp_order = [
							delivery_bid, 
							created_at, 
							payment_time, 
							supplier_name, 
							name,
							product_model,
							origin_price,
							count,
							sales,
							total_product_height,
							pay_interface_type_code,
							u'-',
                            u'-',
                            u'-',
                            u'-',
                            u'-',
                            u'-' if order['status_code'] == 'created' and coupon_name else coupon_money,
                            u'-' if order['status_code'] == 'created' or not coupon_name else coupon_name,
							status_code,
							buyer_name,
							ship_name,
							ship_tel,
							ship_area,
							ship_address,
							leader_name,
							leader_remark,
							express_company_name_value,
							express_number,
							postage_time,
							remark,
							customer_message,
							is_first_order,
						]

					if mall_type:
						#供货商相同只在第一列展示
						if supplier_name not in supplier_list and (status_code==u'退款成功' or status_code==u'退款中'):
							tmp_order.insert(19, refund_integral_money)
							tmp_order.insert(19, refund_coupon_money)
							tmp_order.insert(19, refund_weizoom_card_money)
							tmp_order.insert(19, refund_money)

							supplier_list.append(supplier_name)

						else:
							for i in xrange(4):
								tmp_order.insert(19,'-')
					# if has_supplier:
						# tmp_order.append(u'-' if 0.0 == product.purchase_price else product.purchase_price)
						# tmp_order.append(u'-'  if 0.0 ==product.purchase_price else product.purchase_price*relation.number)
						# tmp_order.append(u'采购价')
						# tmp_order.append(u'采购成本')
					table.write_row("A{}".format(tmp_line), tmp_order)
					tmp_line += 1
					i += 1
					#统计赠品总量
					if delivery_item['status_code'] != 'cancelled':
						pass
				order_count += 1
		totals = [
			u'总计',
			u'订单量:{}'.format(total_order_count),
			u'已完成:{}'.format(finished_order_count),
			u'商品金额:{}'.format(total_product_money),
			u'支付总额:{}'.format(total_pay_money),
			u'现金支付金额:{}'.format(total_cash),
			u'微众卡支付金额:{}'.format(total_weizoom_card_money),
			u'赠品总数:{}'.format(total_premium_product),
			u'积分抵扣总金额:{}'.format(total_integral_money),
			u'优惠劵价值总额:{}'.format(total_coupon_money)
		]
		if mall_type:
			webapp_type_list = [
				u'退现金金额:{}'.format(total_refunded_cash) ,
				u'退微众卡金额:{}'.format(total_refunded_weizoom_card_money) ,
				u'退优惠券金额:{}'.format(total_refunded_coupon_money) ,
				u'退积分抵扣金额:{}'.format(total_refunded_integral_money) ,
			]
			totals.extend(webapp_type_list)
		table.write_row("A{}".format(tmp_line), totals)
		job.processed_count=total_order_count
		job.save()
		if cur_page >= page_info['max_page']:
			break
		else:
			cur_page += 1
		
	workbook.close()
	upyun_path = '/upload/excel/{}'.format(filename)
	yun_url = upyun_util.upload_static_file(file_path, upyun_path)
	job.status=1
	job.file_path=yun_url
	job.update_at=datetime.now()
	job.save()
