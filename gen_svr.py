#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import getopt
import sys
import os
import stat
import traceback
import shutil

jsonfile = ''
jsondata = None
toolpath = ''
codepath = ''

def print_usage(argv):
	print 'Usage:'
	print '\t%s -f /path/to/svr.json -d .' % (argv[0])
	print 'Options:'
	print '\t-f\tsvr description file'
	print '\t-d\tdirectory of svr code'
	print '\t-h\tshow help'

def parse_opts(argv):
	global jsonfile, codepath, toolpath
	toolpath = os.path.dirname(os.path.abspath(argv[0]))
	try:
		opts, args = getopt.getopt(argv[1:], "d:f:h")
	except getopt.GetoptError:
		print_usage(argv)
		sys.exit()
	for op, value in opts:
		if op == '-d':
			codepath = os.path.abspath(value)
		elif op == '-f':
			jsonfile = value
		else:
			print_usage(argv)
			sys.exit()

def check_conf_file(argv):
	global jsonfile
	if jsonfile == '' or not os.path.exists(jsonfile):
		print_usage(argv)
		sys.exit()

def parse_conf_file():
	global jsonfile, jsondata
	try:
		fp = open(jsonfile, 'r')
		jsondata = json.loads(fp.read())
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def check_srcpath(argv):
	global codepath
	if codepath == '':
		print_usage(argv)
		sys.exit()

