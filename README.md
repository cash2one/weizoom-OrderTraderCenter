**用Python开发消息服务的codebase（基于阿里MNS消息服务）**

# 安装必要组件

```
pip install -U "peewee==2.6.4"
pip install git+https://git2.weizzz.com:84/microservice/eaglet.git
pip install -U git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git
```

生成API文档：
```
swagger-codegen generate -i openapi.json -l html -o html
```

# 配置数据库

在mysql console中执行：
```
CREATE DATABASE redagent DEFAULT CHARSET UTF8;
GRANT ALL ON redagent.* to 'redagent'@'%' IDENTIFIED BY 'Weizoom!';
```

在shell中执行：
```
bash rebuild.sh
```

# 构建Docker镜像

```
bash build_docker.sh
```
