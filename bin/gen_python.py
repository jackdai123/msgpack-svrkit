#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import stat
import shutil
import traceback

def get_init_value(data_type):
	if data_type == 'string':
		return '\'\''
	if data_type == 'bool':
		return 'False';
	if data_type in ['int', 'float']:
		return '0'
	if data_type == 'list':
		return '[]'
	if data_type == 'tuple':
		return '()'
	if data_type == 'dict':
		return '{}'
	return 'None'

class GenPythonCode:
	def __init__(self, json, tpl, code):
		self.jsondata = json
		self.tplpath = tpl
		self.codepath = code
		self.Process()

	def Process(self):
		self.CheckParams()
		self.gen_init_file()
		self.gen_svr_control_file()
		self.gen_svrconf_file()
		self.gen_server_file()
		self.gen_readme_file()
		self.gen_global_init()
		self.gen_utils()
		if 'rpc_server' in self.jsondata:
			self.gen_rpc_cli()
			self.gen_rpc_handler()
			self.gen_rpc_init()
			self.gen_rpc_proto()
			self.gen_rpc_test()
		if 'self_server' in self.jsondata:
			self.gen_self_handler()
			self.gen_self_init()

	def CheckParams(self):
		if not os.path.exists(self.tplpath):
			raise IOError('%s is not exists' % (self.tplpath))
		if not os.path.exists(self.codepath):
			os.mkdir(self.codepath)

	def gen_init_file(self):
		try:
			shutil.copy(os.path.join(self.tplpath, '__init__.py'),
					os.path.join(self.codepath, '__init__.py'))
			shutil.copy(os.path.join(self.tplpath, '__init__.py'),
					os.path.join(os.path.abspath(os.path.join(self.codepath, '..')), '__init__.py'))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_svr_control_file(self):
		content = ''
		try:
			fp = open(os.path.join(self.tplpath, 'svr_control.py'), 'r')
			content = fp.read()
			content = content.replace('${app}', self.jsondata['app'])
			content = content.replace('${PYTHONPATH}', '/opt/au:/opt/gu:/opt/ke')
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
		try:
			fp = open(os.path.join(self.codepath, self.jsondata['app']), 'w')
			fp.write(content)
			fp.close()
			os.chmod(os.path.join(self.codepath, self.jsondata['app']), stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH)
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_svrconf_file(self):
		content = '[app]\nname=%s\npid=/var/run/%s.pid\n\n' % (self.jsondata['app'], self.jsondata['app'])
		if 'rpc_server' in self.jsondata:
			content += '[rpc_server]\nip=%s\nport=%d\nworker_type=%s\nworker_sum=%d\n\n' \
					% (self.jsondata['rpc_server']['ip'], self.jsondata['rpc_server']['port'],
							self.jsondata['rpc_server']['worker_type'], self.jsondata['rpc_server']['worker_sum'])
		if 'self_server' in self.jsondata:
			if self.jsondata['self_server']['dispatch_type'] == 'simple':
				content += '[self_server]\ndispatch_type=simple\nworker_type=%s\nworker_sum=%d\n' \
						% (self.jsondata['self_server']['worker_type'], self.jsondata['self_server']['worker_sum'])
				if 'coroutine_sum' in self.jsondata['self_server']:
					content += 'coroutine_sum=%d\n' % (self.jsondata['self_server']['coroutine_sum'])
				content += '\n'
			elif self.jsondata['self_server']['dispatch_type'] == 'custom':
				content += '[self_server]\ndispatch_type=custom\nworker_type=%s\ngroup_sum=%d\n\n' \
						% (self.jsondata['self_server']['worker_type'], len(self.jsondata['self_server']['groups']))
				for i in xrange(len(self.jsondata['self_server']['groups'])):
					content += '[self_group%d]\ngroup_name=%s\nworker_sum=%d\n' % \
							(i, self.jsondata['self_server']['groups'][i]['group_name'],
									self.jsondata['self_server']['groups'][i]['worker_sum'])
					if self.jsondata['self_server']['worker_type'] == 'process_coroutine':
						content += 'coroutine_sum=%d\n' % (self.jsondata['self_server']['groups'][i]['coroutine_sum'])
					content += '\n'
			else:
				raise TypeError('type of self dispatch_type isnot correct!')
		try:
			fp = open(os.path.join(self.codepath, self.jsondata['app'] + '_svr.conf'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_server_file(self):
		try:
			shutil.copy(os.path.join(self.tplpath, 'svr.py'),
					os.path.join(self.codepath, self.jsondata['app'] + '_svr.py'))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_readme_file(self):
		try:
			fp = open(os.path.join(self.codepath, 'README.md'), 'w')
			fp.write('# %s' % (self.jsondata['app']))
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_global_init(self):
		global_init_dir = os.path.join(self.codepath, 'global_init')
		if os.path.exists(global_init_dir):
			shutil.rmtree(global_init_dir)
		os.mkdir(global_init_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, 'global_init_init.py'),
					os.path.join(global_init_dir, '__init__.py'))
			shutil.copy(os.path.join(self.tplpath, 'global_init_app.py'),
					os.path.join(global_init_dir, '%s_global_init.py' % (self.jsondata['app'])))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_utils(self):
		utils_dir = os.path.join(self.codepath, 'utils')
		if os.path.exists(utils_dir):
			shutil.rmtree(utils_dir)
		os.mkdir(utils_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, '__init__.py'),
					os.path.join(utils_dir, '__init__.py'))
			shutil.copy(os.path.join(self.tplpath, '__init__.py'),
					os.path.join(utils_dir, '%s_utils.py' % (self.jsondata['app'])))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_cli(self):
		rpc_cli_dir = os.path.join(self.codepath, 'rpc_cli')
		if os.path.exists(rpc_cli_dir):
			shutil.rmtree(rpc_cli_dir)
		os.mkdir(rpc_cli_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, 'rpc_cli_init.py'),
					os.path.join(rpc_cli_dir, '__init__.py'))
			self.gen_cliconf_file(rpc_cli_dir)
			self.gen_rpc_cli_file(rpc_cli_dir)
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_cliconf_file(self, rpc_cli_dir):
		try:
			if self.jsondata['rpc_client']['mode'] == 'sharding':
				shutil.copy(os.path.join(self.tplpath, 'cli_sharding_conf.py'),
						os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_cli.conf'))
			elif self.jsondata['rpc_client']['mode'] == 'hashring':
				shutil.copy(os.path.join(self.tplpath, 'cli_hashring_conf.py'),
						os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_cli.conf'))
			else:
				raise TypeError('type of rpc_client mode isnot correct!')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_cli_file(self, rpc_cli_dir):
		content = ''
		try:
			fp = open(os.path.join(self.tplpath, 'cli_head.py'), 'r')
			content += fp.read()
			fp.close()
			content = content.replace('${app}', self.jsondata['app'])
			content += self.gen_rpc_cli_code()
			fp = open(os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_cli.py'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_cli_code(self):
		content = ''
		for api in self.jsondata['rpc_server']['apis']:
			for arg in api['args']:
				content += '\t#@param %s : %s\n' % (arg['name'], arg['type'])
			if 'req_proto' in api:
				content += '\t#@req : %s\n' % (api['req_proto'])
			if 'res_proto' in api:
				content += '\t#@res : %s\n' % (api['res_proto'])
			content += '\tdef %s(self' % (api['name'])
			for arg in api['args']:
				content += ', %s' % (arg['name'])
			content += '):\n\t\tfor i in xrange(3):\n\t\t\ttry:\n'
			if 'req_proto' in api:
				for proto in self.jsondata['protos']:
					if proto['name'] == api['req_proto']:
						content += '\t\t\t\treq = self.rpc_proto.%s()\n' % (api['req_proto'])
						for field in proto['fields']:
							content += '\t\t\t\treq.%s = %s\n' % (field['name'], get_init_value(field['type']))
						break
				else:
					content += '\t\t\t\treq = %s\n' % (get_init_value(api['req_proto']))
			content += '\t\t\t\tfuture = self.client.call_async(\'%s\'' % (api['name'])
			if 'req_proto' in api:
				content += ', req'
			content += ')\n\t\t\t\tresult = future.get()\n'
			if 'res_proto' in api:
				for proto in self.jsondata['protos']:
					if proto['name'] == api['res_proto']:
						content += '\t\t\t\tres = self.rpc_proto.%s()\n' % (api['res_proto'])
						content += '\t\t\t\tres.from_msgpack(result)\n\t\t\t\treturn res\n'
						break
				else:
					content += '\t\t\t\treturn result\n'
			else:
				content += '\t\t\t\treturn result\n'
			content += '\t\t\texcept Exception, e:\n\t\t\t\tif not self._failover():\n\t\t\t\t\tbreak\n\n'
		return content

	def gen_rpc_handler(self):
		rpc_handler_dir = os.path.join(self.codepath, 'rpc_handler')
		if os.path.exists(rpc_handler_dir):
			shutil.rmtree(rpc_handler_dir)
		os.mkdir(rpc_handler_dir)

		try:
			fp = open(os.path.join(self.tplpath, 'rpc_handler_init.py'), 'r')
			content = fp.read()
			fp.close()
			for api in self.jsondata['rpc_server']['apis']:
				content += '\tdef %s(self' % (api['name'])
				if 'req_proto' in api:
					content += ', req'
				content += '):\n\t\tres = self.rpc_worker_pool.apply_async(self.func_map[\'%s\'].%s' % (api['name'], api['name'])
				if 'req_proto' in api:
					content += ', (req,)'
				content += ')\n\t\treturn res.get()\n\n'
			fp = open(os.path.join(rpc_handler_dir, '__init__.py'), 'w')
			fp.write(content)
			fp.close()

			fp = open(os.path.join(self.tplpath, 'rpc_handler_app.py'), 'r')
			content = fp.read()
			fp.close()
			content = content.replace('${app}', self.jsondata['app'])
			for api in self.jsondata['rpc_server']['apis']:
				if 'req_proto' in api:
					content += '\t#@req : %s\n' % (api['req_proto'])
				if 'res_proto' in api:
					content += '\t#@res : %s\n' % (api['res_proto'])
				content += '\tdef %s(self' % (api['name'])
				if 'req_proto' in api:
					content += ', m'
				content += '):\n'
				if 'req_proto' in api:
					for proto in self.jsondata['protos']:
						if proto['name'] == api['req_proto']:
							content += '\t\treq = self.rpc_proto.%s()\n' % (api['req_proto'])
							content += '\t\treq.from_msgpack(m)\n\n'
							break
					else:
						content += '\t\treq = m\n\n'
				content += '\t\t########add logic code here########\n\n'
				content += '\t\t########end logic code########\n\n'
				if 'res_proto' in api:
					for proto in self.jsondata['protos']:
						if proto['name'] == api['res_proto']:
							content += '\t\tres = self.rpc_proto.%s()\n' % (api['res_proto'])
							break
					else:
						content += '\t\tres = %s\n' % (get_init_value(api['res_proto']))
					content += '\t\treturn res\n\n'
				else:
					content += '\t\treturn None\n\n'
			fp = open(os.path.join(rpc_handler_dir, '%s_rpc_handler.py' % (self.jsondata['app'])), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_init(self):
		rpc_init_dir = os.path.join(self.codepath, 'rpc_init')
		if os.path.exists(rpc_init_dir):
			shutil.rmtree(rpc_init_dir)
		os.mkdir(rpc_init_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, 'rpc_init_init.py'),
					os.path.join(rpc_init_dir, '__init__.py'))
			shutil.copy(os.path.join(self.tplpath, 'rpc_init_app.py'),
					os.path.join(rpc_init_dir, '%s_rpc_init.py' % (self.jsondata['app'])))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_proto(self):
		rpc_proto_dir = os.path.join(self.codepath, 'rpc_proto')
		if os.path.exists(rpc_proto_dir):
			shutil.rmtree(rpc_proto_dir)
		os.mkdir(rpc_proto_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, '__init__.py'),
					os.path.join(rpc_proto_dir, '__init__.py'))
			self.gen_proto_file(rpc_proto_dir)
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_proto_file(self, rpc_proto_dir):
		if 'protos' in self.jsondata:
			content = '#!/usr/bin/env python\n#-*- coding: utf-8 -*-\n\n'
			for proto in self.jsondata['protos']:
				content += 'class %s(object):\n\tdef __init__(self):\n' % (proto['name'])
				for field in proto['fields']:
					content += '\t\tself.%s = %s\n' % (field['name'], get_init_value(field['type']))
				content += '\n\tdef to_msgpack(self):\n\t\treturn [\n'
				for field in proto['fields']:
					content += '\t\t\tself.%s,\n' % (field['name'])
				content += '\t\t]\n\n\tdef from_msgpack(self, msg):\n'
				index = 0
				for field in proto['fields']:
					content += '\t\tself.%s = msg[%d]\n' % (field['name'], index)
					index += 1
				content += '\n'

			try:
				fp = open(os.path.join(rpc_proto_dir, self.jsondata['app'] + '_rpc_proto.py'), 'w')
				fp.write(content)
				fp.close()
			except Exception,e:
				print traceback.format_exc()
				sys.exit()

	def gen_rpc_test(self):
		rpc_test_dir = os.path.join(self.codepath, 'rpc_test')
		if os.path.exists(rpc_test_dir):
			shutil.rmtree(rpc_test_dir)
		os.mkdir(rpc_test_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, '__init__.py'),
					os.path.join(rpc_test_dir, '__init__.py'))
			self.gen_test_file(rpc_test_dir)
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_test_file(self, rpc_test_dir):
		content = ''
		try:
			fp = open(os.path.join(self.tplpath, 'rpc_test_app.py'), 'r')
			content += fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
		
		content += '\tdef run(self):\n'
		for api in self.jsondata['rpc_server']['apis']:
			content += '\t\tself.test_%s()\n' % (api['name'])
		content += '\n'

		for api in self.jsondata['rpc_server']['apis']:
			content += '\tdef test_%s(self):\n' % (api['name'])
			content += '\t\tret = self.cli.%s(' % (api['name'])
			for arg in api['args']:
				content += get_init_value(arg['type']) + ','
			content += ')\n\t\tprint \'%s ret %%s\' %% (ret)\n\n' % (api['name'])

		content += 'if __name__ == \'__main__\':\n\tRPCTest().run()\n\n'

		try:
			fp = open(os.path.join(rpc_test_dir, self.jsondata['app'] + '_rpc_test.py'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_self_handler(self):
		self_handler_dir = os.path.join(self.codepath, 'self_handler')
		if os.path.exists(self_handler_dir):
			shutil.rmtree(self_handler_dir)
		os.mkdir(self_handler_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, 'self_handler_init.py'),
					os.path.join(self_handler_dir, '__init__.py'))
			self.gen_self_handler_file(self_handler_dir)
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_self_handler_file(self, self_handler_dir):
		if self.jsondata['self_server']['dispatch_type'] == 'simple':
			self.gen_self_simple_handler_file(self_handler_dir)
		elif self.jsondata['self_server']['dispatch_type'] == 'custom':
			self.gen_self_custom_logic_handler_file(self_handler_dir)
		else:
			raise TypeError('type of self dispatch_type isnot correct!')

	def gen_self_simple_handler_file(self, self_handler_dir):
		try:
			shutil.copy(os.path.join(self.tplpath, 'simple_self_handler.py'),
					os.path.join(self_handler_dir, self.jsondata['app'] + '_self_handler.py'))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_self_custom_logic_handler_file(self, self_handler_dir):
		try:
			for group in self.jsondata['self_server']['groups']:
				shutil.copy(os.path.join(self.tplpath, 'custom_self_handler.py'),
						os.path.join(self_handler_dir, '%s_%s_self_handler.py' % (self.jsondata['app'], group['group_name'])))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_self_init(self):
		self_init_dir = os.path.join(self.codepath, 'self_init')
		if os.path.exists(self_init_dir):
			shutil.rmtree(self_init_dir)
		os.mkdir(self_init_dir)

		try:
			shutil.copy(os.path.join(self.tplpath, 'self_init_init.py'),
					os.path.join(self_init_dir, '__init__.py'))
			shutil.copy(os.path.join(self.tplpath, 'self_init_app.py'),
					os.path.join(self_init_dir, '%s_self_init.py' % (self.jsondata['app'])))
		except Exception,e:
			print traceback.format_exc()
			sys.exit()


