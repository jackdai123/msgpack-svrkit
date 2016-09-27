#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys

def Client(service, caller):
	rpc_cli_dir = os.path.dirname(os.path.abspath(__file__))
	module_name = service + '_rpc_cli'
	cliconf = os.path.join(rpc_cli_dir, module_name+'.conf')
	clipy = os.path.join(rpc_cli_dir, module_name+'.py')

	if not os.path.exists(cliconf):
		raise IOError('%s not exists' % (cliconf))
	if not os.path.exists(clipy) and \
		not os.path.exists(clipy + 'c'):
		raise IOError('%s and %sc not exists' % (clipy, clipy))

	if rpc_cli_dir not in sys.path:
		sys.path.append(rpc_cli_dir)
	module = __import__(module_name)
	return module.Client(conffile = cliconf, caller = caller)

