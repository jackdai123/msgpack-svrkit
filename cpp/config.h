#pragma once

#include <string>

namespace ${app} {

	class Config {
		public:
			Config();
			~Config();

			bool InitConfig(const char * path);
			bool ReadItem(const char * section, const char * key, char * value, size_t size, const char * default_value);
			bool ReadItem(const char * section, const char * key, int * value, const int default_value);

			bool ReadItem(const char * section, const char * key, char * value, size_t size);
			bool ReadItem(const char * section, const char * key, int * value);

		private:
			std::string content_;
	};

}
