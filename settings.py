# -*- coding: utf-8 -*-

import os
import logging

from eaglet.utils.resource_client import Resource

PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))

MODE = 'develop'
SERVICE_NAME = 'order_trade_center'
GAIA_DB = os.environ.get('GAIA_DB', None) or 'db.dev.com'

DATABASES = {
    'default': {
        'ENGINE': 'mysql+retry',
        #'NAME': 'new_zeus',
        'NAME': 'weapp',
        'USER': 'weapp',
        'PASSWORD': 'weizoom',
        'HOST': GAIA_DB,
        'PORT': '',
        'CONN_MAX_AGE': 100
    }
}


MIDDLEWARES = [    
    'eaglet.middlewares.debug_middleware.QueryMonitorMiddleware',
    'eaglet.middlewares.debug_middleware.RedisMiddleware',
    'middleware.mns_middleware.NotificationsMiddleware',

    #账号信息中间件
    #'middleware.webapp_account_middleware.WebAppAccountMiddleware',
]

# settings for WAPI Logger
if MODE == 'develop':
    WAPI_LOGGER_ENABLED = False # Debug环境下不记录wapi详细数据
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
    PAY_HOST = 'api.weapp.com'
    ENABLE_SQL_LOG = False

    logging.basicConfig(
        format='[%(asctime)s] %(name)s %(levelname)s %(message)s', 
        datefmt="%Y-%m-%d %H:%M:%S", 
        level=logging.INFO
    )
else:
    # 真实环境暂时关闭
    #WAPI_LOGGER_ENABLED = False
    # 生产环境开启API Logger
    WAPI_LOGGER_ENABLED = True
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
    PAY_HOST = 'api.weapp.com'
    ENABLE_SQL_LOG = False

    logging.basicConfig(
        format='[%(asctime)s] %(name)s %(levelname)s %(message)s', 
        datefmt="%Y-%m-%d %H:%M:%S", 
        level=logging.INFO
    )

if MODE == "deploy":
    DEBUG = False
else:
    DEBUG = True


#缓存相关配置
REDIS_HOST = os.environ.get('_REDIS_HOST', 'redis.weapp.com')
REDIS_PORT = 6379
REDIS_CACHES_DB = 1
REDIS_QUEUE_DB = 8
REDIS_CACHE_KEY = ':1:api'
MESSAGE_DEBUG_MODE = False

#BDD相关配置
WEAPP_DIR = '../weapp'
WEAPP_BDD_SERVER_HOST = '127.0.0.1'
WEAPP_BDD_SERVER_PORT = 8170
ENABLE_BDD_DUMP_RESPONSE = True

#watchdog相关
WATCH_DOG_DEVICE = 'mysql'
WATCH_DOG_LEVEL = 200
IS_UNDER_BDD = False


# Celery for Falcon
INSTALLED_TASKS = [
    #'resource.member.tasks',
    # 'core.watchdog.tasks',
    #'wapi.tasks',
    
    # 'services.example_service.tasks.example_log_service',
    # 'services.order_notify_mail_service.task.notify_order_mail',
    # 'services.record_member_pv_service.task.record_member_pv',
    # 'services.update_member_from_weixin.task.update_member_info',
]

# CTYPT_INFO = {
#     'id': 'weizoom_h5',
#     'token': '2950d602ffb613f47d7ec17d0a802b',
#     'encodingAESKey': 'BPQSp7DFZSs1lz3EBEoIGe6RVCJCFTnGim2mzJw5W4I'
# }
MAIL_NOTIFY_USERNAME = u'noreply@notice.weizoom.com'
MAIL_NOTIFY_PASSWORD = u'Weizoom2015'
MAIL_NOTIFY_ACCOUNT_SMTP = u'smtp.dm.aliyun.com'


H5_DOMAIN = 'h5.weapp.com'

MNS_ACCESS_KEY_ID = os.environ.get('MNS_ACCESS_KEY_ID', 'LTAICKQ4rQBofAhF')
MNS_ACCESS_KEY_SECRET = os.environ.get('MNS_ACCESS_KEY_SECRET', 'bPKU71c0cfrui4bWgGPO96tLiOJ0PZ')
MNS_ENDPOINT = os.environ.get('MNS_ENDPOINT', 'https://1615750970594173.mns.cn-beijing.aliyuncs.com/')
MNS_SECURITY_TOKEN = os.environ.get('MNS_SECURITY_TOKEN', '')

Resource.configure({"service_map": {'gaia': 'gaia@inner'}})
