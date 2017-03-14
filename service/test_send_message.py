# -*- coding: utf-8 -*-
from bdem import msgutil

topic_name = 'test-topic'


data = {
	"delivery_item_id": 100,
	"delivery_item_bid": '888888888'
}
msgutil.send_message(topic_name, 'test_send', data)
