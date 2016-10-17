# -*- coding: utf-8 -*-
import falcon
import json
import logging
import base64
from service import service_register
from util import mns_util
from falcon.http_status import HTTPStatus
from eaglet.core.exceptionutil import unicode_full_stack


class NotificationsMiddleware(object):
	def process_request(self, req, resp):
		if req.path == "/notifications":
			if not mns_util.mns_authenticate(req):
				self.raise_response({"errmsg": "Access Forbidden!"}, falcon.HTTP_403)

			msg = mns_util.NotifyMessage()
			msg_type = "XML"
			body = req.stream.read()
			# print ">>>>>>>>>>", body
			if not mns_util.validate_body(body, msg, msg_type):
				self.raise_response({"errmsg": "Invalid Notify Message"}, falcon.HTTP_400)
			msg = msg.to_dict()
			logging.info("Receive Message Succeed! MessageBody:%s MessageID:%s" % (
						msg['message'], msg['message_id']))

			message = base64.decodestring(msg['message'])
			data = json.loads(message)
			function_name = data['name']
			func = service_register.find_service(function_name)
			status = falcon.HTTP_500
			if func:
				try:
					response = func(data['data'], msg)
					logging.info("service response: {}".format(response))
					status = falcon.HTTP_200
				except:
					logging.info(u"Service Exception: {}".format(unicode_full_stack()))
			else:
				logging.info(u"Error: no such service found : {}".format(function_name))

			# query_string = urllib.urlencode({'message': recv_msg['message']})
			# raise redirects.HTTPTemporaryRedirect("/notifications/HTTPEndpoint?{}".format(query_string))
			# resp = Resource.use('notifications', 'localhost:4180').post({'resource': 'HTTPEndpoint', 'data': {'message': recv_msg['message']} })
			self.raise_response({}, status)

	@staticmethod
	def raise_response(self, body, status=falcon.HTTP_200, headers=None):
		raise HTTPStatus(status, headers, json.dumps(body))
