#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import importlib

class RPCTest:
	def __init__(self):
		rpc_test_name = os.path.splitext(os.path.basename(__file__))[0]
		service_name = rpc_test_name[:-9]
		self.rpc_proto = None
		self.cli = self._get_rpc_cli().Client(service=service_name, caller=rpc_test_name)

	def _get_rpc_cli(self):
		absolute_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
		for python_path in os.getenv('PYTHONPATH').split(':'):
			if absolute_path.startswith(python_path):
				rootpath = os.path.relpath(absolute_path, python_path).replace(os.path.sep, '.')
				self.rpc_proto = importlib.import_module('.rpc_proto.${app}_rpc_proto', rootpath)
				return importlib.import_module('.rpc_cli', rootpath)
		else:
			raise IOError('%s is not in PYTHONPATH' % (__file__))

