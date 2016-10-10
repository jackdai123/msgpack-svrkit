# 创建echo服务
- cd ~ && git clone https://github.com/jackdai123/msgpack-svrkit.git
- cd ~ && mkdir echo && cd echo && cp ~/msgpack-svrkit/sample/svr_sample7.json ./echo.json
- cat echo.json
```json
{
	"app": "echo",

	"protos": [{
		"name": "echomsg",
		"fields": [{
			"name": "my_string",
			"type": "string"
		},{
			"name": "vec_int",
			"type": "list",
			"subtype": "int"
		},{
			"name": "dict_string",
			"type": "dict",
			"subtype": "int:string"
		}]
	}],

	"rpc_client": {
		"mode": "sharding"
	},

	"rpc_server": {
		"ip": "0.0.0.0",
		"port": 3000,
		"worker_type": "thread",
		"worker_sum": 4,
		"apis": [{
			"name": "echo1",
			"req_proto": "echomsg",
			"res_proto": "echomsg"
		},{
			"name": "echo2",
			"res_proto": "echomsg"
		},{
			"name": "echo3"
		},{
			"name": "echo4",
			"req_proto": "echomsg"
		}]
	},

	"self_server": {
		"dispatch_type": "custom",
		"worker_type": "thread",
		"groups" : [{
			"group_name": "event",
			"worker_sum": 2
		},{
			"group_name": "value",
			"worker_sum": 2
		}]
	}
}
```
- ~/msgpack-svrkit/bin/gen_svr.py -f echo.json -g python -d .
- ls -l
```bash
total 12
-rw-rw-r--.  1 vagrant vagrant  831 Oct 10 08:05 echo.json
-rw-rw-r--.  1 vagrant vagrant   45 Oct 10 08:05 __init__.py
drwxrwxr-x. 11 vagrant vagrant 4096 Oct 10 08:05 python
```
- ls -l python
```bash
total 28
-rwxrwxr--. 1 vagrant vagrant  991 Oct 10 08:05 echo
-rw-rw-r--. 1 vagrant vagrant  263 Oct 10 08:05 echo_svr.conf
-rw-rw-r--. 1 vagrant vagrant 8918 Oct 10 08:05 echo_svr.py
drwxrwxr-x. 2 vagrant vagrant   50 Oct 10 08:05 global_init
-rw-rw-r--. 1 vagrant vagrant   45 Oct 10 08:05 __init__.py
-rw-rw-r--. 1 vagrant vagrant    6 Oct 10 08:05 README.md
drwxrwxr-x. 2 vagrant vagrant   70 Oct 10 08:05 rpc_cli
drwxrwxr-x. 2 vagrant vagrant   50 Oct 10 08:05 rpc_handler
drwxrwxr-x. 2 vagrant vagrant   47 Oct 10 08:05 rpc_init
drwxrwxr-x. 2 vagrant vagrant   48 Oct 10 08:05 rpc_proto
drwxrwxr-x. 2 vagrant vagrant   47 Oct 10 08:05 rpc_test
drwxrwxr-x. 2 vagrant vagrant   90 Oct 10 08:05 self_handler
drwxrwxr-x. 2 vagrant vagrant   48 Oct 10 08:05 self_init
drwxrwxr-x. 2 vagrant vagrant   44 Oct 10 08:05 utils
```
- 代码及目录说明
> * echo：服务启停脚本，注意需设置脚本中的PYTHONPATH
> * echo_svr.conf：服务配置文件
> * echo_svr.py：服务代码
> * global_init：rpc和self服务全局初始化
> * rpc_cli：rpc客户端代码及配置文件
> * rpc_handler：rpc服务端逻辑代码
> * rpc_init：rpc服务初始化
> * rpc_proto：rpc协议
> * rpc_test：rpc单测程序
> * self_handler：普通服务逻辑代码
> * self_init：普通服务初始化
> * utils：工具类及常用函数

- cd python && cat echo_svr.conf
```ini
[app]
name=echo
pid=/var/run/echo.pid

[rpc_server]
ip=0.0.0.0
port=3000
worker_type=thread
worker_sum=4

[self_server]
dispatch_type=custom
worker_type=thread
group_sum=2

[self_group0]
group_name=event
worker_sum=2

[self_group1]
group_name=value
worker_sum=2
```
- export PYTHONPATH=$(dirname `pwd`)
- python echo_svr.py
```bash
Usage:
		python echo_svr.py [-c <config>] [-d] [-h]
Options:
		-c      configure file of server
		-d      run as daemon
		-h      show help
Examples:
		python echo_svr.py -c svr.conf -d
```
- python echo_svr.py -c echo_svr.conf -d
- ps -efL | grep echo_svr
```bash
vagrant   5717     1  5717  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5718  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5719  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5720  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5721  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5722  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5723  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5724  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5725  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5726  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5727  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5728  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5729  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
vagrant   5717     1  5730  0   14 08:17 ?        00:00:00 python echo_svr.py -c echo_svr.conf -d
```
- cat rpc_cli/echo_rpc_cli.conf
```ini
[server]
sum=2
mode=sharding
shardsum=1000

[server0]
ip=127.0.0.1
port=3000
ip_bak=127.0.0.1
port_bak=3001
shardbegin=0
shardend=499

[server1]
ip=127.0.0.1
port=3002
ip_bak=127.0.0.1
port_bak=3003
shardbegin=500
shardend=999
```
- python rpc_test/echo_rpc_test.py 
```bash
echo1 ret <python.rpc_proto.echo_rpc_proto.echomsg object at 0x122c2d0>
echo2 ret <python.rpc_proto.echo_rpc_proto.echomsg object at 0x122c2d0>
echo3 ret None
echo4 ret None
```

# rpc性能测试
- **测试环境**：虚拟机单核512M内存，Intel(R) Core(TM) i3-4130 CPU @ 3.40GHz，客户端和服务端部署在同一台机器，运行100w次echo请求
```python
#修改rpc_test/echo_rpc_test.py，循环100w次
def test_echo(self):
	req = self.rpc_proto.echomsg()
	for i in xrange(1000000):
		self.cli.echo1(req)
```
- **有返回结果的测试**：IDL描述文件中rpc_server.apis不设置res_proto，qps为3000/s
```
real    5m36.347s
user    2m27.468s
sys     0m15.990s
```
- **无返回结果的测试**：IDL描述文件中rpc_server.apis设置res_proto，qps为1.4w/s
```
real    1m12.819s
user    0m42.881s
sys     0m1.417s
```

# 依赖库
- [daemonize](https://github.com/thesharp/daemonize)
- [msgpackrpc](https://github.com/msgpack-rpc/msgpack-rpc-python)
- [consistent_hash](https://github.com/yummybian/consistent-hash)

