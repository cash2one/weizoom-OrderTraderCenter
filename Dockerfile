# reg.weizzz.com:5000/wz/redmine-agent:1.0

FROM reg.weizom.com/wzbase/python27:1.0
MAINTAINER victor "gaoliqi@weizoom.com"


RUN \
  pip install -U git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git &&\
  pip install -U git+https://git2.weizzz.com:84/microservice/dingtalk-sso.git &&\
  pip install -U git+https://git2.weizzz.com:84/microservice/eaglet.git
 ADD . /service
 WORKDIR /service
ENTRYPOINT ["/usr/local/bin/dumb-init", "/bin/bash", "start_service.sh"]