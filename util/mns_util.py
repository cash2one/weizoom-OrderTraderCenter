# -*- coding: utf-8 -*-

import logging
import json
import base64
import M2Crypto
import urllib2
from xml.dom.minidom import parseString


class NotifyMessage:
	def __init__(self):
		self.topic_owner = ""
		self.topic_name = ""
		self.subscriber = ""
		self.subscription_name = ""
		self.message_id = ""
		self.message_md5 = ""
		self.message_tag = ""
		self.message = ""
		self.publish_time = -1

	def __str__(self):
		"""
		msg_info = {"TopicOwner"    : self.topic_owner,
					"TopicName"     : self.topic_name,
					"Subscriber"    : self.subscriber,
					"SubscriptionName"  : self.subscription_name,
					"MessageId"     : self.message_id,
					"MessageMD5"    : self.message_md5,
					"MessageTag"     : self.message_tag,
					"Message"       : self.message,
					"PublishTime"   : self.publish_time}
		return "\n".join(["%s: %s"%(k.ljust(30),v) for k,v in msg_info.items()])
		"""
		return json.dumps(self.to_dict())

	def to_dict(self):
		return {
			"topic_owner": self.topic_owner,
			"topic_name": self.topic_name,
			"subscriber": self.subscriber,
			"subscription_name": self.subscription_name,
			"message_id": self.message_id,
			"message_md5": self.message_md5,
			"message_tag": self.message_tag,
			"message": self.message,
			"publish_time": self.publish_time,
		}


def mns_authenticate(request):
	"""
	MNS认证
	"""
	headers = request.headers
	service_str = "\n".join(sorted(["%s:%s" % (k.lower(), v) for k, v in headers.items() if k.startswith("X-MNS")]))
	# logging.info("service_str: {}".format(service_str))

	sign_header_list = []
	for key in ["CONTENT-MD5", "CONTENT-TYPE", "DATE"]:
		if key in headers.keys():
			sign_header_list.append(headers[key])
		else:
			sign_header_list.append("")
	# logging.info("sign_header_list: {}".format(sign_header_list))
	str2sign = "%s\n%s\n%s\n%s" % ("POST",
								   "\n".join(sign_header_list),
								   service_str,
								   request.path)
	logging.info("str2sign: [{}]".format(str2sign))

	# verify
	authorization = headers.get('AUTHORIZATION')
	logging.info("authorization: {}".format(authorization))
	signature = base64.b64decode(authorization)
	# logging.info("signature: {}".format(binascii.hexlify(signature)))
	cert_str = urllib2.urlopen(base64.b64decode(headers.get('X-MNS-SIGNING-CERT-URL'))).read()
	# logging.info("cert_str: {}".format(cert_str))
	pubkey = M2Crypto.X509.load_cert_string(cert_str).get_pubkey()
	pubkey.reset_context(md='sha1')
	pubkey.verify_init()
	pubkey.verify_update(str(str2sign))
	return pubkey.verify_final(signature)


def xml_decode(data, msg):
	if data == "":
		logging.error("Data is \"\".")
		return False
	try:
		d = parseString(data)
	except Exception, e:
		logging.error("Parse string fail, exception:%s" % e)
		return False

	node_list = d.getElementsByTagName("Notification")
	if not node_list:
		logging.error("Get node of \"Notification\" fail:%s" % e)
		return False

	data_dic = {}
	for node in node_list[0].childNodes:
		if node.nodeName != "#text" and node.childNodes != []:
			data_dic[node.nodeName] = str(node.childNodes[0].nodeValue.strip())

	key_list = ["TopicOwner", "TopicName", "Subscriber", "SubscriptionName", "MessageId", "MessageMD5", "Message",
				"PublishTime"]
	for key in key_list:
		if key not in data_dic.keys():
			logging.error("Check item fail. Need \"%s\"." % key)
			return False

	msg.topic_owner = data_dic["TopicOwner"]
	msg.topic_name = data_dic["TopicName"]
	msg.subscriber = data_dic["Subscriber"]
	msg.subscription_name = data_dic["SubscriptionName"]
	msg.message_id = data_dic["MessageId"]
	msg.message_md5 = data_dic["MessageMD5"]
	msg.message_tag = data_dic["MessageTag"] if data_dic.has_key("MessageTag") else ""
	msg.message = data_dic["Message"]
	msg.publish_time = data_dic["PublishTime"]
	return True


def validate_body(data, msg, msg_type):
	if msg_type == "XML":
		return xml_decode(data, msg)
	else:
		msg.message = data
	return True
