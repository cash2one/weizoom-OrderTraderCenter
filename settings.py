# -*- coding: utf-8 -*-

import os
import logging


DEBUG = True
PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))

MODE = 'develop'
#MODE = 'deploy'
SERVICE_NAME = 'redmine-agent'

DATABASES = {
    'default': {
        'ENGINE': 'mysql+retry',
        'NAME': 'redagent',
        'USER': 'redagent',
        'PASSWORD': 'Weizoom!',
        'HOST': 'db.redmine-agent.com',
        'PORT': '',
        'CONN_MAX_AGE': 100
    },
    'redmine': {
        'ENGINE': 'mysql+retry',
        'NAME': 'redmine',
        'USER': 'root',                      
        'PASSWORD': 'secret',
        'HOST': 'db.redmine.com',
        'PORT': '',
        'CONN_MAX_AGE': 100
    }
}

if 'develop' == MODE:
    DATABASES['redmine']['HOST'] = 'ubuntu'
    DATABASES['redmine']['PORT'] = '13314'


MIDDLEWARES = [    
    'eaglet.middlewares.debug_middleware.QueryMonitorMiddleware',
    'eaglet.middlewares.debug_middleware.RedisMiddleware',

    #账号信息中间件
    #'middleware.webapp_account_middleware.WebAppAccountMiddleware',
]
#sevice celery 相关
EVENT_DISPATCHER = 'redis'

# settings for WAPI Logger
if MODE == 'develop':
    WAPI_LOGGER_ENABLED = False # Debug环境下不记录wapi详细数据
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
    PAY_HOST = 'api.weapp.com'
    #sevice celery 相关
    EVENT_DISPATCHER = 'local'
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


#缓存相关配置
REDIS_HOST = 'redis.weapp.com'
REDIS_PORT = 6379
REDIS_CACHES_DB = 1
REDIS_CACHE_KEY = ':1:api'

#BDD相关配置
WEAPP_DIR = '../weapp'
WEAPP_BDD_SERVER_HOST = '127.0.0.1'
WEAPP_BDD_SERVER_PORT = 8170
ENABLE_BDD_DUMP_RESPONSE = True

#watchdog相关
WATCH_DOG_DEVICE = 'mysql'
WATCH_DOG_LEVEL = 200
IS_UNDER_BDD = False
# 是否开启TaskQueue(基于Celery)
TASKQUEUE_ENABLED = True


# Celery for Falcon
INSTALLED_TASKS = [
    #'resource.member.tasks',
    # 'core.watchdog.tasks',
    'wapi.tasks',
    
    # 'services.example_service.tasks.example_log_service',
    # 'services.order_notify_mail_service.task.notify_order_mail',
    # 'services.record_member_pv_service.task.record_member_pv',
    # 'services.update_member_from_weixin.task.update_member_info',
]

#redis celery相关
REDIS_SERVICE_DB = 2

CTYPT_INFO = {
    'id': 'weizoom_h5',
    'token': '2950d602ffb613f47d7ec17d0a802b',
    'encodingAESKey': 'BPQSp7DFZSs1lz3EBEoIGe6RVCJCFTnGim2mzJw5W4I'
}

COMPONENT_INFO = {
    'app_id' : 'wx9b89fe19768a02d2',
}

# 本地服务器多线程支持开关
DEV_SERVER_MULTITHREADING = False

if 'deploy' == MODE:
    REDMINE_HOST = 'http://redmine.weizom.com:3000'
    # 小微机器人
    REDMINE_KEY = '553ef7b5b2c2271686f0c201a37e558f70d02f42'
else:
    # for development
    REDMINE_HOST = 'http://ubuntu:3000'
    REDMINE_KEY = '32047486b71e754465e42be5df84e546415dbd85'


#DING_CREATE_USER_IF_NOT_EXIST = True
#DING_DEFAULT_USER_PASSWORD = 'random_pass_54834875'
# 钉钉API的CORP_ID
DING_CORP_ID="ding0b2ce527846e5291" # 微众公司
DING_CORP_SECRET ="krWUpmV0Qw2CogbSENLt_VdkS5w7p0in8ID02zSmBnPkN6WXiyNXSeaE4VHwv4D-"
#HOST = "http://ftkpi.weapp.weizoom.com"

if 'deploy' == MODE:
    MNS_ACCESS_KEY_ID = 'LTAICKQ4rQBofAhF'
    MNS_ACCESS_KEY_SECRET = 'bPKU71c0cfrui4bWgGPO96tLiOJ0PZ'
    MNS_ENDPOINT = 'http://1615750970594173.mns.cn-hangzhou.aliyuncs.com/'
    MNS_SECURITY_TOKEN = ''
    SUBSCRIBE_QUEUE_NAME = 'redmine-agent'
else:
    MNS_ACCESS_KEY_ID = 'LTAICKQ4rQBofAhF'
    MNS_ACCESS_KEY_SECRET = 'bPKU71c0cfrui4bWgGPO96tLiOJ0PZ'
    MNS_ENDPOINT = 'http://1615750970594173.mns.cn-hangzhou.aliyuncs.com/'
    #MNS_ENDPOINT = 'http://1615750970594173.mns.cn-shanghai.aliyuncs.com/'
    MNS_SECURITY_TOKEN = ''
    SUBSCRIBE_QUEUE_NAME = 'test-redmine-agent'
