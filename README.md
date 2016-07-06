#pysvrkit简介
**pysvrkit**是一个用来生成python服务框架（skeleton）的工具，主要为了提升后台python工程师的开发效率，特点如下：
- **基于msgpack的rpc** ：[msgpack](http://msgpack.org/)是一个快速精巧的二进制打包协议，支持超过50种开发语言，基于msgpack可以容易的跨语言开发；
- **IDL描述文件** ：使用pysvrkit生成服务代码前，需书写[IDL](http://baike.baidu.com/link?url=lDbMtbnZgrE1cW-N3yBZ35xYWWHPTSUXYxWtH81cduOZ7O7NfLN_IGKRxbHPyvKZkO0Uperzq2wu-f0wMKEduaGdK3j1IyV7vG8WxGrYRAa)文件，定义服务名称、服务工作模式、rpc接口和协议、客户端分布方式等等；
- **多种工作模式** ：支持多进程、多线程、协程工作模式，根据使用场景不同在IDL描述文件选择不同的工作模式。
- **多种客户端分布方式**：支持分片、一致性哈希等多种分布方式，根据使用场景不同在IDL描述文件选择不同的分布式方式

#IDL描述文件
**IDL描述文件**是一个json文件，主要包括rpc协议、客户端分布、rpc服务描述、普通服务描述四部分：
- **rpc协议**：定义rpc协议数据结构，对应描述文件中的protos字段，如下json片段定义了只包含一个字符串字段名叫echomsg结构，其中字段类型支持string、bool、int、float、list、tuple、dict
        - name：定义数据结构的名称
        - fields：定义数据结构包含的字段
        - fields.name：定义一个字段的名称
        - fields.type：定义一个字段的数据类型
```json
        "protos": [{
                "name": "echomsg",
                "fields": [{
                        "name": "value",
                        "type": "string"
                }]
        }]
```
- **客户端分布**：pysvrkit由客户端来决定路由，即请求发送到哪台服务器，对应描述文件中的rpc_client.mode字段，目前只支持sharding和hashring两种模式，如下json片段使用hashring
        - hashring：即[一致性哈希](http://blog.csdn.net/cywosp/article/details/23397179/)分布方式，适合无状态服务
        - sharding：根据客户端ID分片，适合有状态的比如存储服务
```json
    "rpc_client": {
                "mode": "hashring"
    }
```
- **rpc服务描述**：定义rpc服务，对应描述文件中的rpc_server字段，如下json片段定义一个echo服务，只有一个echo接口
        - ip：定义rpc服务监听的ip
        - port：定义rpc服务监听的端口
        - worker_type：只支持process和thread两种
        - worker_sum：定义rpc工作者的数量
        - apis：定义服务提供的接口
        - apis.name：定义接口的名称
        - apis.args：定义接口参数
        - apis.args.name：定义接口参数的名称
        - apis.args.type：定义接口参数的数据类型
        - apis.ret：定义是否有返回值
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
                                "type": "echomsg"
                        }],
                        "ret": true
                }]
    }
```
- **普通服务描述**：定义普通服务，即不接受rpc请求的后台服务，对应描述文件中的self_server字段，如下json片段是一些常见的例子
        - dispatch_type：只支持simple和custom两种simple会生成worker_sum个工作者，做同样的任务；custom会生成若干个工作组，工作组之间做不同的任务
        - worker_type：只支持process、thread和process_coroutine三种，其中process_coroutine会生成worker_sum个进程、每个进程coroutine_sum个协程
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

#创建echo服务
- git clone https://github.com/jackdai123/pysvrkit.git
- mkdir echo && cd echo
- cat svr.json
```json
{
        "app": "echo",

        "protos": [{
                "name": "echomsg",
                "fields": [{
                        "name": "value",
                        "type": "string"
                }]
        }],

        "rpc_client": {
                "mode": "hashring"
        },

        "rpc_server": {
                "ip": "0.0.0.0",
                "port": 3000,
                "worker_type": "thread",
                "worker_sum": 4,
                "apis": [{
                        "name": "echo",
                        "args": [{
                                "name": "msg",
                                "type": "echomsg"
                        }],
                        "ret": true
                }]
        },

        "self_server": {
                "dispatch_type": "custom",
                "worker_type": "process_coroutine",
                "groups" : [{
                        "group_name": "event",
                        "worker_sum": 2,
                        "coroutine_sum": 3
                },{
                        "group_name": "value",
                        "worker_sum": 2,
                        "coroutine_sum": 3
                }]
        }
}
```
- ../pysvrkit/gen_svr.py -f svr.json -d .
- ls -l
```bash
-rwxrwxr--. 1 vagrant vagrant  890 Jul  5 09:43 echo
-rw-rw-r--. 1 vagrant vagrant  165 Jul  5 09:43 echo_cli.conf
-rw-rw-r--. 1 vagrant vagrant 4186 Jul  5 09:43 echo_cli.py
-rw-rw-r--. 1 vagrant vagrant  287 Jul  5 09:43 echo_proto.py
-rw-rw-r--. 1 vagrant vagrant  132 Jul  5 09:43 echo_rpc_handler.py
-rw-rw-r--. 1 vagrant vagrant  241 Jul  5 09:43 echo_self_event_handler.py
-rw-rw-r--. 1 vagrant vagrant  433 Jul  5 09:43 echo_self_handler.py
-rw-rw-r--. 1 vagrant vagrant  241 Jul  5 09:43 echo_self_value_handler.py
-rw-rw-r--. 1 vagrant vagrant  302 Jul  5 09:43 echo_svr.conf
-rw-rw-r--. 1 vagrant vagrant 8886 Jul  5 09:43 echo_svr.py
-rw-rw-r--. 1 vagrant vagrant  251 Jul  5 09:43 echo_test.py
-rw-rw-r--. 1 vagrant vagrant  633 Jul  5 08:33 svr.json
```
- cat echo_svr.conf
```ini
[app]
name=echo
pid=/tmp/echo.pid

