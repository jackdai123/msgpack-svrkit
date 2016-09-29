#include "echo_rpc_cli.h"                                                                        
#include "config.h"                                                                              
#include "log_utils.h"                                                                           
#include <jubatus/msgpack/rpc/client.h>                                                          
#include <jubatus/msgpack/rpc/future.h>                                                          
                                                                                                 
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
            log(LOG_ERR, "Config::%s key sum | shardsum not found", __func__);                   
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
                log(LOG_ERR, "Config::%s server%d config err", __func__, i);                     
                return false;                                                                    
            }                                                                                    
                                                                                                 
            this->servers_.push_back(svr); 
        }

        if (this->servers_.empty()) {
            log(LOG_ERR, "Config::%s no servers", __func__);
            return false;
        }
        return true;
    }

    const Endpoint_t * ClientConfig::GetByShard(const int shard_id) const {
        int id = shard_id % this->shard_sum_;
        std::vector<Server_t>::const_iterator it;

        for (it = this->servers_.begin(); it != this->servers_.end(); it++) {
            if (it->shard_begin <= id && id <= it->shard_end) {
                //next: add network check
                return &(it->master);
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

    int Client::echo(const echomsg & req, echomsg * res) {
        //next: add different dist mode, e.g. sharding and consistent_hash
        int shard_id = 0;
        const Endpoint_t * ep = global_client_config.GetByShard(shard_id);

        if (ep) {
            msgpack::rpc::client msgpack_cli(ep->ip, ep->port);
            msgpack::rpc::future callback = msgpack_cli.call("echo", req);
            callback.get< echomsg >((msgpack::rpc::auto_zone*)res);
            return 0;
        }

        return -1;
    }

}
