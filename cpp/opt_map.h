#pragma once

#include <vector>
#include <string>
#include <map>

namespace ${app} {

	class OptMap {
		public:
			OptMap(const char * optstring);

			virtual ~OptMap();

			bool Parse(int argc, char * argv[]);

			bool Has(char c) const;

			size_t Count(char c) const;

			const char * Get(char c, size_t index = 0) const;

			bool GetInt(char c, int * val, size_t index = 0) const;

			bool GetUInt(char c, unsigned int * val, size_t index = 0) const;

			size_t GetNonOptCount();

			const char * GetNonOpt(size_t index);

		private:
			char * opt_string_;

			typedef std::map<char, std::vector<const char *>, std::less<char> > option_map_;
			option_map_ opt_;

			std::vector<std::string> non_opt_;
	};

}

