class Service:
	def __init__(self, argv):
		self.daemon = False
		self.conffile = ''
		self.conf = ConfigParser.ConfigParser()
		self.parse_opts(argv)
		self.parse_conf(argv)

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

	def print_usage(self, argv):
		print 'Usage:'
		print '\t%s -f /path/to/svr.conf -d' % (argv[0])
		print 'Options:'
		print '\t-f\tserver configure file'
		print '\t-d\trun as daemon'
		print '\t-h\tshow help'

	def start(self):
		if self.daemon:
			daemon = daemonize.Daemonize(
				app = self.conf.get('app', 'name'),
				pid = self.conf.get('app', 'pid'),
				action = self.start_server,
				auto_close_fds = False)
			daemon.start()
		else:
			self.start_server()

