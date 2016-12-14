# -*- coding: utf-8 -*-
"""

SELECT * from market_tools_template_message;
+------+------------+------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+---------------------+
|   id |   industry | title                              |   send_point | attribute                                                                                                | created_at          |
|------+------------+------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+---------------------|
|    1 |          1 | TM00247-购买成功通知               |            0 | product:product_name,price:final_price,time:payment_time                                                 | 2014-12-04 19:49:54 |
|    2 |          1 | OPENTM200303341-商品发货通知       |            1 | keyword1: express_company_name, keyword2:express_number, keyword3:product_name,keyword4:number           | 2014-12-04 19:49:54 |
|    3 |          0 | TM00398-付款成功通知               |            0 | orderProductPrice:final_price,orderProductName:product_name,orderAddress:ship_address,orderName:order_id | 2014-12-04 19:49:54 |
|    4 |          0 | TM00505-订单标记发货通知           |            1 | orderProductPrice:final_price,orderProductName:product_name,orderAddress:ship_address,orderName:order_id | 2014-12-04 19:49:54 |
|    5 |          0 | OPENTM200474379-优惠券领取成功通知 |            2 | keyword1:coupon_name,keyword3:invalid_date                                                               | 2015-09-25 17:52:48 |
|    6 |          0 | TM00853-优惠券过期提醒             |            3 | orderTicketStore:coupon_store,orderTicketRule:coupon_rule                                                | 2015-09-25 17:52:48 |
|    7 |          0 | OPENTM207449727-任务完成通知       |            4 | keyword1:task_name,keyword2:prize,keyword3:finish_time                                                   | 2016-01-28 20:53:07 |
+------+------------+------------------------------------+--------------+----------------------------------------------------------------------------------------------------------+---------------------+
"""
# from django.conf import settings 
# settings.configure()
import settings
from eaglet.core.wxapi import get_weixin_api
from gaia_conf import TOPIC
from service.handler_register import register
from eaglet.utils.resource_client import Resource

TEMPLATE_DB_TITLE2TMS_NAME = {
	u"TM00247-购买成功通知": u"购买成功通知",
	u"OPENTM200303341-商品发货通知": u"商品发货通知",
	u"TM00398-付款成功通知": u"付款成功通知",
	u"TM00505-订单标记发货通知": u"订单标记发货通知",
	u"OPENTM200474379-优惠券领取成功通知": u"优惠券领取成功通知",
	u"TM00853-优惠券过期提醒": u"优惠券过期提醒",
	u"OPENTM207449727-任务完成通知": u"任务完成通知"
}
PAY_ORDER_SUCCESS = 0       #订单支付成功
PAY_DELIVER_NOTIFY = 1      #发货通知
COUPON_ARRIVAL_NOTIFY = 2   #优惠劵到账通知
COUPON_EXPIRED_REMIND = 3   #优惠劵过期提醒

class FakeObject(object):
	"""docstring for ClassName"""
	pass
		
