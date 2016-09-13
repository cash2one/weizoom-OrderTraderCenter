# reg.weizzz.com:5000/wz/redmine-agent:1.0

FROM reg.weizzz.com:5000/wz/python27:1.0
MAINTAINER victor "gaoliqi@weizoom.com"

# install gcc for pycrypto
RUN yum -y install \
    python-requests \
    wget \
    git \
  && yum clean all

RUN pip install \
  MySQL-python \
  #'mongoengine==0.10.6' \
  'pymongo==2.8' \
  xlwt \
  xlrd \
  Image \
  #"beautifulsoup4<4.4" \
  "beautifulsoup<3.3" \
  pycrypto \
  #selenium \
  iso8601 \
  python-redmine \
  && rm -rf ~/.pip ~/.cache

RUN \
  pip install -U git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git &&\
  pip install -U git+https://git2.weizzz.com:84/microservice/dingtalk-sso.git &&\
  pip install -U git+https://git2.weizzz.com:84/microservice/eaglet.git

CMD ["bash", "/service/start.sh"]
