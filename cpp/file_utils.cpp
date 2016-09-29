#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>

#include "file_utils.h"
#include "log_utils.h"

namespace echo {

	bool FileUtils::ReadFile(const char * path, std::string * content) {
		bool ret = false;

		int fd = ::open(path, O_RDONLY);
		if (fd >= 0) {
			struct stat file_stat;
			if (0 == fstat(fd, &file_stat)) {
				content->resize(file_stat.st_size);

				if (read(fd, (char*) content->data(), file_stat.st_size) == file_stat.st_size) {
					ret = true;
				} else {
					log(LOG_ERR, "WARN: read( ..., %llu ) fail, errno %d, %s",
							(unsigned long long) file_stat.st_size, errno, strerror(errno));
				}
			} else {
				log(LOG_ERR, "WARN: stat %s fail, errno %d, %s", path, errno, strerror(errno));
			}

			close(fd);
		} else {
			log(LOG_ERR, "WARN: open %s fail, errno %d, %s", path, errno, strerror(errno));
		}

		return ret;
	}

}
