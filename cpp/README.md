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
- ~/msgpack-svrkit/bin/gen_svr.py -f echo.json -g cpp -d .
- ls -l
```bash
total 8
drwxrwxr-x. 2 vagrant vagrant 4096 Oct 10 08:39 cpp
-rw-rw-r--. 1 vagrant vagrant  831 Oct 10 08:05 echo.json
```
- ls -l cpp
```bash
total 100
-rw-rw-r--. 1 vagrant vagrant 2454 Oct 10 08:39 config.cpp
-rw-rw-r--. 1 vagrant vagrant  554 Oct 10 08:39 config.h
-rw-rw-r--. 1 vagrant vagrant 1129 Oct 10 08:39 daemon.cpp
-rw-rw-r--. 1 vagrant vagrant   50 Oct 10 08:39 daemon.h
-rwxrwxr--. 1 vagrant vagrant  852 Oct 10 08:39 echo
-rw-rw-r--. 1 vagrant vagrant  239 Oct 10 08:39 echo_rpc_cli.conf
-rw-rw-r--. 1 vagrant vagrant 5130 Oct 10 08:39 echo_rpc_cli.cpp
-rw-rw-r--. 1 vagrant vagrant 1100 Oct 10 08:39 echo_rpc_cli.h
-rw-rw-r--. 1 vagrant vagrant 1352 Oct 10 08:39 echo_rpc_handler.cpp
-rw-rw-r--. 1 vagrant vagrant  493 Oct 10 08:39 echo_rpc_handler.h
-rw-rw-r--. 1 vagrant vagrant  300 Oct 10 08:39 echo_rpc_proto.h
-rw-rw-r--. 1 vagrant vagrant 2815 Oct 10 08:39 echo_rpc_test.cpp
-rw-rw-r--. 1 vagrant vagrant 1143 Oct 10 08:39 echo_rpc_test.h
-rw-rw-r--. 1 vagrant vagrant  117 Oct 10 08:39 echo_svr.conf
-rw-rw-r--. 1 vagrant vagrant 3263 Oct 10 08:39 echo_svr.cpp
-rw-rw-r--. 1 vagrant vagrant  397 Oct 10 08:39 echo_svr.h
-rw-rw-r--. 1 vagrant vagrant 1498 Oct 10 08:39 file_utils.cpp
-rw-rw-r--. 1 vagrant vagrant  274 Oct 10 08:39 file_utils.h
-rw-rw-r--. 1 vagrant vagrant  314 Oct 10 08:39 log_utils.cpp
-rw-rw-r--. 1 vagrant vagrant  263 Oct 10 08:39 log_utils.h
-rw-rw-r--. 1 vagrant vagrant 1470 Oct 10 08:39 Makefile
-rw-rw-r--. 1 vagrant vagrant 1777 Oct 10 08:39 opt_map.cpp
-rw-rw-r--. 1 vagrant vagrant  712 Oct 10 08:39 opt_map.h
-rw-rw-r--. 1 vagrant vagrant    6 Oct 10 08:39 README.md
```
- 代码及目录说明
> * config.\*: 配置文件解析类
> * daemon.\*: 创建守护进程类
> * echo：服务启停脚本
> * echo_rpc_cli.\*: rpc客户端代码及配置文件
> * echo_rpc_handler.\*：rpc服务端逻辑代码
> * echo_rpc_proto.h：rpc协议
> * echo_rpc_test：rpc单测程序
> * echo_svr.\*：rpc服务代码及配置文件
> * file_utils.\*：文件读写类
> * log_utils.\*：日志输出类
> * Makefile：编译Makefile
> * opt_map.\*：rpc单测选项类
> * README.md：服务README

