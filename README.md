# 用Python开发消息服务的codebase（基于阿里MNS消息服务）

# 安装必要组件

```
pip install -U "peewee==2.6.4"
pip install git+https://git2.weizzz.com:84/microservice/eaglet.git
pip install -U git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git
```

# 配置数据库

创建数据库：
```
mysql> CREATE DATABASE service DEFAULT CHARSET 'UTF8';
mysql> GRANT ALL ON service.* TO 'service'@'%' IDENTIFIED BY 'weizoom';
```

配置hosts文件：
```
127.0.0.1   db.service.com
```

# 启动service服务
```
python manage.py service_runner
```

或者执行：
```
bash start_service_runner.sh
```

# 本地调试

将待输入的message存入JSON文件，再执行`manage.py local_service_runner`。例如：
```
python manage.py local_service_runner test/test_demo.json
```

> **Message(消息)**是JSON格式的，必须包括`function`和`args`两个字段。例如：
> ```
> {
>   "function": "function_name",
>   "args": {
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
from service.service_register import register
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


# 生成API文档

```
bootprint swagger openapi.json html
```

> 执行 `npm install -g bootprint && npm install -g bootprint-swagger` 安装 `bootprint`。

# 构建Docker镜像

```
bash build_docker.sh
```
