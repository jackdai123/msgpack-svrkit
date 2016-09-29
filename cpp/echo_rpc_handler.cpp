#include <exception>
#include "echo_rpc_handler.h"

namespace echo {

	void echo_rpc_handler :: dispatch( msgpack_stream stream ) {
		try {
			std::string method;
			stream.method().convert(&method);

			if (method == "echo") {
				msgpack::type::tuple< echomsg > req;
				stream.params().convert(&req);
				this->echo( stream, req.get<0>() );
			} else {
				stream.error( msgpack::rpc::NO_METHOD_ERROR );
			}
		} catch( msgpack::type_error & e ) {
			stream.error( msgpack::rpc::ARGUMENT_ERROR );
		} catch( std::exception & e ) {
			stream.error( std::string(e.what()) );
		}
	}

	void echo_rpc_handler :: echo( msgpack_stream stream, const echomsg & req ) {
		//add logic code
		printf( "req: %s [%d, %d] [\'%s\', \'%s\']\n", req.my_string.c_str(),
				req.vec_int[0], req.vec_int[1],
				req.vec_string[0].c_str(), req.vec_string[1].c_str() );

		//construct response
		echomsg res;
		res.my_string = "hi";
		res.vec_int.push_back(2);
		res.vec_int.push_back(4);
		res.vec_string.push_back("fuck");
		res.vec_string.push_back("shit");

		//return response
		stream.result(res);
	}

}
