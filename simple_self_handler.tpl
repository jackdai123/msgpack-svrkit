#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time

class process:
	def __init__(self, self_group_name, worker_id, args):
		self.self_group_name = self_group_name
		self.worker_id = worker_id
		self.args = args
		self.do()

	def do(self):
		while 1:
			print '%s_%d' % (self.self_group_name, self.worker_id)
			time.sleep(5)

