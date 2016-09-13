#coding: utf8
"""
业务数据交换消息BDEM(Business Data Exchange Message)工具
"""

import base64
from mns.account import Account
from mns.topic import TopicMessage
import json
import logging

try:
	import settings
except:
	from django.conf import settings

_mns_account = None

def send_message(topic_name, func_name, args):
	"""
	向MNS发消息
	"""
	global _mns_account
	if not _mns_account:
		_mns_account = Account(\
			settings.MNS_ENDPOINT, \
			settings.MNS_ACCESS_KEY_ID, \
			settings.MNS_ACCESS_KEY_SECRET, \
			settings.MNS_SECURITY_TOKEN)

	data = {
		'function': func_name,
		'args': args
	}

	topic = _mns_account.get_topic(topic_name)
	msg_body = json.dumps(data)
	msg_body = base64.b64encode(msg_body)
	#msg_tag = "important"
	message = TopicMessage(msg_body)
	re_msg = topic.publish_message(message)
	logging.info("Publish Message Succeed.\nMessageBody:%s\nMessageId:%s\nMessageBodyMd5:%s\n\n" % (msg_body, re_msg.message_id, re_msg.message_body_md5))
	return re_msg
