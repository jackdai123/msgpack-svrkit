#pragma once

#include <jubatus/msgpack/rpc/server.h>
#include "echo_rpc_proto.h"

namespace echo {

	class echo_rpc_handler : public msgpack::rpc::dispatcher {
		public:
			typedef msgpack::rpc::request msgpack_stream;

		public:
			void dispatch( msgpack_stream stream );

		public:
			void echo( msgpack_stream stream, const echomsg & req );
	};

}
