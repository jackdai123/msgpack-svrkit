	def rpc_worker_process_init(self):
		libc.prctl(1, 15)

	def start_rpc_server(self, rpc_worker_type, rpc_worker_sum):
		if rpc_worker_type == 'process':
			libc.prctl(1, 15)

		global rpc_worker_pool
		if rpc_worker_type == 'process':
			rpc_worker_pool = ProcessPool(
					processes = rpc_worker_sum,
					initializer = self.rpc_worker_process_init)
		elif rpc_worker_type == 'thread':
			rpc_worker_pool = ThreadPool(
					processes = rpc_worker_sum)
		else:
			raise TypeError('type of self worker_type isnot correct!')

		addr = msgpackrpc.Address(
				host = self.conf.get('rpc_server', 'ip'),
				port = self.conf.getint('rpc_server', 'port'))
		server = msgpackrpc.Server(RPCHandler())
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

