# coding: utf8
import os
# 消息队列topic
TOPIC = {

	'base_service': os.environ.get('BASE_SERVICE_TOPIC', 'test-topic')  # 基础的异步化服务，如邮件，模板消息等

}
