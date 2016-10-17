# msgpack-svrkit简介
msgpack-svrkit是一个用来生成cpp、python等多语言服务框架（skeleton）的工具，主要为了提升后台工程师的开发效率，特点如下：
> * **基于msgpack的rpc** ：[msgpack](http://msgpack.org/)是一个快速精巧的二进制打包协议，支持超过50种开发语言，基于msgpack可以容易的跨语言开发
> * **IDL描述文件** ：使用msgpack-svrkit生成服务代码前，需书写[IDL](http://baike.baidu.com/link?url=lDbMtbnZgrE1cW-N3yBZ35xYWWHPTSUXYxWtH81cduOZ7O7NfLN_IGKRxbHPyvKZkO0Uperzq2wu-f0wMKEduaGdK3j1IyV7vG8WxGrYRAa)文件，定义服务名称、服务工作模式、rpc接口和协议、客户端分布方式等等
> * **两种服务模式** ：支持rpc和普通服务两种服务模式
> * **多种工作模式** ：支持多进程、多线程、协程工作模式
> * **多种客户端分布方式**：暂时只支持分片、一致性哈希两种分布方式

# IDL描述文件
IDL描述文件是一个json文件，主要包括rpc协议、客户端分布、rpc服务描述、普通服务描述四部分：
## 1. **<span id="rpc_proto">rpc协议<span>**
定义rpc协议数据结构，对应描述文件中的protos字段

> * name：定义数据结构的名称
> * fields：定义数据结构包含的字段
> * fields.name：定义一个字段的名称
> * fields.type：定义一个字段的数据类型，支持类型有string、bool、int、float、list、dict、自定义数据结构
> * fields.subtype：定义一个字段数据类型的子类型，支持子类型有string、bool、int、float、自定义数据结构

如下json片段定义了包含3个字段、名叫echomsg的数据结构，其中vec_string是个字符串数组、dict_float是key为整形、value为浮点型的字典
另外一个数据结构response支持数据结构嵌套，内部嵌套了之前定义的echomsg

```json
"protos": [{
	"name": "echomsg",
	"fields": [{
		"name": "my_bool",
		"type": "bool"
	},{
		"name": "vec_string",
		"type": "list",
		"subtype": "string"
	},{
		"name": "dict_float",
		"type": "dict",
		"subtype": "int:float"
	}]
},{
	"name": "response",
	"fields": [{
		"name": "echo",
		"type": "echomsg"
	},{
		"name": "vec_echo",
		"type": "list",
		"subtype": "echomsg"
	},{
		"name": "dict_echo",
		"type": "dict",
		"subtype": "int:echomsg"
	}]

}]
```

## 2. **客户端分布**
msgpack-svrkit由客户端来决定路由，即请求发送到哪台服务器，对应描述文件中的rpc_client.mode字段，目前只支持sharding和hashring两种模式

> * hashring：即[一致性哈希](http://blog.csdn.net/cywosp/article/details/23397179/)分布方式，适合无状态服务
> * sharding：根据客户端ID分片，适合有状态服务，比如存储服务

如下json片段定义使用hashring分布方式

```json
"rpc_client": {
	"mode": "hashring"
}
```

## 3. **rpc服务描述**
定义rpc服务，对应描述文件中的rpc_server字段

> * ip：定义rpc服务监听的ip，比如127.0.0.1
> * port：定义rpc服务监听的端口，比如3000
> * worker_type：定义工作模式，只支持process和thread两种
> * worker_sum：定义rpc工作者的数量
> * apis：定义服务提供的接口
> * apis.name：定义接口的名称
> * apis.req_proto: 定义接口请求的数据类型，见[rpc协议](#rpc_proto)
> * apis.res_proto: 定义接口响应的数据类型，见[rpc协议](#rpc_proto)

如下json片段定义一个多线程、有4个rpc接口的echo服务

```json
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
}
```

## 4. **普通服务描述**
定义普通服务，即不接受rpc请求的后台服务，对应描述文件中的self_server字段

> * dispatch_type：支持simple和custom两种，simple会生成worker_sum个工作者，做同样的任务；custom会生成若干个工作组，工作组之间做不同的任务
> * worker_type：支持process、thread、coroutine和process_coroutine四种，其中process_coroutine会生成worker_sum个进程、每个进程coroutine_sum个协程

如下json片段是一些常见的例子

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

# msgpack-svrkit使用
msgpack-svrkit提供gen_svr.py工具，在主目录的bin下面，输入IDL文件和要生成服务的语言即可，下面以echo服务为例说明

- cd ~ && git clone https://github.com/jackdai123/msgpack-svrkit.git
- ~/msgpack-svrkit/bin/gen_svr.py
```bash
Usage:
		/home/vagrant/msgpack-svrkit/bin/gen_svr.py -f /path/to/svr.json -g lang1,lang2,lang3 -d .
Options:
		-f    svr description file
		-g    languages(cpp,python,java) for generate
		-d    directory of svr code
		-h    show help
Examples:
		/home/vagrant/msgpack-svrkit/bin/gen_svr.py -f /path/to/svr.json -g python -d .
		/home/vagrant/msgpack-svrkit/bin/gen_svr.py -f /path/to/svr.json -g python,cpp,java -d .
```
- cd ~ && mkdir echo && cd echo && cp ~/msgpack-svrkit/sample/svr_sample7.json ./echo.json
- ~/msgpack-svrkit/bin/gen_svr.py -f echo.json -g python,cpp -d .
- ls -l
```bash
total 16
drwxrwxr-x. 2 vagrant vagrant 4096 Oct 10 06:47 cpp
-rw-rw-r--. 1 vagrant vagrant  635 Oct 10 02:12 echo.json
-rw-rw-r--. 1 vagrant vagrant   45 Oct 10 06:47 __init__.py
drwxrwxr-x. 9 vagrant vagrant 4096 Oct 10 06:47 python
```
- ls -l cpp
```bash
total 100
-rw-rw-r--. 1 vagrant vagrant 2454 Oct 10 06:47 config.cpp
-rw-rw-r--. 1 vagrant vagrant  554 Oct 10 06:47 config.h
-rw-rw-r--. 1 vagrant vagrant 1129 Oct 10 06:47 daemon.cpp
-rw-rw-r--. 1 vagrant vagrant   50 Oct 10 06:47 daemon.h
-rwxrwxr--. 1 vagrant vagrant  852 Oct 10 06:47 echo
-rw-rw-r--. 1 vagrant vagrant  239 Oct 10 06:47 echo_rpc_cli.conf
-rw-rw-r--. 1 vagrant vagrant 5130 Oct 10 06:47 echo_rpc_cli.cpp
-rw-rw-r--. 1 vagrant vagrant 1100 Oct 10 06:47 echo_rpc_cli.h
-rw-rw-r--. 1 vagrant vagrant 1352 Oct 10 06:47 echo_rpc_handler.cpp
-rw-rw-r--. 1 vagrant vagrant  493 Oct 10 06:47 echo_rpc_handler.h
-rw-rw-r--. 1 vagrant vagrant  300 Oct 10 06:47 echo_rpc_proto.h
-rw-rw-r--. 1 vagrant vagrant 2815 Oct 10 06:47 echo_rpc_test.cpp
-rw-rw-r--. 1 vagrant vagrant 1143 Oct 10 06:47 echo_rpc_test.h
-rw-rw-r--. 1 vagrant vagrant  117 Oct 10 06:47 echo_svr.conf
-rw-rw-r--. 1 vagrant vagrant 3281 Oct 10 06:47 echo_svr.cpp
-rw-rw-r--. 1 vagrant vagrant  397 Oct 10 06:47 echo_svr.h
-rw-rw-r--. 1 vagrant vagrant 1498 Oct 10 06:47 file_utils.cpp
-rw-rw-r--. 1 vagrant vagrant  274 Oct 10 06:47 file_utils.h
-rw-rw-r--. 1 vagrant vagrant  314 Oct 10 06:47 log_utils.cpp
-rw-rw-r--. 1 vagrant vagrant  263 Oct 10 06:47 log_utils.h
-rw-rw-r--. 1 vagrant vagrant 1470 Oct 10 06:47 Makefile
-rw-rw-r--. 1 vagrant vagrant 1777 Oct 10 06:47 opt_map.cpp
-rw-rw-r--. 1 vagrant vagrant  712 Oct 10 06:47 opt_map.h
-rw-rw-r--. 1 vagrant vagrant    6 Oct 10 06:47 README.md
```
- ls -l python
```bash
total 28
-rwxrwxr--. 1 vagrant vagrant  991 Oct 10 06:47 echo
-rw-rw-r--. 1 vagrant vagrant  106 Oct 10 06:47 echo_svr.conf
-rw-rw-r--. 1 vagrant vagrant 8918 Oct 10 06:47 echo_svr.py
drwxrwxr-x. 2 vagrant vagrant   50 Oct 10 06:47 global_init
-rw-rw-r--. 1 vagrant vagrant   45 Oct 10 06:47 __init__.py
-rw-rw-r--. 1 vagrant vagrant    6 Oct 10 06:47 README.md
drwxrwxr-x. 2 vagrant vagrant   70 Oct 10 06:47 rpc_cli
drwxrwxr-x. 2 vagrant vagrant   50 Oct 10 06:47 rpc_handler
drwxrwxr-x. 2 vagrant vagrant   47 Oct 10 06:47 rpc_init
drwxrwxr-x. 2 vagrant vagrant   48 Oct 10 06:47 rpc_proto
drwxrwxr-x. 2 vagrant vagrant   47 Oct 10 06:47 rpc_test
drwxrwxr-x. 2 vagrant vagrant   44 Oct 10 06:47 utils
```

# 多语言服务使用细节
- [cpp](https://github.com/jackdai123/msgpack-svrkit/tree/master/cpp)
- [python](https://github.com/jackdai123/msgpack-svrkit/tree/master/python)

# 反馈与建议
- QQ：26126441
- 微信：david_jlu
- 邮箱：david_jlu@foxmail.com
