#include <exception>
#include "${app}_rpc_handler.h"

namespace ${app} {

	void ${app}_rpc_handler :: dispatch( msgpack_stream stream ) {
		try {
			std::string method;
			stream.method().convert(&method);

			${dispath_code}
			} else {
				stream.error( msgpack::rpc::NO_METHOD_ERROR );
			}
		} catch( msgpack::type_error & e ) {
			stream.error( msgpack::rpc::ARGUMENT_ERROR );
		} catch( std::exception & e ) {
			stream.error( std::string(e.what()) );
		}
	}

