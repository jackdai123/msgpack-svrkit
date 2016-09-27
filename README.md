# pysvrkit简介
**pysvrkit**是一个用来生成python服务框架（skeleton）的工具，主要为了提升后台python工程师的开发效率，特点如下：
> * **基于msgpack的rpc** ：[msgpack](http://msgpack.org/)是一个快速精巧的二进制打包协议，支持超过50种开发语言，基于msgpack可以容易的跨语言开发
> * **IDL描述文件** ：使用pysvrkit生成服务代码前，需书写[IDL](http://baike.baidu.com/link?url=lDbMtbnZgrE1cW-N3yBZ35xYWWHPTSUXYxWtH81cduOZ7O7NfLN_IGKRxbHPyvKZkO0Uperzq2wu-f0wMKEduaGdK3j1IyV7vG8WxGrYRAa)文件，定义服务名称、服务工作模式、rpc接口和协议、客户端分布方式等等
> * **多种工作模式** ：支持多进程、多线程、协程工作模式，根据使用场景不同在IDL描述文件选择不同的工作模式
> * **多种客户端分布方式**：支持分片、一致性哈希等多种分布方式，根据使用场景不同在IDL描述文件选择不同的分布式方式

# IDL描述文件
**IDL描述文件**是一个json文件，主要包括rpc协议、客户端分布、rpc服务描述、普通服务描述四部分：
## 1. **rpc协议**
定义rpc协议数据结构，对应描述文件中的protos字段，如下json片段定义了只包含一个字符串字段名叫echomsg结构，其中字段类型支持string、bool、int、float、list、tuple、dict

> * name：定义数据结构的名称
> * fields：定义数据结构包含的字段
> * fields.name：定义一个字段的名称
> * fields.type：定义一个字段的数据类型

```json
"protos": [{
	"name": "echomsg",
	"fields": [{
		"name": "value",
		"type": "string"
	}]
}]
```

## 2. **客户端分布**
pysvrkit由客户端来决定路由，即请求发送到哪台服务器，对应描述文件中的rpc_client.mode字段，目前只支持sharding和hashring两种模式，如下json片段使用hashring

> * hashring：即[一致性哈希](http://blog.csdn.net/cywosp/article/details/23397179/)分布方式，适合无状态服务
> * sharding：根据客户端ID分片，适合有状态的比如存储服务

```json
"rpc_client": {
	"mode": "hashring"
}
```

## 3. **rpc服务描述**
定义rpc服务，对应描述文件中的rpc_server字段，如下json片段定义一个echo服务，只有一个echo接口

> * ip：定义rpc服务监听的ip
> * port：定义rpc服务监听的端口
> * worker_type：只支持process和thread两种
> * worker_sum：定义rpc工作者的数量
> * apis：定义服务提供的接口
> * apis.name：定义接口的名称
> * apis.args：定义接口参数
> * apis.args.name：定义接口参数的名称
> * apis.args.type：定义接口参数的数据类型
> * apis.req_proto: 定义接口请求的数据类型
> * apis.res_proto: 定义接口响应的数据类型

```json
"rpc_server": {
	"ip": "0.0.0.0",
	"port": 3000,
	"worker_type": "thread",
	"worker_sum": 4,
	"apis": [{
		"name": "echo",
		"args": [{
			"name": "msg",
			"type": "string"
		}],
		"req_proto": "echomsg",
		"res_proto": "echomsg"
	}]
}
```

## 4. **普通服务描述**
定义普通服务，即不接受rpc请求的后台服务，对应描述文件中的self_server字段，如下json片段是一些常见的例子
> * dispatch_type：支持simple和custom两种，simple会生成worker_sum个工作者，做同样的任务；custom会生成若干个工作组，工作组之间做不同的任务
> * worker_type：支持process、thread、coroutine和process_coroutine四种，其中process_coroutine会生成worker_sum个进程、每个进程coroutine_sum个协程

```json
"self_server": {
	"dispatch_type": "simple",
	"worker_type": "thread",
	"worker_sum": 4
}
```

```json
"self_server": {
	"dispatch_type": "simple",
	"worker_type": "process_coroutine",
	"worker_sum": 2,
	"coroutine_sum": 100
}
```

```json
"self_server": {
	"dispatch_type": "custom",
	"worker_type": "process",
	"groups" : [{
		"group_name": "event",
		"worker_sum": 2
	},{
		"group_name": "value",
		"worker_sum": 2
	}]
}
```

```json
"self_server": {
	"dispatch_type": "custom",
	"worker_type": "process_coroutine",
	"groups" : [{
		"group_name": "event",
		"worker_sum": 2,
		"coroutine_sum": 100
	},{
		"group_name": "value",
		"worker_sum": 2,
		"coroutine_sum": 100
	}]
}
```

```json
"self_server": {
	"dispatch_type": "simple",
	"worker_type": "coroutine",
	"worker_sum": 100
}
```

```json
"self_server": {
	"dispatch_type": "custom",
	"worker_type": "coroutine",
	"groups" : [{
		"group_name": "event",
		"worker_sum": 2
	},{
		"group_name": "value",
		"worker_sum": 3
	}]
}
```

# 创建echo服务
- git clone https://github.com/jackdai123/pysvrkit.git
- mkdir echo && cd echo
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
			"type": "list"
		},{
			"name": "vec_string",
			"type": "list"
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
			"name": "echo",
			"args": [{
				"name": "my_string",
				"type": "string"
			},{
				"name": "vec_int",
				"type": "list"
			},{
				"name": "vec_string",
				"type": "list"
			}],
			"req_proto": "echomsg",
			"res_proto": "echomsg"
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
- ../pysvrkit/bin/gen_svr.py -f echo.json -d .
- ls -l
```bash
-rwxrwxr--. 1 vagrant vagrant  991 Sep 27 05:44 echo
-rw-rw-r--. 1 vagrant vagrant  819 Sep 27 05:44 echo.json
-rw-rw-r--. 1 vagrant vagrant  263 Sep 27 05:44 echo_svr.conf
-rw-rw-r--. 1 vagrant vagrant 8791 Sep 27 05:44 echo_svr.py
drwxrwxr-x. 2 vagrant vagrant   96 Sep 27 05:45 global_init
-rw-rw-r--. 1 vagrant vagrant   45 Sep 27 05:44 __init__.py
-rw-rw-r--. 1 vagrant vagrant    6 Sep 27 05:44 README.md
drwxrwxr-x. 2 vagrant vagrant 4096 Sep 27 05:45 rpc_cli
drwxrwxr-x. 2 vagrant vagrant   96 Sep 27 05:45 rpc_handler
drwxrwxr-x. 2 vagrant vagrant   90 Sep 27 05:45 rpc_init
drwxrwxr-x. 2 vagrant vagrant   92 Sep 27 05:45 rpc_proto
drwxrwxr-x. 2 vagrant vagrant   47 Sep 27 05:44 rpc_test
drwxrwxr-x. 2 vagrant vagrant 4096 Sep 27 05:45 self_handler
drwxrwxr-x. 2 vagrant vagrant   92 Sep 27 05:45 self_init
drwxrwxr-x. 2 vagrant vagrant   44 Sep 27 05:44 utils
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

- cat echo_svr.conf
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
- export PYTHONPATH=$(dirname \`pwd\`)
- python echo_svr.py -f echo_svr.conf -d
- ps -efL | grep echo_svr
```bash
vagrant  19430     1 19430  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19431  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19432  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19433  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19434  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19435  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19436  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19437  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19438  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19439  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19440  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19441  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19442  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
vagrant  19430     1 19443  0   14 05:58 ?        00:00:00 python echo_svr.py -f echo_svr.conf -d
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
echo ret <echo.rpc_proto.echo_rpc_proto.echomsg object at 0x1bfb290>
```

# rpc性能测试
- **测试环境**：虚拟机单核512M内存，Intel(R) Core(TM) i3-4130 CPU @ 3.40GHz，客户端和服务端部署在同一台机器，运行100w次echo请求
```python
#修改rpc_test/echo_rpc_test.py，循环100w次
def test_echo(self):
	for i in xrange(1000000):
		self.cli.echo('',[],[])
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

# 反馈与建议
- QQ：26126441
- 微信：david_jlu
- 邮箱：david_jlu@foxmail.com
