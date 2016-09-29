#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import getopt
import ConfigParser
import traceback
import daemonize
import ctypes
import signal
import importlib
import multiprocessing
from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool

libc = ctypes.CDLL('libc.so.6')

class Service:
	def __init__(self, argv):
		self.daemon = False
		self.conffile = ''
		self.rootpath = ''
		self.conf = ConfigParser.ConfigParser()
		self.parse_opts(argv)
		self.parse_conf(argv)
		self.get_root_path()
		self.args = {}

	def parse_opts(self, argv):
		try:
			opts, args = getopt.getopt(argv[1:], "df:h")
		except getopt.GetoptError:
			self.print_usage(argv)
			sys.exit()
		for op, value in opts:
			if op == '-d':
				self.daemon = True
			elif op == '-f':
				self.conffile = value
			else:
				self.print_usage(argv)
				sys.exit()

	def parse_conf(self, argv):
		if self.conffile != '' and os.path.exists(self.conffile):
			try:
				self.conf.read(self.conffile)
			except Exception,e:
				print traceback.format_exc()
				sys.exit()
		else:
			self.print_usage(argv)
			sys.exit()

	def get_root_path(self):
		absolute_path = os.path.dirname(os.path.abspath(__file__))
		for python_path in os.getenv('PYTHONPATH').split(':'):
			if absolute_path.startswith(python_path):
				self.rootpath = os.path.relpath(absolute_path, python_path).replace(os.path.sep, '.')
				break
		else:
			raise IOError('%s is not in PYTHONPATH' % (__file__))

	def print_usage(self, argv):
		print 'Usage:'
		print '\t%s -f /path/to/svr.conf -d' % (argv[0])
		print 'Options:'
		print '\t-f\tserver configure file'
		print '\t-d\trun as daemon'
		print '\t-h\tshow help'

	def start(self):
		signal.signal(signal.SIGPIPE, signal.SIG_IGN)
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		signal.signal(signal.SIGTERM, signal.SIG_DFL)

		if self.daemon:
			daemon = daemonize.Daemonize(
				app = self.conf.get('app', 'name'),
				pid = self.conf.get('app', 'pid'),
				action = self.start_server,
				auto_close_fds = False)
			daemon.start()
		else:
			self.start_server()

	def rpc_worker_process_init(self):
		libc.prctl(1, 15)

	def start_rpc_server(self, rpc_worker_type, rpc_worker_sum):
		if rpc_worker_type == 'process':
			libc.prctl(1, 15)

		if rpc_worker_type == 'process':
			rpc_worker_pool = ProcessPool(
					processes = rpc_worker_sum,
					initializer = self.rpc_worker_process_init)
		elif rpc_worker_type == 'thread':
			rpc_worker_pool = ThreadPool(
					processes = rpc_worker_sum)
		else:
			raise TypeError('type of self worker_type isnot correct!')

		import msgpackrpc
		rpc_handler = importlib.import_module('.rpc_handler', self.rootpath)
		rpc_init = importlib.import_module('.rpc_init', self.rootpath)

		args = {'rpc_worker_pool' : rpc_worker_pool, 'conffile' : self.conffile}
		rpc_init.init(args, rpc_worker_type)
		args.update(self.args)

		addr = msgpackrpc.Address(
				host = self.conf.get('rpc_server', 'ip'),
				port = self.conf.getint('rpc_server', 'port'))
		server = msgpackrpc.Server(rpc_handler.RPCHandler(args))
		server.listen(addr)
		server.start()

		rpc_worker_pool.close()
		rpc_worker_pool.join()

	def create_rpc_server_manager(self):
		try:
			rpc_worker_type = self.conf.get('rpc_server', 'worker_type')
			rpc_worker_sum = self.conf.getint('rpc_server', 'worker_sum')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		rpc_server_manager = None
		if rpc_worker_type == 'process':
			rpc_server_manager = multiprocessing.process.Process(
					target = self.start_rpc_server,
					args = (rpc_worker_type, rpc_worker_sum))
		elif rpc_worker_type == 'thread':
			rpc_server_manager = multiprocessing.dummy.DummyProcess(
					target = self.start_rpc_server,
					args = (rpc_worker_type, rpc_worker_sum))
		else:
			raise TypeError('type of rpc worker_type isnot correct!')
		return rpc_server_manager

	def self_worker_process_target(self, self_group_name, worker_id, args):
		self_handler = importlib.import_module('.self_handler', self.rootpath)
		libc.prctl(1, 15)
		self_handler.process(self_group_name, worker_id, args)

	def create_self_worker(self, self_worker_type, self_group_name, worker_id, args=None):
		self_handler = importlib.import_module('.self_handler', self.rootpath)
		self_worker = None
		if self_worker_type == 'process':
			self_worker = multiprocessing.process.Process(
					target = self.self_worker_process_target,
					args = (self_group_name, worker_id, args,))
		elif self_worker_type == 'thread':
			self_worker = multiprocessing.dummy.DummyProcess(
					target = self_handler.process,
					args = (self_group_name, worker_id, args,))
		else:
			raise TypeError('type of self worker_type isnot corrent!')
		return self_worker

	def start_self_simple_server(self, self_worker_type):
		try:
			self_worker_sum = self.conf.getint('self_server', 'worker_sum')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		args = {}
		self_worker_map = {}
		for i in xrange(self_worker_sum):
			worker_id = i
			self_worker_map[worker_id] = self.create_self_worker(self_worker_type, '', worker_id, args)
			self_worker_map[worker_id].start()

		while 1:
			for worker_id in self_worker_map:
				self_worker_map[worker_id].join(1)
				if not self_worker_map[worker_id].is_alive():
					self_worker_map[worker_id] = self.create_self_worker(self_worker_type, '', worker_id, args)
					self_worker_map[worker_id].start()

	def start_self_custom_server(self, self_worker_type):
		self_init = importlib.import_module('.self_init', self.rootpath)
		args = {'conf' : self.conf}
		self_init.init(args, self_worker_type)
		args.update(self.args)
		self_worker_map = {}

		try:
			self_group_sum = self.conf.getint('self_server', 'group_sum')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		for i in xrange(self_group_sum):
			try:
				self_group_name = self.conf.get('self_group%d' % (i), 'group_name')
				self_worker_sum = self.conf.getint('self_group%d' % (i), 'worker_sum')
			except Exception,e:
				print traceback.format_exc()
				sys.exit()

			for j in xrange(self_worker_sum):
				worker_id = '%s:%d' % (self_group_name, j)
				self_worker_map[worker_id] = self.create_self_worker(self_worker_type, self_group_name, j, args)
				self_worker_map[worker_id].start()

		while 1:
			for worker_id in self_worker_map:
				self_worker_map[worker_id].join(1)
				if not self_worker_map[worker_id].is_alive():
					tmp_arr = worker_id.split(':')
					self_worker_map[worker_id] = self.create_self_worker(self_worker_type, tmp_arr[0], int(tmp_arr[1]), args)
					self_worker_map[worker_id].start()

	def start_self_server(self, self_worker_type):
		if self_worker_type == 'process':
			libc.prctl(1, 15)

		try:
			self_dispatch_type = self.conf.get('self_server', 'dispatch_type')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		if self_dispatch_type == 'simple':
			self.start_self_simple_server(self_worker_type)
		elif self_dispatch_type == 'custom':
			self.start_self_custom_server(self_worker_type)
		else:
			raise TypeError('type of self dispatch_type isnot correct!')

	def create_self_server_manager(self):
		try:
			self_worker_type = self.conf.get('self_server', 'worker_type')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		self_server_manager = None
		if self_worker_type == 'process':
			self_server_manager = multiprocessing.process.Process(
					target = self.start_self_server,
					args = (self_worker_type,))
		elif self_worker_type == 'thread':
			self_server_manager = multiprocessing.dummy.DummyProcess(
					target = self.start_self_server,
					args = (self_worker_type,))
		else:
			raise TypeError('type of self worker_type isnot correct!')
		return self_server_manager

	def start_server(self):
		rpc_server_manager_dead = True
		self_server_manager_dead = True

		global_init = importlib.import_module('.global_init', self.rootpath)
		global_init.init(self.args)

		while 1:
			if self.conf.has_section('self_server') and self_server_manager_dead:
				self_server_manager = self.create_self_server_manager()
				self_server_manager.start()
				self_server_manager_dead = False

			if self.conf.has_section('rpc_server') and rpc_server_manager_dead:
				rpc_server_manager = self.create_rpc_server_manager()
				rpc_server_manager.start()
				rpc_server_manager_dead = False

			if self.conf.has_section('self_server') and not self_server_manager_dead:
				self_server_manager.join(1)
				if not self_server_manager.is_alive():
					self_server_manager_dead = True

			if self.conf.has_section('rpc_server') and not rpc_server_manager_dead:
				rpc_server_manager.join(1)
				if not rpc_server_manager.is_alive():
					rpc_server_manager_dead = True

if __name__ == '__main__':
	Service(sys.argv).start()

