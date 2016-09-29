#pragma once

#include <stdarg.h>
#include <syslog.h>

namespace echo {

	extern void log(int priority, const char * format, ...) __attribute__((format(printf, 2, 3)));

	typedef void (*vlog_t)(int, const char *, va_list);
	extern void setvlog(vlog_t vlog);

};

