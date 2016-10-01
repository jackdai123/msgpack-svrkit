#include "config.h"
#include "log_utils.h"
#include "${app}_rpc_cli.h"
#include <jubatus/msgpack/rpc/future.h>
#include <exception>

namespace ${app} {

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

	bool Client::Init(const char * config_file) {
		return global_client_config.Read(config_file);
	}

	Client::Client() : shard_id_(0), svr_(NULL), master_cli_(NULL), slave_cli_(NULL) {
		this->build_client_();
	}

	Client::Client(int shard_id) : shard_id_(shard_id), svr_(NULL), master_cli_(NULL), slave_cli_(NULL) {
		this->build_client_();
	}

	Client::~Client() {
		this->destroy_client_();
	}

	void Client::build_client_() {
		this->svr_ = global_client_config.GetByShard(this->shard_id_);
		if (this->svr_) {
			this->master_cli_ = new msgpack::rpc::client(this->svr_->master.ip, this->svr_->master.port);
			this->slave_cli_ = new msgpack::rpc::client(this->svr_->slave.ip, this->svr_->slave.port);
		} else {
			throw std::runtime_error("failed to GetByShard");
		}
	}

	void Client::destroy_client_() {
		this->master_cli_->close();
		this->slave_cli_->close();
		delete this->master_cli_;
		delete this->slave_cli_;
	}