def gen_svrconf_file():
	global jsondata, codepath
	content = '[app]\nname=%s\npid=/tmp/%s.pid\n\n' % (jsondata['app'], jsondata['app'])
	if 'rpc_server' in jsondata:
		content += '[rpc_server]\nip=%s\nport=%d\nworker_type=%s\nworker_sum=%d\n\n' \
				% (jsondata['rpc_server']['ip'], jsondata['rpc_server']['port'],
						jsondata['rpc_server']['worker_type'], jsondata['rpc_server']['worker_sum'])
	if 'self_server' in jsondata:
		if jsondata['self_server']['dispatch_type'] == 'simple':
			content += '[self_server]\ndispatch_type=simple\nworker_type=%s\nworker_sum=%d\n' \
					% (jsondata['self_server']['worker_type'], jsondata['self_server']['worker_sum'])
			if 'coroutine_sum' in jsondata['self_server']:
				content += 'coroutine_sum=%d\n' % (jsondata['self_server']['coroutine_sum'])
			content += '\n'
		elif jsondata['self_server']['dispatch_type'] == 'custom':
			content += '[self_server]\ndispatch_type=custom\nworker_type=%s\ngroup_sum=%d\n\n' \
					% (jsondata['self_server']['worker_type'], len(jsondata['self_server']['groups']))
			for i in xrange(len(jsondata['self_server']['groups'])):
				content += '[self_group%d]\ngroup_name=%s\nworker_sum=%d\ncoroutine_sum=%d\n\n' % \
						(i, jsondata['self_server']['groups'][i]['group_name'],
								jsondata['self_server']['groups'][i]['worker_sum'],
								jsondata['self_server']['groups'][i]['coroutine_sum'])
		else:
			raise TypeError('type of self dispatch_type isnot correct!')
	try:
		fp = open(os.path.join(codepath, jsondata['app'] + '_svr.conf'), 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

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

def gen_proto_file():
	global jsondata, codepath
	content = ''
	if 'protos' in jsondata:
		content = '#!/usr/bin/env python\n#-*- coding: utf-8 -*-\n\nimport msgpack\n\n'
		for proto in jsondata['protos']:
			content += 'class %s(object):\n\tdef __init__(self):\n' % (proto['name'])
			for field in proto['fields']:
				content += '\t\tself.%s = %s\n' % (field['name'], get_init_value(field['type']))
			content += '\n\tdef to_msgpack(self):\n\t\treturn msgpack.dumps({\n'
			for field in proto['fields']:
				content += '\t\t\t\'%s\' : self.%s,\n' % (field['name'], field['name'])
			content += '\t\t\t})\n\n\tdef from_msgpack(self, msg):\n\t\tm = msgpack.loads(msg)\n'
			for field in proto['fields']:
				content += '\t\tself.%s = m[\'%s\']\n' % (field['name'], field['name'])
		content += '\n'
	try:
		fp = open(os.path.join(codepath, jsondata['app'] + '_proto.py'), 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_comm_svr_head():
	global toolpath, jsondata
	content = ''
	try:
		fp = open(os.path.join(toolpath, 'comm_svr_head.tpl'), 'r')
		content = fp.read()
		content = content.replace('${app}', jsondata['app'])
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()
	return content

def gen_rpc_svr_head():
	global toolpath, jsondata
	content = ''
	if 'rpc_server' in jsondata:
		try:
			fp = open(os.path.join(toolpath, 'rpc_svr_head.tpl'), 'r')
			content = fp.read()
			content = content.replace('${app}', jsondata['app'])
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
	return content

def gen_self_svr_head():
	global toolpath, jsondata
	content = ''
	if 'self_server' in jsondata:
		if jsondata['self_server']['worker_type'] == 'process_coroutine':
			content += 'from gevent import monkey\nmonkey.patch_all(sys=True, Event=True)\n'
		content += 'import %s_self_handler\n\n' % (jsondata['app'])
	return content

def gen_rpc_handler_code():
	global jsondata
	content = ''
	if 'rpc_server' in jsondata:
		content += 'class RPCHandler(object):\n'
		for api in jsondata['rpc_server']['apis']:
			content += '\tdef %s(self' % (api['name'])
			for arg in api['args']:
				content += ', %s' % (arg['name'])
			content += '):\n\t\ttimeIn = timeit.default_timer()\n'
			for arg in api['args']:
				content += '\t\t%s_data = %s_proto.%s()\n' % (arg['name'], jsondata['app'], arg['type'])
				content += '\t\t%s_data.from_msgpack(%s)\n' % (arg['name'], arg['name'])
			content += '\t\tres = rpc_worker_pool.apply_async(%s_rpc_handler.%s, (' % (jsondata['app'], api['name'])
			for arg in api['args']:
				content += '%s_data,' % (arg['name'])
			content += '))\n\t\ttimeUse = timeit.default_timer() - timeIn\n'
			if api['ret']:
				content += '\t\treturn res.get()\n'
			content += '\n'
	return content

def gen_comm_svr_body():
	global toolpath
	content = ''
	try:
		fp = open(os.path.join(toolpath, 'comm_svr_body.tpl'), 'r')
		content = fp.read()
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()
	return content

def gen_rpc_svr_body():
	global toolpath, jsondata
	content = ''
	if 'rpc_server' in jsondata:
		try:
			fp = open(os.path.join(toolpath, 'rpc_svr_body.tpl'), 'r')
			content = fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
	return content

def gen_self_svr_body():
	global toolpath, jsondata
	content = ''
	if 'self_server' in jsondata:
		try:
			fp = open(os.path.join(toolpath, 'self_svr_body.tpl'), 'r')
			content = fp.read()
			content = content.replace('${app}', jsondata['app'])
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
	return content

def gen_start_server_head():
	global toolpath, jsondata
	content = '\tdef start_server(self):\n'
	content += '\t\trpc_server_manager_dead = True\n'
	content += '\t\tself_server_manager_dead = True\n\n'
	content += '\t\twhile 1:\n'
	return content

def gen_start_manager():
	global toolpath, jsondata
	content = ''
	if 'rpc_server' in jsondata:
		try:
			fp = open(os.path.join(toolpath, 'rpc_start_manager.tpl'), 'r')
			content += fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
	if 'self_server' in jsondata:
		try:
			fp = open(os.path.join(toolpath, 'self_start_manager.tpl'), 'r')
			content += fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
	return content

def gen_join_manager():
	global toolpath, jsondata
	content = ''
	if 'rpc_server' in jsondata:
		try:
			fp = open(os.path.join(toolpath, 'rpc_join_manager.tpl'), 'r')
			content += fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
	if 'self_server' in jsondata:
		try:
			fp = open(os.path.join(toolpath, 'self_join_manager.tpl'), 'r')
			content += fp.read()
			fp.close()
		except Exception,e:
			print traceback.format_exc()
			sys.exit()
	return content

def gen_start_server_body():
	content = ''
	content += gen_start_manager()
	content += gen_join_manager()
	return content

def gen_start_server():
	content = ''
	content += gen_start_server_head()
	content += gen_start_server_body()
	return content

def gen_comm_svr_tail():
	global toolpath
	content = ''
	try:
		fp = open(os.path.join(toolpath, 'comm_svr_tail.tpl'), 'r')
		content += fp.read()
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()
	return content

def gen_server_file():
	global codepath, jsondata
	content = gen_comm_svr_head()
	content += gen_rpc_svr_head()
	content += gen_self_svr_head()
	content += gen_rpc_handler_code()
	content += gen_comm_svr_body()
	content += gen_rpc_svr_body()
	content += gen_self_svr_body()
	content += gen_start_server()
	content += gen_comm_svr_tail()
	try:
		fp = open(os.path.join(codepath, jsondata['app'] + '_svr.py'), 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_rpc_handler_file():
	global codepath, jsondata
	content = '#!/usr/bin/env python\n#-*- coding: utf-8 -*-\n\nimport %s_proto\n\n' % (jsondata['app'])
	for api in jsondata['rpc_server']['apis']:
		for arg in api['args']:
			content += '#@param %s : %s\n' % (arg['name'], arg['type'])
		if api['ret']:
			content += '#@return : yes\n'
		else:
			content += '#@return : no\n'
		content += 'def %s(' % (api['name'])
		for arg in api['args']:
			content += arg['name'] + ','
		content += '):\n'
		if api['ret']:
			content += '\treturn None\n\n'
		else:
			content += '\tpass\n\n'
	try:
		fp = open(os.path.join(codepath, jsondata['app'] + '_rpc_handler.py'), 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_self_simple_handler_file():
	global toolpath, codepath, jsondata
	try:
		shutil.copy(os.path.join(toolpath, 'simple_self_handler.tpl'),
				os.path.join(codepath, jsondata['app'] + '_self_handler.py'))
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_self_custom_main_hanlder_file():
	global codepath, jsondata
	content = '#!/usr/bin/env python\n#-*- coding: utf-8 -*-\n\n'
	for group in jsondata['self_server']['groups']:
		content += 'import %s_self_%s_handler\n' % (jsondata['app'], group['group_name'])
	content += '\ndef process(self_group_name, self_worker_id, args):\n'
	content += '\tgroup_name = self_group_name.split(\'_\')[0]\n'
	content += '\tworker_id = \'%s_%d\' % (self_group_name, self_worker_id)\n'
	for group in jsondata['self_server']['groups']:
		content += '\tif group_name == \'%s\':\n' % (group['group_name'])
		content += '\t\treturn %s_self_%s_handler.process(worker_id, args)\n' % (jsondata['app'], group['group_name'])
	content += '\n'
	try:
		fp = open(os.path.join(codepath, jsondata['app'] + '_self_handler.py'), 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_self_custom_logic_handler_file():
	global toolpath, codepath, jsondata
	try:
		for group in jsondata['self_server']['groups']:
			shutil.copy(os.path.join(toolpath, 'custom_self_handler.tpl'),
					os.path.join(codepath, '%s_self_%s_handler.py' % (jsondata['app'], group['group_name'])))
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_self_handler_file():
	global toolpath, codepath, jsondata
	if jsondata['self_server']['dispatch_type'] == 'simple':
		gen_self_simple_handler_file()
	elif jsondata['self_server']['dispatch_type'] == 'custom':
		gen_self_custom_main_hanlder_file()
		gen_self_custom_logic_handler_file()
	else:
		raise TypeError('type of self dispatch_type isnot correct!')

def gen_handler_file():
	global jsondata
	if 'rpc_server' in jsondata:
		gen_rpc_handler_file()
	if 'self_server' in jsondata:
		gen_self_handler_file()

def gen_cliconf_file():
	global jsondata, codepath, toolpath
	if 'rpc_server' not in jsondata:
		return
	try:
		if jsondata['rpc_client']['mode'] == 'sharding':
			shutil.copy(os.path.join(toolpath, 'cli_sharding_conf.tpl'),
					os.path.join(codepath, jsondata['app'] + '_cli.conf'))
		elif jsondata['rpc_client']['mode'] == 'hashring':
			shutil.copy(os.path.join(toolpath, 'cli_hashring_conf.tpl'),
					os.path.join(codepath, jsondata['app'] + '_cli.conf'))
		else:
			raise TypeError('type of rpc_client mode isnot correct!')
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_rpc_cli_code():
	global jsondata
	content = ''
	for api in jsondata['rpc_server']['apis']:
		for arg in api['args']:
			content += '\t#@param %s : %s\n' % (arg['name'], arg['type'])
		if api['ret']:
			content += '\t#@return : yes\n'
		else:
			content += '\t#@return : no\n'
		content += '\tdef %s(self' % (api['name'])
		for arg in api['args']:
			content += ', %s' % (arg['name'])
		content += '):\n\t\tfor i in xrange(3):\n\t\t\ttry:\n'
		if api['ret']:
			content += '\t\t\t\tfuture = self.client.call_async(\'%s\'' % (api['name'])
			for arg in api['args']:
				content += ', %s' % (arg['name'])
			content += ')\n\t\t\t\treturn future.get()\n'
		else:
			content += '\t\t\t\tself.client.notify(\'%s\'' % (api['name'])
			for arg in api['args']:
				content += ', %s' % (arg['name'])
			content += ')\n'
		content += '\t\t\texcept Exception, e:\n\t\t\t\tif not self._failover():\n\t\t\t\t\tbreak\n\t\traise Exception, e\n\n'
	return content

def gen_rpc_cli_file():
	global jsondata, toolpath, codepath
	content = ''
	try:
		fp = open(os.path.join(toolpath, 'cli_head.tpl'), 'r')
		content += fp.read()
		fp.close()
		content += gen_rpc_cli_code()
		fp = open(os.path.join(codepath, jsondata['app'] + '_cli.py'), 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_client_file():
	global jsondata
	if 'rpc_server' in jsondata:
		gen_rpc_cli_file()

def gen_test_file():
	global jsondata, codepath
	if 'rpc_server' not in jsondata:
		return
	content = '#!/usr/bin/env python\n#-*- coding: utf-8 -*-\n\n'
	content += 'import %s_proto\nimport %s_cli\n\n' % (jsondata['app'], jsondata['app'])
	for api in jsondata['rpc_server']['apis']:
		content += 'def test_%s():\n' % (api['name'])
		content += '\tcli = %s_cli.Client(\'%s_cli.conf\'' % (jsondata['app'], jsondata['app'])
		if jsondata['rpc_client']['mode'] == 'sharding':
			content += ', 0'
		content += ')\n'
		for arg in api['args']:
			content += '\t%s = %s_proto.%s()\n' % (arg['name'], jsondata['app'], arg['type'])
		if api['ret']:
			content += '\tprint '
		else:
			content += '\t'
		content += 'cli.%s(' % (api['name'])
		for arg in api['args']:
			content += '%s,' % (arg['name'])
		content += ')\n\n'
	content += 'def main():\n'
	for api in jsondata['rpc_server']['apis']:
		content += '\ttest_%s()\n' % (api['name'])
	content += '\nif __name__ == \'__main__\':\n\tmain()\n\n'
	try:
		fp = open(os.path.join(codepath, jsondata['app'] + '_test.py'), 'w')
		fp.write(content)
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

def gen_svr_control_file():
	global jsondata, toolpath, codepath
	content = ''
	try:
		fp = open(os.path.join(toolpath, 'svr_control.tpl'), 'r')
		content = fp.read()
		content = content.replace('${app}', jsondata['app'])
		content = content.replace('${PYTHONPATH}', '/opt/au:/opt/gu:/opt/ke')
		fp.close()
	except Exception,e:
		print traceback.format_exc()
		sys.exit()
	try:
		fp = open(os.path.join(codepath, jsondata['app']), 'w')
		fp.write(content)
		fp.close()
		os.chmod(os.path.join(codepath, jsondata['app']), stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH)
	except Exception,e:
		print traceback.format_exc()
		sys.exit()

if __name__ == '__main__':
	parse_opts(sys.argv)
	check_conf_file(sys.argv)
	parse_conf_file()
	check_srcpath(sys.argv)
	gen_svrconf_file()
	gen_proto_file()
	gen_server_file()
	gen_handler_file()
	gen_cliconf_file()
	gen_client_file()
	gen_test_file()
	gen_svr_control_file()

