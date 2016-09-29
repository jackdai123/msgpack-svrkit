#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "opt_map.h"

namespace echo {

	OptMap::OptMap(const char * optstring) {
		opt_string_ = strdup(optstring);
	}

	OptMap::~OptMap() {
		if (NULL != opt_string_)
			free(opt_string_);
	}

	bool OptMap::Parse(int argc, char * argv[]) {
		bool ret = true;

		int c = 0;

		while ((c = getopt(argc, argv, opt_string_)) != EOF) {
			if ('?' == c || ':' == c) {
				ret = false;
			} else {
				opt_[c].push_back((NULL == ::optarg) ? "" : ::optarg);
			}
		}

		for (int i = optind; i < argc; i++) {
			non_opt_.push_back(argv[i]);
		}

		return ret;
	}

	size_t OptMap::GetNonOptCount() {
		return non_opt_.size();
	}

	const char * OptMap::GetNonOpt(size_t index) {
		if (index >= 0 && index < non_opt_.size()) {
			return non_opt_[index].c_str();
		}

		return NULL;
	}

	bool OptMap::Has(char c) const {
		const option_map_::const_iterator iter = opt_.find(c);

		return opt_.end() != iter;
	}

	size_t OptMap::Count(char c) const {
		const option_map_::const_iterator iter = opt_.find(c);

		return (opt_.end() != iter) ? iter->second.size() : 0;
	}

	const char * OptMap::Get(char c, size_t index) const {
		const option_map_::const_iterator iter = opt_.find(c);

		if (opt_.end() != iter) {
			if (index >= iter->second.size()) {
				return NULL;
			} else {
				return iter->second[index];
			}
		} else {
			return NULL;
		}
	}

	bool OptMap::GetInt(char c, int * val, size_t index) const {
		const char * tmp = Get(c, index);

		if (NULL != tmp)
			*val = atoi(tmp);

		return NULL != tmp;
	}

	bool OptMap::GetUInt(char c, unsigned int * val, size_t index) const {
		const char * tmp = Get(c, index);

		if (NULL != tmp)
			*val = strtoul(tmp, NULL, 10);

		return NULL != tmp;
	}

}
