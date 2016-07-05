	def create_self_coroutines(self, self_group_name, worker_id, args):
		self_coroutine_sum = 0
		self_dispatch_type = self.conf.get('self_server', 'dispatch_type')
		try:
			if self_dispatch_type == 'simple':
				self_coroutine_sum = self.conf.getint('self_server', 'coroutine_sum')
			elif self_dispatch_type == 'custom':
				self_group_sum = self.conf.getint('self_server', 'group_sum')
				for i in xrange(self_group_sum):
					if self.conf.get('self_group%d' % (i), 'group_name') == self_group_name:
						self_coroutine_sum = self.conf.getint('self_group%d' % (i), 'coroutine_sum')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		coroutines = []
		for i in xrange(self_coroutine_sum):
			coroutines.append(gevent.spawn(${app}_self_handler.process, '%s_%d' % (self_group_name, worker_id), i, args))
		if self_coroutine_sum > 0:
			gevent.joinall(coroutines)

	def self_worker_process_target(self, self_worker_type, self_group_name, worker_id, args):
		libc.prctl(1, 15)
		if self_worker_type == 'process':
			${app}_self_handler.process(self_group_name, worker_id, args)
		elif self_worker_type == 'process_coroutine':
			self.create_self_coroutines(self_group_name, worker_id, args)

	def create_self_worker(self, self_worker_type, self_group_name, worker_id, args=None):
		self_worker = None
		if self_worker_type in ['process', 'process_coroutine']:
			self_worker = multiprocessing.process.Process(
					target = self.self_worker_process_target,
					args = (self_worker_type, self_group_name, worker_id, args,))
		elif self_worker_type == 'thread':
			self_worker = multiprocessing.dummy.DummyProcess(
					target = ${app}_self_handler.process,
					args = (self_group_name, worker_id, args,))
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
			self_worker_map[worker_id] = self.create_self_worker(self_worker_type, 'simple', worker_id, args)
			self_worker_map[worker_id].start()

		while 1:
			for worker_id in self_worker_map:
				self_worker_map[worker_id].join(1)
				if not self_worker_map[worker_id].is_alive():
					self_worker_map[worker_id] = self.create_self_worker(self_worker_type, 'simple', worker_id, args)
					self_worker_map[worker_id].start()

	def start_self_custom_server(self, self_worker_type):
		try:
			self_group_sum = self.conf.getint('self_server', 'group_sum')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		args = {}
		self_worker_map = {}
		for i in xrange(self_group_sum):
			try:
				self_group_name = self.conf.get('self_group%d' % (i), 'group_name')
				self_worker_sum = self.conf.getint('self_group%d' % (i), 'worker_sum')
			except Exception,e:
				print traceback.format_exc()
				sys.exit()

			for j in xrange(self_worker_sum):
				key = '%s_%d' % (self_group_name, j)
				self_worker_map[key] = self.create_self_worker(self_worker_type, self_group_name, j, args)
				self_worker_map[key].start()

		while 1:
			for key in self_worker_map:
				self_worker_map[key].join(1)
				if not self_worker_map[key].is_alive():
					key_arr = key.split('_')
					self_worker_map[key] = self.create_self_worker(self_worker_type, key_arr[0], key_arr[1], args)
					self_worker_map[key].start()

	def start_self_server(self, self_worker_type):
		if self_worker_type in ['process', 'process_coroutine']:
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
		if self_worker_type in ['process', 'process_coroutine']:
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

