#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include "config.h"
#include "file_utils.h"

namespace ${app} {

	Config :: Config() {
	}

	Config :: ~Config() {
	}

	bool Config::InitConfig(const char * path) {
		return FileUtils::ReadFile(path, &content_);
	}

	bool Config::ReadItem(const char * section, const char * key, int * value) {
		char tmp[128] = { 0 };
		bool ret = ReadItem(section, key, tmp, sizeof(tmp));
		if (ret) {
			*value = atoi(tmp);
		}
		return ret;
	}

	bool Config::ReadItem(const char * section, const char * key, int * value, const int default_value) {
		char tmp[128] = { 0 };
		bool ret = ReadItem(section, key, tmp, sizeof(tmp));
		if (ret) {
			*value = atoi(tmp);
		} else {
			*value = default_value;
		}
		return ret;
	}

	bool Config::ReadItem(const char * section, const char * key, 
			char * value, size_t size, const char * default_value) {
		bool ret = ReadItem(section, key, value, size);
		if (!ret) {
			snprintf(value, size, "%s", default_value ? default_value : "");
		}

		return ret;
	}

	bool Config::ReadItem(const char * section, const char * key, char * value, size_t size) {
		bool ret = false;

		char tmp_section[128] = { 0 };
		snprintf(tmp_section, sizeof(tmp_section), "\n[%s]", section);

		char tmp_key[128] = { 0 };
		snprintf(tmp_key, sizeof(tmp_key), "\n%s", key);

		const char * end_pos = NULL;
		const char * pos = strstr(content_.c_str(), tmp_section);
		if (NULL != pos) {
			pos = strchr(pos + 1, '\n');
			if (NULL == pos)
				pos = strchr(content_.c_str(), '\0');

			end_pos = strstr(pos, "\n[");
			if (NULL == end_pos)
				end_pos = strchr(pos, '\0');
		}

		for (; NULL != pos && pos < end_pos;) {
			pos = strstr(pos, tmp_key);

			if (NULL == pos || pos > end_pos)
				break;

			const char * tmp_pos = pos + strlen(tmp_key);
			if ((!isspace(*tmp_pos)) && ('=' != *tmp_pos))
				continue;

			pos++;

			const char * eol = strchr(pos, '\n');
			if (NULL == eol)
				eol = strchr(pos, '\0');

			tmp_pos = strchr(pos, '=');
			if (NULL != tmp_pos && tmp_pos < eol) {
				ret = true;

				for (tmp_pos++; tmp_pos <= eol && isspace(*tmp_pos);)
					tmp_pos++;

				for (size_t i = 0; tmp_pos <= eol && i < (size - 1); i++) {
					if (isspace(*tmp_pos))
						break;
					*(value++) = *(tmp_pos++);
				}

				*value = '\0';

				break;
			}
		}

		return ret;
	}

}
