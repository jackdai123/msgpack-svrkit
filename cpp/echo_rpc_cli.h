#pragma once

#include <vector>
#include "echo_rpc_proto.h"
#include <jubatus/msgpack/rpc/client.h>                                                          

namespace echo {

	typedef struct tagEndpoint {
		char ip[32];
		int port;
	} Endpoint_t;

	typedef struct tagServer {
		Endpoint_t master;
		Endpoint_t slave;
		int shard_begin;
		int shard_end;
	} Server_t;

	class ClientConfig {
		public:
			ClientConfig();
			~ClientConfig();

		public:
			bool Read(const char * config_file);
			const Server_t * GetByShard(const int shard_id) const;

		private:
			int shard_sum_;
			std::vector<Server_t> servers_;
	};

	class Client {
		public:
			static bool Init(const char * config_file);

		public:
			Client();
			Client(int shard_id);
			~Client();

		private:
			void build_client_();
			void destroy_client_();

		public:
			int echo(const echomsg & req, echomsg & res);

		private:
			int shard_id_;
			const Server_t * svr_;
			msgpack::rpc::client * master_cli_;
			msgpack::rpc::client * slave_cli_;
	};

}
