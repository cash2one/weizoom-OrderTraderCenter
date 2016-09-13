#coding: utf8

import logging

_SERVICE_LIST = {
}

def register(function_name):
	def wrapper(function):
		_SERVICE_LIST[function_name] = function
		logging.info("registered service: {} => {}".format(function_name, function))
		return function
	return wrapper


def call_function(function_name):
	return _SERVICE_LIST.get(function_name)
