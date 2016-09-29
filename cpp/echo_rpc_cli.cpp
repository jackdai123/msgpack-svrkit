#include "config.h"                                                                              
#include "log_utils.h"                                                                           
#include "echo_rpc_cli.h"                                                                        
#include <jubatus/msgpack/rpc/client.h>                                                          
#include <jubatus/msgpack/rpc/future.h>                                                          
#include <exception>

namespace echo {                                                                                 

	ClientConfig::ClientConfig() {                                                               
	}                                                                                            

	ClientConfig::~ClientConfig() {                                                              
	}                                                                                            

	bool ClientConfig::Read(const char * config_file) {                                          
		Config config;                                                                           
		if (!config.InitConfig(config_file)) {                                                   
			return false;                                                                        
		}                                                                                        

		int count = 0;                                                                           
		bool succ = true;                                                                        
		succ &= config.ReadItem("server", "sum", &count);                                        
		succ &= config.ReadItem("server", "shardsum", &(this->shard_sum_));                      
		if (!succ) {                                                                             
			log(LOG_ERR, "ClientConfig::%s key sum | shardsum not found", __func__);                   
			return false;                                                                        
		}                                                                                        

		for (int i = 0; i < count; i++) {                                                        
			char section[64] = { 0 };                                                            
			snprintf(section, sizeof(section), "server%d", i);                                   

			Server_t svr;                                                                        
			succ = true;                                                                         
			succ &= config.ReadItem(section, "ip", svr.master.ip, sizeof(svr.master.ip));        
			succ &= config.ReadItem(section, "port", &(svr.master.port));                        
			succ &= config.ReadItem(section, "ip_bak", svr.slave.ip, sizeof(svr.slave.ip));      
			succ &= config.ReadItem(section, "port_bak", &(svr.slave.port));                     
			succ &= config.ReadItem(section, "shardbegin", &(svr.shard_begin));                  
			succ &= config.ReadItem(section, "shardend", &(svr.shard_end));                      
			if (!succ) {                                                                         
				log(LOG_ERR, "ClientConfig::%s server%d config err", __func__, i);                     
				return false;                                                                    
			}                                                                                    

			this->servers_.push_back(svr); 
		}

		if (this->servers_.empty()) {
			log(LOG_ERR, "ClientConfig::%s no servers", __func__);
			return false;
		}
		return true;
	}

	const Server_t * ClientConfig::GetByShard(const int shard_id) const {
		int id = shard_id % this->shard_sum_;

		for (size_t i = 0; i < this->servers_.size(); i++) {
			if (this->servers_[i].shard_begin <= id && id <= this->servers_[i].shard_end) {
				return &(this->servers_[i]);
			}
		}

		return NULL;
	}

	static ClientConfig global_client_config;

	Client::Client() {
	}

	Client::~Client() {
	}

	bool Client::Init(const char * config_file) {
		return global_client_config.Read(config_file);
	}

	int Client::echo(int shard_id, const echomsg & req, echomsg & res) {
		//next: add different dist mode, e.g. consistent_hash
		const Server_t * svr = global_client_config.GetByShard(shard_id);

		if (svr) {
			try {
				msgpack::rpc::client msgpack_cli(svr->master.ip, svr->master.port);
				msgpack::rpc::future callback = msgpack_cli.call("echo", req);
				res = callback.get< echomsg >();
			} catch (std::exception & e) {
				log(LOG_ERR, "Client::%s master[%s:%d] %s", __func__, svr->master.ip, svr->master.port, e.what());
				try {
					msgpack::rpc::client msgpack_cli(svr->slave.ip, svr->slave.port);
					msgpack::rpc::future callback = msgpack_cli.call("echo", req);
					res = callback.get< echomsg >();
				} catch (std::exception & e) {
					log(LOG_ERR, "Client::%s slave[%s:%d] %s", __func__, svr->slave.ip, svr->slave.port, e.what());
					return -1;
				}
			}
			return 0;
		}

		return -1;
	}

}
