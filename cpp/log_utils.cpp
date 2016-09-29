#include "log_utils.h"

#include <syslog.h>

namespace echo {

	static vlog_t global_vlog = vsyslog;

	void log(int priority, const char * format, ...) {
		va_list args;
		va_start(args, format);
		global_vlog(priority, format, args);
		va_end(args);
	}

	void setvlog(vlog_t vlog) {
		global_vlog = vlog;
	}

};

