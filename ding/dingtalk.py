#coding: utf8
"""
DingTalk(钉钉)的SDK

* [API官方文档](http://open.dingtalk.com/doc/index.html)

# 如何通过code换取access_token？

参考“免登服务”一节。拿到code之后，获取用户信息。


"""
#import ssl
#ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#ctx.options &= ~ssl.OP_NO_SSLv3

#import requests.packages.urllib3.util.ssl_
##print(requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS)
#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'


import requests
import json
#import datetime as dt
#import codecs
import logging
from models import Token
import hashlib
try:
	import settings
	FOR_EAGLET = True
except:
	from django.conf import settings
	FOR_EAGLET = False


if settings.DING_FORCE_TLSV1:
	import ssl
	from requests.adapters import HTTPAdapter
	from requests.packages.urllib3.poolmanager import PoolManager

	class ForceTLSV1Adapter(HTTPAdapter):
		"""Require TLSv1 for the connection"""
		def init_poolmanager(self, connections, maxsize, block=False):
			# This method gets called when there's no proxy.
			self.poolmanager = PoolManager(
				num_pools=connections,
				maxsize=maxsize,
				block=block,
				ssl_version=ssl.PROTOCOL_TLSv1,
			)

		def proxy_manager_for(self, proxy, **proxy_kwargs):
			# This method is called when there is a proxy.
			proxy_kwargs['ssl_version'] = ssl.PROTOCOL_TLSv1
			return super(ForceTLSV1Adapter, self).proxy_manager_for(proxy, **proxy_kwargs)			


class DingApiException(Exception):
	pass


