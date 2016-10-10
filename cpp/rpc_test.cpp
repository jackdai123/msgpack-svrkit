#include <stdio.h>
#include "${app}_rpc_test.h"
#include "${app}_rpc_cli.h"

namespace ${app} {

	TestTool :: TestTool() {
	}

	TestTool :: ~TestTool() {
	}

${api}
	TestToolImpl:: TestToolImpl() {
	}

	TestToolImpl:: ~TestToolImpl() {
	}

${func}
}

using namespace ${app};

void showUsage( const char * program )
{
	printf( "Usage:\n" );
	printf( "          %s [-c <config>] [-f <func>] [-h]\n", program );
	printf( "Options:\n" );
	printf( "          -c\tconfigure file of client\n" );
	printf( "          -f\trpc method or function\n" );
	printf( "          -h\tshow help\n" );
	printf( "Examples:\n");

	TestTool::Name2Func_t * name2func = TestTool::GetName2Func();

	for( int i = 0; ; i++ ) {
		TestTool::Name2Func_t * iter = &( name2func[i] );

		if( NULL == iter->name ) break;

		printf( "          %s -c ${app}_rpc_cli.conf -f %s %s\n", program, iter->name, iter->usage );
	}

	exit( 0 );
}

int main( int argc, char * argv[] )
{
	const char * func = NULL;
	const char * config = NULL;

	for( int i = 1; i < argc - 1; i++ ) {
		if( 0 == strcmp( argv[i], "-c" ) ) {
			config = argv[ ++i ];
		}
		if( 0 == strcmp( argv[i], "-f" ) ) {
			func = argv[ ++i ];
		}
		if( 0 == strcmp( argv[i], "-h" ) ) {
			showUsage( argv[0] );
		}
	}

	if( NULL == func ) showUsage( argv[0] );

	if( NULL != config ) Client::Init( config );

	TestTool::Name2Func_t * target = NULL;

	TestTool::Name2Func_t * name2func = TestTool::GetName2Func();

	for( int i = 0; i < 100; i++ ) {
		TestTool::Name2Func_t * iter = &( name2func[i] );

		if( NULL == iter->name ) break;

		if( 0 == strcasecmp( func, iter->name ) ) {
			target = iter;
			break;
		}
	}

	if( NULL == target ) showUsage( argv[0] );

	OptMap opt_map( target->opt_string );

	if( ! opt_map.Parse( argc, argv ) ) showUsage( argv[0] );

	TestTool::ToolFunc_t targefunc = target->func;

	TestToolImpl tool;

	if( 0 != ( tool.*targefunc ) ( opt_map ) ) showUsage( argv[0] );

	return 0;
}
