#pragma once

#include <string>

namespace ${app} {

	class ServerConfig {
		public:
			ServerConfig();
			~ServerConfig();

		public:
			bool Read( const char * config_file );

		public:
			std::string GetPidFile();
			std::string GetIP();
			int GetPort();
			int GetWorkerSum();

		private:
			char app_name_[64];
			char pid_file_[256];
			char ip_[32];
			int port_;
			int worker_sum_;
	};

}
