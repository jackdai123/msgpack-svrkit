#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time

class process:
	def __init__(self, worker_id, args):
		self.worker_id = worker_id
		self.args = args
		self.do()

	def do(self):
		while 1:
			print self.worker_id
			time.sleep(5)