class DingTalk:

	CODE_INVALID_TOKEN = 40014

	USER_GAOLIQI = "01544340487177"
	USER_XIAOWEI = "01606068572211"

	# 部分问题沟通讨论组
	DING_CONVERSATION_COMPANY_ISSUE = "67500820"
	# 测试的讨论组
	DING_CONVERSATION_TEST = "80035247"
	# 研发问题沟通群
	DING_CONVERSATION_DEV_ISSUE = "62516703"
	# 运维通知群
	DING_CONVERSATION_DEV_MAINTAIN = "70034783"
	# "系统问题沟通群"
	DING_CONVERSATION_SYS_ISSUE = "76545601"	
	# 微众家项目群
	DING_CONVERSATION_WEIZHONGJIA = "80083502"
	# 互联网+项目
	DING_CONVERSATION_NETPLUS = "70668897"
	# 需求讨论群
	DING_CONVERSATION_PRODUCT_REQ = "108617190"


	#DATETIME_FORMAT="%Y-%m-%dT%H:%M:%S.%fZ"
	DEFAULT_TOKEN_NAME = "weizoom_ding"

	def __init__(self):
		self.ROOT_URL = "https://oapi.dingtalk.com"
		self.headers = {
			"Content-Type": "application/json",
			"Accept": "*/*",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
		}
		self.ssl_verified = False

		if settings.DING_FORCE_TLSV1:
			self.adapter = ForceTLSV1Adapter()


	def get_access_token(self):
		"""
		向Ding发消息
		"""
		res = requests.get("%s/gettoken?corpid=%s&corpsecret=%s" % ( \
			self.ROOT_URL, \
			settings.DING_CORP_ID, \
			settings.DING_CORP_SECRET), verify=self.ssl_verified)
		data = json.loads(res.content)
		if data.get('errcode', -1) == 0:
			access_token = data['access_token']
			print("Got access_token: {}".format(access_token))
			return access_token
		return ''

	def get_access_token_by_name(self, token_name):
		if FOR_EAGLET:
			token = Token.select().where(Token.token_name==token_name, Token.is_deleted==False).first()
			#token = Token.select().first()
			if token:
				return token.access_token

			logging.info("token: {}".format(token))
			access_token = self.get_access_token()
			Token.create(token_name=token_name, access_token=access_token)
		else:
			tokens = Token.objects.filter(token_name=token_name, is_deleted=False)
			if tokens.count()>0:
				return tokens[0].access_token

			access_token = self.get_access_token()
			Token.objects.create(token_name=token_name, access_token=access_token)
		return access_token


	def api_post(self, api_url, data):
		"""
		发送POST API

		@param api_url 形如`/message/send`的地址
		@param data dict对象
		"""
		max_error_times = 5
		res = None
		i = 0
		while i<max_error_times:
			access_token = self.get_access_token_by_name(self.DEFAULT_TOKEN_NAME)
			logging.info("access_token: %s" % (access_token))
			#logging.info("body: %s" % (body))
			#res = self._post_ding(access_token, "%s%s" % (self.ROOT_URL, api_url), body)
		
			url = "%s%s?access_token=%s" % (self.ROOT_URL, api_url, access_token)
			logging.info("API URL: %s" % url)
			logging.debug("api_post data: {}".format(data))
			
			if settings.DING_FORCE_TLSV1:
				s = requests.Session()
				s.mount('https://', self.adapter)
				res = s.post(url, headers=self.headers, verify=self.ssl_verified, json=data)
			else:
				res = requests.post(url, headers=self.headers, verify=self.ssl_verified, json=data)

			data = json.loads(res.content)
			if data.get('errcode') == self.CODE_INVALID_TOKEN: # invalid token
				Token.objects.filter(token_name=self.DEFAULT_TOKEN_NAME).delete()
			else:
				i = max_error_times # to break the loop
		return json.loads(res.content)


	def api_get(self, api_url, params={}):
		"""
		发送GET API
		"""
		max_error_times = 5
		res = None
		i = 0
		while i<max_error_times:
			access_token = self.get_access_token_by_name(self.DEFAULT_TOKEN_NAME)
			params['access_token'] = access_token
			if settings.DING_FORCE_TLSV1:
				s = requests.Session()
				s.mount('https://', self.adapter)
				res = s.get("%s%s" % (self.ROOT_URL, api_url), params=params, headers=self.headers, verify=self.ssl_verified)
			else:
				res = requests.get("%s%s" % (self.ROOT_URL, api_url), params=params, headers=self.headers, verify=self.ssl_verified)
			data = json.loads(res.content)
			if data.get('errcode') == self.CODE_INVALID_TOKEN: # invalid token
				Token.objects.filter(token_name=self.DEFAULT_TOKEN_NAME).delete()
			else:
				i = max_error_times # to break the loop
		return json.loads(res.content)


	def send_message(self, user_id, message="{}", agent_id="6614420"):
		"""
		发企业通知

		"""
		message = {
			"touser": user_id,
			"agentid": agent_id,
			"msgtype":"text",
			"text":{"content": message}
			}
		data = self.api_post("/message/send", message)
		#if data['errcode'] != 0:
		#	raise DingApiException()
		return data


	def send_oa_message(self, user_id, oa_message, agent_id="6614420"):
		"""
		发企业消息（直接传入dict对象）
		"""
		message = {
			"touser": user_id,
			"agentid": agent_id,
			"msgtype":"oa",
			"oa": oa_message
			}
		data = self.api_post("/message/send", message)
		return data


	def send_to_conversation(self, user_id, conversation_id, message, agent_id="6614420"):
		"""
		发送普通会话

		@note 获取conversation_id方法：在Web端查`con-id`。
		"""
		message = {
			"sender": user_id,
			"cid": conversation_id,
			"agentid": agent_id,
			"msgtype":"text",
			"text": {"content": message}
			}
		data = self.api_post("/message/send_to_conversation", message)
		if data['errcode'] != 0:
			logging.error("Error in calling `send_to_conversation`: user_id: {}, conversation_id: {}, agent_id: {},  message: {}, response: {}".format(user_id, conversation_id, agent_id, message, data))
		return data


	def send_oa_message_to_conversation(self, sender_id, conversation_id, oa_message, agent_id="6614420"):
		"""
		发送OA Message
		"""
		message = {
			"sender": sender_id,
			"cid": conversation_id,
			"agentid": agent_id,
			"msgtype":"oa",
			"oa": oa_message
			}
		data = self.api_post("/message/send_to_conversation", message)
		return data


	def get_department_list(self):
		"""
		获取部门列表
		"""
		data = self.api_get("/department/list")
		return data


	def get_user_list(self, department_id):
		"""
		获取用户列表
		"""
		param = {
			"department_id": department_id
		}
		data = self.api_get("/user/list", param)
		return data


	def get_user_simplelist(self, department_id):
		"""
		"""
		param = {
			"department_id": department_id
		}
		data = self.api_get("/user/simplelist", param)
		return data


	def get_userinfo(self, code):
		"""
		通过code换取用户身份

		@return 有4个参数: userid、deviceId、is_sys、sys_level
		@see http://open.dingtalk.com/doc/index.html?spm=a3140.7785475.0.0.NllGu6#通过code换取用户身份
		"""
		data = self.api_get("/user/getuserinfo", {'code': code})
		return data

	def get_user(self, userid):
		"""
		获取用户详情
		"""
		data = self.api_get("/user/get", {'userid': userid})
		return data

	def get_crm_customer(self):
		"""
		获取CRM客户列表

		@see http://ddtalk.github.io/dingTalkDoc/?spm=a3140.7785475.0.0.kGGfAO#获取客户列表
		"""
		data = self.api_get("/crm/customer/get", {})
		return data


	def register_callback(self, event_tags, token, aes_key, url):
		"""
		注册事件回调接口

		@see http://ddtalk.github.io/dingTalkDoc/?spm=a3140.7785475.0.0.kGGfAO#注册事件回调接口
		"""
		param = {
			"call_back_tag": event_tags,
			"token": token,
			"aes_key": aes_key,
			"url": url
		}
		data = self.api_post("/call_back/register_call_back", param)
		return data

	def get_jsapi_ticket(self):
		"""
		获取jsapi-ticket

		返回结果举例：
			{“errcode“:0,“errmsg“:“ok“,“expires_in“:7200,“ticket“:“pguShgfi0NwPQhQudw8DG4lyIZB4wdvTy4vkyxq4nbzp7Oaf7sXwJRJmnXNLx7vdr0eurog3YHYyni0FjhMROI“}
		"""
		param = {
			"type": "jsapi"
		}
		data = self.api_get("/get_jsapi_ticket", param)
		return data


	def create_signature(self, jsapi_ticket, noncestr, timestamp, url):
		"""
		创建jsapi认证的signature

		@see http://ddtalk.github.io/dingTalkDoc/?spm=a3140.7785475.0.0.QEzEHp#pc端开发文档
		"""

		#noncestr = "weizoom_weteam"
		plain = "jsapi_ticket={}&noncestr={}&timestamp={}&url={}".format(jsapi_ticket, noncestr, timestamp, url)
		h = hashlib.sha1()
		h.update(plain)
		sign = h.hexdigest()
		return sign
