#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include "log_utils.h"

static int redirect_fds()
{
	close(0);
	close(1);
	close(2);

	if (open("/dev/null", O_RDWR) != 0) {
		return -1;
	}

	dup(0);
	dup(0);

	return 0;
}

static int do_fork()
{
	int status = 0;

	switch(fork())
	{
		case 0:
			break;

		case -1:
			status = -1;
			break;

		default:
			_exit(0);
	}

	return status;
}

namespace echo {

	int daemon() {
		int status = 0;

		if ((status = do_fork()) < 0) {
			log(LOG_ERR, "%s failed to fork: %s", __func__, strerror(errno));
		} else if ((status = setsid()) < 0) {
			log(LOG_ERR, "%s failed to setsid: %s", __func__, strerror(errno));
		} else if ((status = do_fork()) < 0) {
			log(LOG_ERR, "%s failed to fork: %s", __func__, strerror(errno));
		} else {
			umask(0);
			if ((status = chdir("/")) < 0) {
				log(LOG_ERR, "%s failed to chdir: %s", __func__, strerror(errno));
			} else if ((status = redirect_fds()) < 0){
				log(LOG_ERR, "%s failed to redirect_fds: %s", __func__, strerror(errno));
			}
		}

		return status;
	}

}
