#include "config.h"
#include "log_utils.h"                                                                           
#include "file_utils.h"
#include "${app}_svr.h"
#include "${app}_rpc_handler.h"
#include "daemon.h"
#include <sstream>

namespace ${app} {

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
			printf("ServerConfig::%s app name | pid not found\n", __func__);
			return succ;
		}

		succ = true;
		succ &= config.ReadItem("rpc_server", "ip", this->ip_, sizeof(this->ip_));
		succ &= config.ReadItem("rpc_server", "port", &(this->port_));
		succ &= config.ReadItem("rpc_server", "worker_sum", &(this->worker_sum_));
		if (!succ) {
			printf("ServerConfig::%s rpc_server ip | port | worker_sum not found\n", __func__);
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

using namespace ${app};

static void write_pid_file(const char * pid_file) {
	std::stringstream ss;
	std::string pid_str;
	ss << getpid();
	ss >> pid_str;
	if ( ! FileUtils::WriteFile( pid_file, pid_str ) ) {
		printf("%s failed to write pidfile %s\n", __func__, pid_file);
		exit( 0 );
	}
}

static void showUsage( const char * program ) {
	printf( "Usage:\n" );
	printf( "          %s [-c <config>] [-d] [-h]\n", program );
	printf( "Options:\n" );
	printf( "          -c\tconfigure file of server\n" );
	printf( "          -d\trun as daemon\n" );
	printf( "          -h\tshow help\n" );
	printf( "Examples:\n" );
	printf( "          %s -c ${app}_svr.conf -d\n", program );
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

	if (config.GetPidFile() != "") {
		write_pid_file( config.GetPidFile().c_str() );
	}

	if (daemon_flag) {
		daemon();
	}

	msgpack::rpc::server svr;
	std::auto_ptr<msgpack::rpc::dispatcher> dp( new ${app}_rpc_handler );
	svr.serve( dp.get() );
	svr.listen( config.GetIP(), config.GetPort() );
	svr.run( config.GetWorkerSum() );

	return 0;
}
