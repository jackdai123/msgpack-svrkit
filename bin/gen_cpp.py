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

def replace_content(src_file, dest_file, tag, tag_content):
	content = ''
	try:
		fp = open(src_file, 'r')
		content = fp.read()
		content = content.replace(tag, tag_content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()
	try:
		fp = open(dest_file, 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

class GenPythonCode:
	def __init__(self, json, tpl, code):
		self.jsondata = json
		self.tplpath = tpl
		self.codepath = code
		self.Process()

	def Process(self):
		self.CheckParams()
		self.gen_make_file()
		self.gen_svr_control_file()
		self.gen_svrconf_file()
		self.gen_server_file()
		self.gen_readme_file()
		self.gen_comm_file()
		if 'rpc_server' in self.jsondata:
			self.gen_rpc_cli()
			self.gen_rpc_handler()
			self.gen_rpc_init()
			self.gen_rpc_proto()
			self.gen_rpc_test()

	def CheckParams(self):
		if not os.path.exists(self.tplpath):
			raise IOError('%s is not exists' % (self.tplpath))
		if not os.path.exists(self.codepath):
			os.mkdir(self.codepath)

	def gen_make_file(self):
		replace_content(
				os.path.join(self.tplpath, 'Makefile'),
				os.path.join(self.codepath, 'Makefile'),
				'${app}',
				self.jsondata['app'])

	def gen_svr_control_file(self):
		replace_content(
				os.path.join(self.tplpath, 'svr_control'),
				os.path.join(self.codepath, self.jsondata['app']),
				'${app}',
				self.jsondata['app'])
		os.chmod(os.path.join(self.codepath, self.jsondata['app']),
				stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH)

	def gen_svrconf_file(self):
		content = '#svr conf\n\n[app]\nname=%s\npid=/var/run/%s.pid\n\n' % (self.jsondata['app'], self.jsondata['app'])
		if 'rpc_server' in self.jsondata:
			content += '[rpc_server]\nip=%s\nport=%d\nworker_type=%s\nworker_sum=%d\n\n' \
					% (self.jsondata['rpc_server']['ip'], self.jsondata['rpc_server']['port'],
							self.jsondata['rpc_server']['worker_type'], self.jsondata['rpc_server']['worker_sum'])
		try:
			fp = open(os.path.join(self.codepath, self.jsondata['app'] + '_svr.conf'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_server_file(self):
		replace_content(
				os.path.join(self.tplpath, 'svr.h'),
				os.path.join(self.codepath, '%s_svr.h' % (self.jsondata['app'])),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'svr.cpp'),
				os.path.join(self.codepath, '%s_svr.cpp' % (self.jsondata['app'])),
				'${app}',
				self.jsondata['app'])

	def gen_readme_file(self):
		try:
			fp = open(os.path.join(self.codepath, 'README.md'), 'w')
			fp.write('# %s' % (self.jsondata['app']))
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_comm_file(self):
		replace_content(
				os.path.join(self.tplpath, 'config.h'),
				os.path.join(self.codepath, 'config.h'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'config.cpp'),
				os.path.join(self.codepath, 'config.cpp'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'daemon.h'),
				os.path.join(self.codepath, 'daemon.h'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'daemon.cpp'),
				os.path.join(self.codepath, 'daemon.cpp'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'file_utils.h'),
				os.path.join(self.codepath, 'file_utils.h'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'file_utils.cpp'),
				os.path.join(self.codepath, 'file_utils.cpp'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'log_utils.h'),
				os.path.join(self.codepath, 'log_utils.h'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'log_utils.cpp'),
				os.path.join(self.codepath, 'log_utils.cpp'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'opt_map.h'),
				os.path.join(self.codepath, 'opt_map.h'),
				'${app}',
				self.jsondata['app'])
		replace_content(
				os.path.join(self.tplpath, 'opt_map.cpp'),
				os.path.join(self.codepath, 'opt_map.cpp'),
				'${app}',
				self.jsondata['app'])

	def gen_rpc_cli(self):
		self.gen_cliconf_file(self.codepath)
		self.gen_rpc_cli_head_file(self.codepath)
		self.gen_rpc_cli_cpp_file(self.codepath)

	def gen_cliconf_file(self, rpc_cli_dir):
		try:
			if self.jsondata['rpc_client']['mode'] == 'sharding':
				shutil.copy(os.path.join(self.tplpath, 'rpc_cli.conf'),
						os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_cli.conf'))
			else:
				raise TypeError('type of rpc_client mode isnot correct!')
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_cli_head_file(self, rpc_cli_dir):
		content = ''
		try:
			fp = open(os.path.join(self.tplpath, 'rpc_cli.h'), 'r')
			content += fp.read()
			fp.close()
			content = content.replace('${app}', self.jsondata['app'])
			content += self.gen_rpc_cli_head_code()
			fp = open(os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_cli.h'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_cli_head_code(self):
		content = '\t\tpublic:\n'
		for api in self.jsondata['rpc_server']['apis']:
			content += '\t\t\tint %s(' % (api['name'])
			if 'req_proto' in api:
				content += 'const %s & req' % (api['req_proto'])
			if 'res_proto' in api:
				if 'req_proto' in api:
					content += ', '
				content += '%s & res' % (api['res_proto'])
			content += ');\n'
		content += '\t};\n\n}'
		return content

	def gen_rpc_cli_cpp_file(self, rpc_cli_dir):
		content = ''
		try:
			fp = open(os.path.join(self.tplpath, 'rpc_cli.cpp'), 'r')
			content += fp.read()
			fp.close()
			content = content.replace('${app}', self.jsondata['app'])
			content += self.gen_rpc_cli_cpp_code()
			content += '}'
			fp = open(os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_cli.cpp'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_cli_cpp_code(self):
		content = ''
		for api in self.jsondata['rpc_server']['apis']:
			content += '\tint Client::%s(' % (api['name'])
			if 'req_proto' in api:
				content += 'const %s & req' % (api['req_proto'])
			if 'res_proto' in api:
				if 'req_proto' in api:
					content += ', '
				content += '%s & res' % (api['res_proto'])
			content += ') {\n\t\ttry {\n\t\t\tmsgpack::rpc::future callback = this->master_cli_->call(\"%s\"' % (api['name'])
			if 'req_proto' in api:
				content += ', req'
			content += ');\n\t\t\t'
			if 'res_proto' in api:
				content += 'res = '
			content += 'callback.get< '
			if 'res_proto' in api:
				content += '%s' % (api['res_proto'])
			content += ' >();\n\t\t} catch (std::exception & e) {\n'
			content += '\t\t\tlog(LOG_ERR, \"Client::%s master[%s:%d] %s\", __func__, this->svr_->master.ip, this->svr_->master.port, e.what());\n'
			content += '\t\t\ttry {\n\t\t\t\tmsgpack::rpc::future callback = this->slave_cli_->call(\"%s\"' % (api['name'])
			if 'req_proto' in api:
				content += ', req'
			content += ');\n\t\t\t\t'
			if 'res_proto' in api:
				content += 'res = '
			content += 'callback.get< '
			if 'res_proto' in api:
				content += '%s' % (api['res_proto'])
			content += ' >();\n\t\t\t} catch (std::exception & e) {\n'
			content += '\t\t\t\tlog(LOG_ERR, \"Client::%s slave[%s:%d] %s\", __func__, this->svr_->slave.ip, this->svr_->slave.port, e.what());\n'
			content += '\t\t\t\treturn -1;\n\t\t\t}\n\t\t}\n\n\t\treturn 0;\n\t}\n'
		return content

	def gen_rpc_handler(self):
		self.gen_rpc_handler_head_file(self.codepath)
		self.gen_rpc_handler_cpp_file(self.codepath)

	def gen_rpc_handler_head_file(self, rpc_cli_dir):
		content = ''
		try:
			fp = open(os.path.join(self.tplpath, 'rpc_handler.h'), 'r')
			content += fp.read()
			fp.close()
			content = content.replace('${app}', self.jsondata['app'])
			content += self.gen_rpc_handler_head_code()
			fp = open(os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_handler.h'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_handler_head_code(self):
		content = '\t\tpublic:\n'
		for api in self.jsondata['rpc_server']['apis']:
			content += '\t\t\tvoid %s( msgpack_stream stream' % (api['name'])
			if 'req_proto' in api:
				content += ', const %s & req' % (api['req_proto'])
			content += ' );\n'
		content += '\t};\n\n}'
		return content

	def gen_rpc_handler_cpp_file(self, rpc_cli_dir):
		content = ''
		try:
			fp = open(os.path.join(self.tplpath, 'rpc_handler.cpp'), 'r')
			content += fp.read()
			fp.close()
			content = content.replace('${app}', self.jsondata['app'])
			content = content.replace('${dispath_code}', self.gen_rpc_handler_dispatch_code())
			content += self.gen_rpc_handler_cpp_code()
			content += '}'
			fp = open(os.path.join(rpc_cli_dir, self.jsondata['app'] + '_rpc_handler.cpp'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_handler_dispatch_code(self):
		content = ''
		for i in xrange(len(self.jsondata['rpc_server']['apis'])):
			api = self.jsondata['rpc_server']['apis']
			if i != 0:
				content += '\t\t\t} else '
			content += 'if (method == \"%s\") {\n' % (api['name'])
			if 'req_proto' in api:
				content += '\t\t\t\tmsgpack::type::tuple< %s > req;\n' % (api['req_proto'])
				content += '\t\t\t\tstream.params().convert(&req);\n'
			content += '\t\t\t\tthis->%s( stream' % (api['name'])
			if 'req_proto' in api:
				content += ', req.get<0>() );\n'
			else:
				content += ' );\n'
		return content

	def gen_rpc_handler_cpp_code(self):
		content = ''
		for api in self.jsondata['rpc_server']['apis']:
			content += '\t void %s_rpc_handler :: %s( msgpack_stream stream' % (self.jsondata['app'], api['name'])
			if 'req_proto' in api:
				content += ', const %s & req'
			content += ' ) {\n\t\t//add logic code\n\n'
			if 'res_proto' in api:
				content += '\t\t//return response\n'
				content += '\t\t%s res;\n' % (api['res_proto'])
				content += '\t\tstream.result(res);\n'
			content += '\t}\n\n'
		return content




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

