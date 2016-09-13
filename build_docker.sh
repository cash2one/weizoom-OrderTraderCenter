#!/bin/bash
DEPEND_IMAGE=`grep '^FROM' Dockerfile |awk '{print $2}'`
docker pull $DEPEND_IMAGE

NAME=reg.weizzz.com:5000/wz/redmine-agent:1.0
docker build --rm -t $NAME $@ . \
 && docker push $NAME
