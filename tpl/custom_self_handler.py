#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import time

class process:
	def __init__(self, worker_id, args):
		self.worker_id		= worker_id
		self.args			= args
		self.do()

	def do(self):
		while 1:
			print '%s thread%d %s' % (os.path.splitext(os.path.basename(__file__))[0], self.worker_id, self.args)
			time.sleep(5)

