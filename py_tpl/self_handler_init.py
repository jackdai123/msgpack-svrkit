#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import traceback

def process(self_group_name, self_worker_id, args):
	self_handler_dir = os.path.dirname(os.path.abspath(__file__))
	if self_handler_dir not in sys.path:
		sys.path.append(self_handler_dir)

	module_name = '%s_%s_self_handler' % (args['conf'].get('app', 'name'), self_group_name)
	try:
		module = __import__(module_name)
		module.process(self_worker_id, args)
	except Exception as e:
		print 'import %s module %s' % (module_name, traceback.format_exc())

