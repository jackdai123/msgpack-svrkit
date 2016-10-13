#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import importlib

class handler:
	def __init__(self, args):
		self.args = args
		self.rpc_proto = None
		self._get_rpc_proto()

	def _get_rpc_proto(self):
		absolute_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
		for python_path in os.getenv('PYTHONPATH').split(':'):
			if absolute_path.startswith(python_path):
				rootpath = os.path.relpath(absolute_path, python_path).replace(os.path.sep, '.')
				self.rpc_proto = importlib.import_module('.rpc_proto.${app}_rpc_proto', rootpath)
				break
		else:
			raise IOError('%s is not in PYTHONPATH' % (__file__))