- cd cpp && cat echo_svr.conf
```ini
#svr conf

[app]
name=echo
pid=/var/run/echo.pid

[rpc_server]
ip=0.0.0.0
port=3000
worker_type=thread
worker_sum=4
```
- make
- ./echo_svr
```bash
Usage:
		./echo_svr [-c <config>] [-d] [-h]
Options:
		-c    configure file of server
		-d    run as daemon
		-h    show help
Examples:
		./echo_svr -c echo_svr.conf -d
```
- ./echo_svr -c echo_svr.conf -d
- ps -efL | grep echo_svr
```bash
vagrant   5908     1  5908  0    5 08:51 ?        00:00:00 ./echo_svr -c echo_svr.conf -d
vagrant   5908     1  5909  0    5 08:51 ?        00:00:00 ./echo_svr -c echo_svr.conf -d
vagrant   5908     1  5910  0    5 08:51 ?        00:00:00 ./echo_svr -c echo_svr.conf -d
vagrant   5908     1  5911  0    5 08:51 ?        00:00:00 ./echo_svr -c echo_svr.conf -d
vagrant   5908     1  5912  0    5 08:51 ?        00:00:00 ./echo_svr -c echo_svr.conf -d
```
- cat echo_rpc_cli.conf
```ini
#cli conf

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
- ./echo_rpc_test
```bash
Usage:
		./echo_rpc_test [-c <config>] [-f <func>] [-h]
Options:
		-c    configure file of client
		-f    rpc method or function
		-h    show help
Examples:
		./echo_rpc_test -c echo_rpc_cli.conf -f echo1 
		./echo_rpc_test -c echo_rpc_cli.conf -f echo2 
		./echo_rpc_test -c echo_rpc_cli.conf -f echo3 
		./echo_rpc_test -c echo_rpc_cli.conf -f echo4 
```
- ./echo_rpc_test -c echo_rpc_cli.conf -f echo1
```bash
echo1 return 0
```
- ./echo_rpc_test -c echo_rpc_cli.conf -f echo2
```bash
echo2 return 0
```
- ./echo_rpc_test -c echo_rpc_cli.conf -f echo3
```bash
echo3 return 0
```
- ./echo_rpc_test -c echo_rpc_cli.conf -f echo4
```bash
echo4 return 0
```

# rpc性能测试
- **测试环境**：虚拟机单核512M内存，Intel(R) Core(TM) i3-4130 CPU @ 3.40GHz，客户端和服务端部署在同一台机器，运行100w次echo请求
```cpp
//修改echo_rpc_test.cpp，循环100w次
int TestToolImpl :: echo1( OptMap & opt_map ) {
	echomsg req;
	echomsg res;

	Client cli;
	for ( int i = 0; i < 1000000; i++ ) {
		int ret = cli.echo1( req, res );
	}

	return 0;
}
int TestToolImpl :: echo4( OptMap & opt_map ) {
	echomsg req;

	Client cli;
	for ( int i = 0; i < 1000000; i++ ) {
		int ret = cli.echo4( req, res );
	}

	return 0;
}
```
- **有返回结果的测试**：IDL描述文件中rpc_server.apis设置res_proto，qps为2.9w/s
```bash
time ./echo_rpc_test -c echo_rpc_cli.conf -f echo1

real    0m34.306s
user    0m10.524s
sys     0m6.635s
```
- **无返回结果的测试**：IDL描述文件中rpc_server.apis不设置res_proto，qps为40w/s
```bash
time ./echo_rpc_test -c echo_rpc_cli.conf -f echo4

real    0m2.492s
user    0m0.714s
sys     0m0.481s
```

# 依赖库
- gcc >= 4.1 with C++ support
- [msgpack](https://github.com/msgpack/msgpack-c/tree/cpp-1.0.0)：用cpp版本，否则不会生成libmsgpack.a
- [jubatus_mpio](https://github.com/jubatus/jubatus-mpio)：用master版本即可
- [jubatus_msgpack-rpc](https://github.com/jubatus/jubatus-msgpack-rpc/tree/msgpack-1.x/cpp)：用msgpack-1.x版本

