#pragma once

#include <string>

namespace echo {

	class FileUtils {
		public:
			static bool ReadFile(const char * path, std::string * content);

		private:
			FileUtils();
			~FileUtils();
	};

}

