#!/bin/bash

cd /service

#bash rebuild.sh

rm -f `find . -name '*.pyc'`

while true; do
	python manage.py service_runner
done
