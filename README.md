# 用Python开发消息服务的codebase（基于阿里MNS消息服务）

# 消息Service相关概念
## service
一个消息service是一个基于mns-service-base创建的service，最终会产生一个docker镜像，并在生产环境被部署。每一个service处理一类消息，一般来说，我们通常根据消息的来源来划分service，比如一个service处理来自商品管理的消息，另一个service处理来自订单管理的service。可以想到，一个service会处理多个消息。

## message handler
一个service会处理多个消息，每一种消息由一个`message handler`处理，一个message handler即是一个python函数：

```
from service.handler_register import register

@register("demo_data_created")
def handler(data, recv_msg=None):
	"""
	演示接收消息
	"""
	logging.info("processing message data: {}".format(data))
```

我们通过`register`这个decorator向service注册一个`message handler`，其中的`demo_data_created`是消息名。当service从消息中间件收到消息后，会根据消息种的消息名选择相应的`message handler`进行处理。

> 注意：当前一个消息只能对应一个`message handler`，如果为同一种消息注册两个handler，后注册的会覆盖先注册的handler

一般而言，在message handler的编程实践中，我们推荐使用`api service(比如gaia service)`进行读写数据的操作，而不是直接读写数据库，`api service`是微众微服务架构中唯一拥有数据库知识的service，这是一个架构层面的基本原则。但我们在mns-service-base中也引入了eaglet对数据库的支持，允许在特殊情况下直接访问数据库。再次强调：**我们强烈建议不要在event service中直接访问数据库**

# 安装必要组件

```
pip install -U "peewee==2.6.4"
pip install git+https://git2.weizzz.com:84/microservice/eaglet.git
pip install -U git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git
```

# 启动service服务
```
[linux]

bash start_service.sh
```

或者

```
[windows]
start_service.bat
```

启动后，service会向位于阿里云的消息中间件中的queue（queue在settings.py中配置）进行消息轮询，并处理消息

# 本地调试

1. 将待输入的message存入JSON文件
2. 执行`python manage.py local_service_runner`：
```
python manage.py local_service_runner test/test_demo.json
```

> **Message(消息)**是JSON格式的，必须包括`name`和`data`两个字段。`name`为消息名，由小写字母及下划线(_)组成，简要描述此消息用途。`data`为参数，是dict类型数据。例如：
> ```
> {
>   "name": "message_name",
>   "data": {
>       "key": "some_key",
>       "value": "some_value"
>      }
> }
> ```

# 编写一个service

步骤概要：

1. 在`service`下创建`.py`文件。比如`foo_service.py`。

2. 创建service function。例如：
```python
#coding: utf8
from service.handler_register import register
import logging
@register("foo.process")
def foo_process(data, recv_msg=None):
    """
    演示接收消息
    """
    logging.info("data: {}".format(data))
    logging.info("ReceiptHandle: {}".format(recv_msg.receipt_handle))
    logging.info("MessageBody: {}".format(recv_msg.message_body))
    logging.info("MessageID: {}".format(recv_msg.message_id))
    return
```

3. 在`service/__init__.py`中添加
```
import foo_service
```

4. 构造数据，本地调试：
```
./local_runner.sh test/foo.json
```

5. 部署线上环境。在生产环境中（如docker container）执行：
```
bash start_service.sh
```
即可对接MNS。

    > 注意：部署线上环境时须修改`settings.py`参数（比如MODE='deploy'，MNS_*等参数）

# 发送消息

请参考[mns_python_sdk](https://git2.weizzz.com:84/microservice/mns_python_sdk)。


# 生成API文档

```
bootprint swagger openapi.json html
```

> 执行 `npm install -g bootprint && npm install -g bootprint-swagger` 安装 `bootprint`。

# 构建Docker镜像

```
bash build_docker.sh
```