@register("send_order_template_message_task")
def process(data, recv_msg=None):
	"""
	发货通知：测试的时候需准备测试数据，在页面上点发货即可
	"""
	corp_id = data['corp_id']
	# corp = Corporation(corp_id)
	to_status = data['to_status']
	topic = TOPIC['template_message']

	type = data['type']
	if type == 'delivery_item':
		delivery_item_id = data['delivery_item_id']

		# 获取出货单详情
		data_delivery_item = {
			'corp_id': corp_id,
			'delivery_item_id': delivery_item_id
		}
		resp_delivery_item = Resource.use('gaia').get({
			'resource': 'order.delivery_item',
			'data': data_delivery_item
		})
		delivery_item = resp_delivery_item['data']['delivery_item']

		# 获取订单详情
		order_id = delivery_item['origin_order_id']
		data_order = {
			'corp_id': corp_id,
			'id': order_id
		}
		resp_order = Resource.use('gaia').get({
			'resource': 'order.order',
			'data': data_order
		})
		order = resp_order['data']['order']

		if to_status == 'shipped':
			# 获取消息模板
			data_template_message = {
				'corp_id':corp_id,
				'send_point':PAY_DELIVER_NOTIFY
			}
			resp_template_message = Resource.use('gaia').get({
				'resource': 'mall.template_message',
				'data': data_template_message
			})
			template_message = resp_template_message['data']['template']

			"""
			"template": {
			      "status": 1,
			      "remark_text": "请您留意最近的快递信息，注意查收。如果有什么问题请第一时间在微信上直接与我们联系，米琦尔感谢您的支持。",
			      "first_text": "属于您的米琦尔生态富硒大米，已经从岗山硒谷国储级保鲜冷藏仓中取出并且已经发货",
			      "template_message_id": 2,
			      "created_at": "2014-12-05 09:49:49",
			      "id": 32,
			      "template_id": "toIz4WWt1ek8IY6GFB7UeLHg0uA61c53O0_2yDesi9o",
			      "owner_id": 102
		    }
			"""

			name = TEMPLATE_DB_TITLE2TMS_NAME[template_message.get('title','')]


			template_data = dict()
			if template_message:
				member_id = order['member_info']['id']
				data_member = {
					'corp_id':corp_id,
					'member_id':member_id
				}
				resp_member = Resource.use('gaia').get({
					'resource': 'member.member_openid',
					'data': data_member
				})
				openid = resp_member['data']['social_account']['openid']
				template_data['touser'] = openid
				template_data['template_id'] = template_message.get('template_id','')
				template_data['url'] = 'http://%s/mall/order_detail/?woid=%s&order_id=%s' % (settings.H5_DOMAIN, corp_id, order['bid'])
				# template_data['url'] = 'http://%s/mall/order_detail/?woid=%s&order_id=%s' % (H5_DOMAIN, corp_id, order['order_id'])
				template_data['topcolor'] = "#FF0000"
				detail_data = {}
				attribute = template_message.get('attribute','')
				detail_data["first"] = {"value" : template_message.get('first_text',''), "color" : "#000000"}
				detail_data["remark"] = {"value" : template_message.get('remark_text',''), "color" : "#000000"}
				order['express_company_name'] =  u'%s快递' % delivery_item['express_company_name_text']
				order['order_id'] = order.get('bid','')
				order['ship_address'] = order.get('ship_area_text','')+order.get('ship_address','')
				if attribute:
					attribute_data_list = attribute.split(',')
					for attribute_datas in attribute_data_list:
						attribute_data = attribute_datas.split(':')
						key = attribute_data[0].strip()
						attr = attribute_data[1].strip()
						if attr == 'final_price' and order.get(attr,''):
							value = u'￥%s［实际付款］' % order.get(attr,'')
							detail_data[key] = {"value" : value, "color" : "#173177"}
						elif order.get(attr,''):
							if attr == 'final_price':
								value = u'￥%s［实际付款］' % order.get(attr,'')
								detail_data[key] = {"value" : value, "color" : "#173177"}
							elif attr == 'payment_time':
								dt = datetime.now()
								payment_time = dt.strftime('%Y-%m-%d %H:%M:%S')
								detail_data[key] = {"value" : payment_time, "color" : "#173177"}
							else:
								detail_data[key] = {"value" : order.get(attr,''), "color" : "#173177"}
						else:
							order_products = order['delivery_items'][0]['products']
							if 'number' == attr:
								number = sum([product['count'] for product in order_products])
								detail_data[key] = {"value" : number, "color" : "#173177"}

							if 'product_name' == attr:
								products = order_products
								product_names =','.join([p['name'] for p in products])
								detail_data[key] = {"value" : product_names, "color" : "#173177"}
				template_data['data'] = detail_data

				# 获取微信用户的access_token
				data_mpuser_info = {
					'corp_id':corp_id,
				}
				resp_mpuser_info = Resource.use('gaia').get({
					'resource': 'weixin.mpuser_access_token',
					'data': data_mpuser_info
				})
				mpuser_access_token = resp_mpuser_info['data']['access_token']
				access_token = FakeObject()
				access_token.access_token = mpuser_access_token['access_token']
				weixin_api = get_weixin_api(access_token)
    			weixin_api.send_template_message(template_data, True)
