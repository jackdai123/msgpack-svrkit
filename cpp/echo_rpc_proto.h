#pragma once

#include <string>
#include <vector>
#include <msgpack.hpp>

namespace echo {

	class echomsg {
		public:
			std::string my_string;
			std::vector<int> vec_int;
			std::vector<std::string> vec_string;

		public:
			MSGPACK_DEFINE(my_string, vec_int, vec_string);
	};

}
