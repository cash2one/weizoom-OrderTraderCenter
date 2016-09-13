# -*- coding: utf-8 -*-
"""DingTalk auth backend"""

try:
	# make it compatible with eaglet
	import settings
except:
	from django.conf import settings
import string
import random
import logging

__all__ = []

_DEFAULT_PASSWORD_LENGTH = 32

_DEFAULTS = {
	'DING_CREATE_USER_IF_NOT_EXIST': True,
	'DING_DEFAULT_USER_PASSWORD': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(_DEFAULT_PASSWORD_LENGTH)),
	'DING_FORCE_TLSV1': False,
}

for key, value in _DEFAULTS.items():
	try:
		getattr(settings, key)
	except AttributeError:
		setattr(settings, key, value)
	# Suppress errors from DJANGO_SETTINGS_MODULE not being set
	except ImportError as e:
		logging.info("ImportError: {}".format(e))
		pass
