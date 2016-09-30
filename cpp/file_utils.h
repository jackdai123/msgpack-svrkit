#pragma once

#include <string>

namespace echo {

	class FileUtils {
		public:
			static bool ReadFile(const char * path, std::string * content);
			static bool WriteFile(const char * path, const std::string & content);

		private:
			FileUtils();
			~FileUtils();
	};

}

