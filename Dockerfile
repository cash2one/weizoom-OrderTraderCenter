# reg.weizzz.com:5000/wz/redmine-agent:1.0

FROM reg.weizom.com/wzbase/python27:1.0
MAINTAINER victor "gaoliqi@weizoom.com"

# install gcc for pycrypto
RUN yum -y install \
  #  python-requests \
    wget \
    git \
  && yum clean all

RUN pip install \
  #MySQL-python \
  #'mongoengine==0.10.6' \
  'pymongo==2.8' \
  xlwt \
  xlrd \
  Image \
  #"beautifulsoup4<4.4" \
  #"beautifulsoup<3.3" \
  pycrypto \
  #selenium \
  iso8601 \
  xlsxwriter \
  
  && rm -rf ~/.pip ~/.cache

RUN \
  pip install -U git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git &&\
  pip install -U git+https://git2.weizzz.com:84/microservice/dingtalk-sso.git &&\
  pip install -U git+https://git2.weizzz.com:84/microservice/eaglet.git
 ADD . /service
 WORKDIR /service
ENTRYPOINT ["/usr/local/bin/dumb-init", "/bin/bash", "start_service.sh"]