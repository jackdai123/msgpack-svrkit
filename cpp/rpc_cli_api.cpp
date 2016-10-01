	int Client::${api}(const ${req_proto} & req, ${res_proto} & res) {
		try {
			msgpack::rpc::future callback = this->master_cli_->call("${api}", req);
			res = callback.get< ${res_proto} >();
		} catch (std::exception & e) {
			log(LOG_ERR, "Client::%s master[%s:%d] %s", __func__, this->svr_->master.ip, this->svr_->master.port, e.what());
			try {
				msgpack::rpc::future callback = this->slave_cli_->call("${api}", req);
				res = callback.get< ${res_proto} >();
			} catch (std::exception & e) {
				log(LOG_ERR, "Client::%s slave[%s:%d] %s", __func__, this->svr_->slave.ip, this->svr_->slave.port, e.what());
				return -1;
			}
		}

		return 0;
	}

