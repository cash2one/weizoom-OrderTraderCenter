#!/bin/bash

NAME=reg.weizom.com/weizoom/order_trade_center:latest
VERSION=$(date +%Y%m%d%H%M)
TIMESTAMP_TAG=reg.weizom.com/weizoom/order_trade_center:$VERSION

docker images --format="{{.Repository}}:{{.Tag}}" | grep order_trade_center | xargs docker rmi
docker build --no-cache --rm -t ${NAME} -t ${TIMESTAMP_TAG} .

docker push ${NAME}
docker push ${TIMESTAMP_TAG}