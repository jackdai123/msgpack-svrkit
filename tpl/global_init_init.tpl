#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import traceback

def init(args):
	global_init_dir = os.path.dirname(os.path.abspath(__file__))
	files = os.listdir(global_init_dir)
	if global_init_dir not in sys.path:
		sys.path.append(global_init_dir)
	loaded_modules = set()

	for f in files:
		if f.find('_global_init.py') == -1:
			continue

		module_name, ext = os.path.splitext(f)
		if module_name in loaded_modules:
			continue

		try:
			module = __import__(module_name)
			loaded_modules.add(module_name)
			module.init(args)
		except Exception as e:
			print 'import %s module %s' % (module_name, traceback.format_exc())

