		try:
			self_worker_type = self.conf.get('self_server', 'worker_type')
			self_worker_sum = self.conf.getint('self_server', 'worker_sum')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		self_server_manager_dead = True

