#include "config.h"
#include "log_utils.h"                                                                           
#include "file_utils.h"
#include "echo_svr.h"
#include "echo_rpc_handler.h"
#include "daemon.h"
#include <sstream>

namespace echo {

	ServerConfig :: ServerConfig() {
		memset(this->app_name_, 0, sizeof(this->app_name_));
		memset(this->pid_file_, 0, sizeof(this->pid_file_));
		memset(this->ip_, 0, sizeof(this->ip_));
		this->port_ = -1;
		this->worker_sum_ = 0;
	}

	ServerConfig :: ~ServerConfig() {
	}

	bool ServerConfig :: Read( const char * config_file ) {
		Config config;
		if (!config.InitConfig(config_file)) {
			return false;
		}

		bool succ = true;
		succ &= config.ReadItem("app", "name", this->app_name_, sizeof(this->app_name_));
		succ &= config.ReadItem("app", "pid", this->pid_file_, sizeof(this->pid_file_));
		if (!succ) {
			log(LOG_ERR, "ServerConfig::%s app name | pid not found", __func__);
			return succ;
		}

		succ = true;
		succ &= config.ReadItem("rpc_server", "ip", this->ip_, sizeof(this->ip_));
		succ &= config.ReadItem("rpc_server", "port", &(this->port_));
		succ &= config.ReadItem("rpc_server", "worker_sum", &(this->worker_sum_));
		if (!succ) {
			log(LOG_ERR, "ServerConfig::%s rpc_server ip | port | worker_sum not found", __func__);
		}

		return succ;
	}

	std::string ServerConfig :: GetPidFile() {
		return this->pid_file_;
	}

	std::string ServerConfig :: GetIP() {
		return this->ip_;
	}

	int ServerConfig :: GetPort() {
		return this->port_;
	}

	int ServerConfig :: GetWorkerSum() {
		return this->worker_sum_;
	}

}

using namespace echo;

static void write_pid_file(const char * pid_file) {
	std::stringstream ss;
	std::string pid_str;
	ss << getpid();
	ss >> pid_str;
	if ( ! FileUtils::WriteFile( pid_file, pid_str ) ) {
		log(LOG_ERR, "%s failed to write pidfile %s", __func__, pid_file);
		exit( 0 );
	}
}

static void showUsage( const char * program ) {
	printf( "Usage:\n          %s [-c <config>] [-d] [-h]\nExamples:\n", program );
	printf( "          %s -c svr.conf -d\n", program );
	exit( 0 );
}

int main( int argc, char * argv[] ) {
	int c ;
	const char * config_file = NULL;
	extern char * optarg ;
	bool daemon_flag = false;

	while( ( c = getopt( argc, argv, "c:dh" ) ) != EOF ) {
		switch ( c ) {
			case 'c':
				config_file = optarg;
				break;
			case 'd':
				daemon_flag = true;
				break;
			case 'h':
			default:
				showUsage( argv[0] );
				break;
		}
	}

	assert(signal(SIGPIPE, SIG_IGN) != SIG_ERR);
	assert(signal(SIGINT, SIG_DFL) != SIG_ERR);
	assert(signal(SIGTERM, SIG_DFL) != SIG_ERR);

	if( NULL == config_file ) {
		showUsage( argv[0] );
	}

	ServerConfig config;
	if( ! config.Read( config_file ) ) {
		showUsage( argv[0] );
	}

	if (daemon_flag) {
		daemon();
	}

	if (config.GetPidFile() != "") {
		write_pid_file( config.GetPidFile().c_str() );
	}

	msgpack::rpc::server svr;
	std::auto_ptr<msgpack::rpc::dispatcher> dp( new echo_rpc_handler );
	svr.serve( dp.get() );
	svr.listen( config.GetIP(), config.GetPort() );
	svr.run( config.GetWorkerSum() );

	return 0;
}
