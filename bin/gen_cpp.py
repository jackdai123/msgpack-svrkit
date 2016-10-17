#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import stat
import shutil
import traceback

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

class GenCppCode:
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
			self.gen_rpc_proto()
			self.gen_rpc_test()

	def CheckParams(self):
		if not os.path.exists(self.tplpath):
			raise IOError('%s is not exists' % (self.tplpath))
		if not os.path.exists(self.codepath):
			os.mkdir(self.codepath)

		for proto in self.jsondata['protos']:
			for field in proto['fields']:
				if field['type'] not in ['int','float','bool','string','list','dict']:
					raise TypeError('proto:%s field:%s type is not [\'int\',\'float\',\'bool\',\'string\',\'list\',\'dict\']' % (proto['name'], field['name']))
				if 'subtype' in field:
					for subtype in field['subtype'].split(':'):
						for proto2 in self.jsondata['protos']:
							if proto2['name'] == subtype:
								break
						else:
							if subtype not in ['int','float','bool','string']:
								raise TypeError('proto:%s field:%s subtype is not [\'int\',\'float\',\'bool\',\'string\']' % (proto['name'], field['name']))

		for api in self.jsondata['rpc_server']['apis']:
			if 'req_proto' in api and not self.check_proto(api['req_proto']):
				raise TypeError('req_proto:%s is not supported' % (api['req_proto']))
			if 'res_proto' in api and not self.check_proto(api['res_proto']):
				raise TypeError('res_proto:%s is not supported' % (api['res_proto']))

	def check_proto(self, proto_name):
		for proto in self.jsondata['protos']:
			if proto['name'] == proto_name:
				return True;
		return False

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
			content += ') {\n\t\ttry {\n'
			if 'res_proto' in api:
				content += '\t\t\tmsgpack::rpc::future callback = this->master_cli_->call(\"%s\"' % (api['name'])
			else:
				content += '\t\t\tthis->master_cli_->notify(\"%s\"' % (api['name'])
			if 'req_proto' in api:
				content += ', req'
			content += ');\n'
			if 'res_proto' in api:
				content += '\t\t\tres = callback.get< %s >();\n' % (api['res_proto'])
			else:
				content += '\t\t\tthis->master_cli_->get_loop()->flush();\n'
			content += '\t\t} catch (std::exception & e) {\n'
			content += '\t\t\tlog(LOG_ERR, \"Client::%s master[%s:%d] %s\", __func__, this->svr_->master.ip, this->svr_->master.port, e.what());\n'
			content += '\t\t\ttry {\n'
			if 'res_proto' in api:
				content += '\t\t\t\tmsgpack::rpc::future callback = this->slave_cli_->call(\"%s\"' % (api['name'])
			else:
				content += '\t\t\t\tthis->slave_cli_->notify(\"%s\"' % (api['name'])
			if 'req_proto' in api:
				content += ', req'
			content += ');\n'
			if 'res_proto' in api:
				content += '\t\t\t\tres = callback.get< %s >();\n' % (api['res_proto'])
			else:
				content += '\t\t\t\tthis->slave_cli_->get_loop()->flush();\n'
			content += '\t\t\t} catch (std::exception & e) {\n'
			content += '\t\t\t\tlog(LOG_ERR, \"Client::%s slave[%s:%d] %s\", __func__, this->svr_->slave.ip, this->svr_->slave.port, e.what());\n'
			content += '\t\t\t\treturn -1;\n\t\t\t}\n\t\t}\n\n\t\treturn 0;\n\t}\n\n'
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
			api = self.jsondata['rpc_server']['apis'][i]
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
			content += '\tvoid %s_rpc_handler :: %s( msgpack_stream stream' % (self.jsondata['app'], api['name'])
			if 'req_proto' in api:
				content += ', const %s & req' % (api['req_proto'])
			content += ' ) {\n\t\t//add logic code\n\n'
			if 'res_proto' in api:
				content += '\t\t//return response\n'
				content += '\t\t%s res;\n' % (api['res_proto'])
				content += '\t\tstream.result(res);\n'
			content += '\t}\n\n'
		return content

	def get_type_name(self, data_type):
		if data_type in ['bool','int','float']:
			return data_type
		if data_type == 'string':
			return 'std::string'
		if data_type == 'list':
			return 'std::vector'
		if data_type == 'dict':
			return 'std::map'
		for proto in self.jsondata['protos']:
			if proto['name'] == data_type:
				return data_type
		return ''

	def gen_rpc_proto(self):
		if 'protos' not in self.jsondata:
			return

		field_types = {}
		content = '#pragma once\n\n'
		for proto in self.jsondata['protos']:
			for field in proto['fields']:
				field_types[field['type']] = 1
				if 'subtype' in field:
					for subtype in field['subtype'].split(':'):
						field_types[subtype] = 1

		for t in field_types:
			if t == 'string':
				content += '#include <string>\n'
			elif t == 'list':
				content += '#include <vector>\n'
			elif t == 'dict':
				content += '#include <map>\n'
		content += '#include <msgpack.hpp>\n\n'
		content += 'namespace %s {\n\n' % (self.jsondata['app'])

		for proto in self.jsondata['protos']:
			content += '\tclass %s {\n\t\tpublic:\n' % (proto['name'])
			for field in proto['fields']:
				if field['type'] in ['bool','int','float','string']:
					content += '\t\t\t%s %s;\n' % (self.get_type_name(field['type']), field['name'])
				elif field['type'] == 'list':
					content += '\t\t\t%s<%s> %s;\n' % (self.get_type_name(field['type']), self.get_type_name(field['subtype']), field['name'])
				elif field['type'] == 'dict':
					content += '\t\t\t%s<%s,%s> %s;\n' % (self.get_type_name(field['type']), self.get_type_name(field['subtype'].split(':')[0]), self.get_type_name(field['subtype'].split(':')[1]), field['name'])
			content += '\n\t\tpublic:\n\t\t\tMSGPACK_DEFINE('
			for i in xrange(len(proto['fields'])):
				if i != 0:
					content += ', '
				content += proto['fields'][i]['name']
			content += ');\n\t};\n\n'
		content += '}'

		try:
			fp = open(os.path.join(self.codepath, self.jsondata['app'] + '_rpc_proto.h'), 'w')
			fp.write(content)
			fp.close()
			fp = open(os.path.join(self.codepath, self.jsondata['app'] + '_rpc_proto.cpp'), 'w')
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def gen_rpc_test(self):
		self.gen_rpc_test_head_file(self.codepath)
		self.gen_rpc_test_cpp_file(self.codepath)

	def gen_rpc_test_head_file(self, rpc_test_dir):
		try:
			fp = open(os.path.join(self.tplpath, 'rpc_test.h'), 'r')
			content = fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		api_content = ''
		arg_content = ''
		for api in self.jsondata['rpc_server']['apis']:
			api_content += '\t\t\tvirtual int %s( OptMap & bigmap );\n' % (api['name'])
			arg_content += '\t\t\t\t\t{ \"%s\", &TestTool::%s, \"c:f:h\", \"\" },\n' % (api['name'], api['name'])

		content = content.replace('${app}', self.jsondata['app'])
		content = content.replace('${api}', api_content)
		content = content.replace('${arg}', arg_content)

		try:
			fp = open(os.path.join(rpc_test_dir, self.jsondata['app'] + '_rpc_test.h'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

	def	gen_rpc_test_cpp_file(self, rpc_test_dir):
		try:
			fp = open(os.path.join(self.tplpath, 'rpc_test.cpp'), 'r')
			content = fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

		api_content = ''
		func_content = ''
		for api in self.jsondata['rpc_server']['apis']:
			api_content += '\tint TestTool :: %s( OptMap & ) {\n\t\treturn -1;\n\t}\n\n' % (api['name'])
			func_content += '\tint TestToolImpl :: %s( OptMap & opt_map ) {\n' % (api['name'])
			if 'req_proto' in api:
				func_content += '\t\t%s req;\n' % (api['req_proto'])
			if 'res_proto' in api:
				func_content += '\t\t%s res;\n' % (api['res_proto'])
			func_content += '\n\t\tClient cli;\n'
			func_content += '\t\tint ret = cli.%s( ' % (api['name'])
			if 'req_proto' in api:
				func_content += 'req'
			if 'res_proto' in api:
				if 'req_proto' in api:
					func_content += ', '
				func_content += 'res'
			func_content += ' );\n'
			func_content += '\t\tprintf( \"%s return %d\\n\", __func__, ret );\n\n'
			func_content += '\t\treturn 0;\n\t}\n\n'

		content = content.replace('${app}', self.jsondata['app'])
		content = content.replace('${api}', api_content)
		content = content.replace('${func}', func_content)

		try:
			fp = open(os.path.join(rpc_test_dir, self.jsondata['app'] + '_rpc_test.cpp'), 'w')
			fp.write(content)
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()

