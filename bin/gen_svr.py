#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import json
import getopt
import traceback
from gen_python import GenPythonCode
from gen_cpp import GenCppCode
#import gen_java

class GenCode:
	def __init__(self, argv):
		self.init()
		self.parse_opts(argv)
		self.check_conf_file(argv)
		self.parse_conf_file()
		self.check_langs(argv)
		self.check_srcpath(sys.argv)
		self.gen_code()

	def init(self):
		self.svrkitpath = ''
		self.codepath = ''
		self.jsonfile = ''
		self.jsondata = None
		self.langs = []

	def parse_opts(self, argv):
		self.svrkitpath = os.path.dirname(os.path.abspath(os.path.join(os.path.realpath(argv[0]), '..')))
		try:
			opts, args = getopt.getopt(argv[1:], "d:f:g:h")
		except getopt.GetoptError:
			self.print_usage(argv)
			sys.exit()

		for op, value in opts:
			if op == '-d':
				self.codepath = os.path.realpath(value)
			elif op == '-f':
				self.jsonfile = value
			elif op == '-g':
				self.langs = value.split(',')
			else:
				self.print_usage(argv)
				sys.exit()

	def check_conf_file(self, argv):
		if self.jsonfile == '':
			self.print_usage(argv)
			sys.exit()
		if not os.path.exists(self.jsonfile):
			raise IOError('%s is not exists' % (self.jsonfile))

	def parse_conf_file(self):
		try:
			fp = open(self.jsonfile, 'r')
			self.jsondata = json.loads(fp.read())
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def check_langs(self, argv):
		for lang in self.langs:
			if lang not in ['python', 'cpp', 'java']:
				raise TypeError('language %s is not supported' % (lang))
		if len(self.langs) == 0:
			self.print_usage(argv)
			sys.exit()

	def check_srcpath(self, argv):
		if self.codepath == '':
			self.print_usage(argv)
			sys.exit()
		if not os.path.exists(self.codepath):
			raise IOError('%s is not exists' % (self.codepath))

	def gen_code(self):
		for lang in self.langs:
			if lang == 'python':
				GenPythonCode(self.jsondata, os.path.join(self.svrkitpath, 'python'), os.path.join(self.codepath, 'python'))
			elif lang == 'cpp':
				GenCppCode(self.jsondata, os.path.join(self.svrkitpath, 'cpp'), os.path.join(self.codepath, 'cpp'))
			#elif lang == 'java':
			#	gen_cpp.gencode()

	def print_usage(self, argv):
		print 'Usage:'
		print '          %s -f /path/to/svr.json -g lang1,lang2,lang3 -d .' % (argv[0])
		print 'Options:'
		print '          -f\tsvr description file'
		print '          -g\tlanguages(cpp,python,java) for generate'
		print '          -d\tdirectory of svr code'
		print '          -h\tshow help'
		print 'Examples:'
		print '          %s -f /path/to/svr.json -g python -d .' % (argv[0])
		print '          %s -f /path/to/svr.json -g python,cpp,java -d .' % (argv[0])

if __name__ == '__main__':
	GenCode(sys.argv)