[rpc_server]
ip=0.0.0.0
port=3000
worker_type=thread
worker_sum=4

[self_server]
dispatch_type=custom
worker_type=process_coroutine
group_sum=2

[self_group0]
group_name=event
worker_sum=2
coroutine_sum=3

[self_group1]
group_name=value
worker_sum=2
coroutine_sum=3

```
- ./echo start
- ps -ef | grep echo_svr
```bash
vagrant  22236     1  1 09:48 ?        00:00:00 python /home/vagrant/echo/echo_svr.py -f /home/vagrant/echo/echo_svr.conf -d
vagrant  22243 22236  1 09:48 ?        00:00:00 python /home/vagrant/echo/echo_svr.py -f /home/vagrant/echo/echo_svr.conf -d
vagrant  22245 22243  0 09:48 ?        00:00:00 python /home/vagrant/echo/echo_svr.py -f /home/vagrant/echo/echo_svr.conf -d
vagrant  22246 22243  0 09:48 ?        00:00:00 python /home/vagrant/echo/echo_svr.py -f /home/vagrant/echo/echo_svr.conf -d
vagrant  22247 22243  0 09:48 ?        00:00:00 python /home/vagrant/echo/echo_svr.py -f /home/vagrant/echo/echo_svr.conf -d
vagrant  22248 22243  0 09:48 ?        00:00:00 python /home/vagrant/echo/echo_svr.py -f /home/vagrant/echo/echo_svr.conf -d
```
- cat echo_cli.conf
```ini
[server]
sum=3
mode=hashring

[server0]
ip=127.0.0.1
port=3000
weight=100

[server1]
ip=127.0.0.1
port=3000
weight=100

[server2]
ip=127.0.0.1
port=3000
weight=100
```
- cat echo_rpc_handler.py
```python
def echo(msg,):
        return msg.value
```
- cat echo_test.py
```python
def test_echo():
        cli = echo_cli.Client('echo_cli.conf')
        msg = echo_proto.echomsg()
        msg.value = 'testtest'
        print cli.echo(msg,)
```
- python echo_test.py
```
testtest
```
- ./echo stop

#rpc性能测试
- **测试环境**：虚拟机单核512M内存，Intel(R) Core(TM) i3-4130 CPU @ 3.40GHz，客户端和服务端部署在同一台机器，运行100w次echo请求
```python
def test_echo():
        cli = echo_cli.Client('echo_cli.conf', 0)
        msg = echo_proto.echomsg()
        for i in xrange(1000000):
                cli.echo(msg,)
```
- **有返回结果的测试**：IDL描述文件中rpc_server.apis.ret设置为false，qps为3000/s
```
real    5m36.347s
user    2m27.468s
sys     0m15.990s
```
- **无返回结果的测试**：IDL描述文件中rpc_server.apis.ret设置为true，qps为1.4w/s
```
real    1m12.819s
user    0m42.881s
sys     0m1.417s
```

#依赖库
- [msgpackrpc](https://github.com/msgpack-rpc/msgpack-rpc-python)
- [daemonize](https://github.com/thesharp/daemonize)
- [gevent](https://github.com/gevent/gevent)
- [consistent_hash](https://github.com/yummybian/consistent-hash)



# 反馈与建议
- 微信：david_jlu
- QQ：26126441
- 邮箱：<david_jlu@foxmail.com>
