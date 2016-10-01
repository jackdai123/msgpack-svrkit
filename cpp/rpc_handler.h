#pragma once

#include <jubatus/msgpack/rpc/server.h>
#include "${app}_rpc_proto.h"

namespace ${app} {

	class ${app}_rpc_handler : public msgpack::rpc::dispatcher {
		public:
			typedef msgpack::rpc::request msgpack_stream;

		public:
			void dispatch( msgpack_stream stream );

