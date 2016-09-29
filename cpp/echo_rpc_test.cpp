#include <stdio.h>
#include "echo_rpc_test.h"
#include "echo_rpc_cli.h"

namespace echo {


	TestTool :: TestTool() {
	}

	TestTool :: ~TestTool() {
	}

	int TestTool :: echo( OptMap & /* opt_map */ ) {
		printf( "\n    *** echo unimplement ***\n" );
		return -1;
	}

	TestToolImpl:: TestToolImpl() {
	}

	TestToolImpl:: ~TestToolImpl() {
	}

	int TestToolImpl :: echo( OptMap & opt_map ) {
		echomsg req;
		echomsg res;

		if( NULL == opt_map.Get( 's' ) ) return -1;

		req.my_string = opt_map.Get( 's' ); 
		req.vec_int.push_back(1);
		req.vec_int.push_back(3);
		req.vec_string.push_back("david");
		req.vec_string.push_back("yuki");

		Client cli;
		int ret = cli.echo( req, &res );
		printf( "%s return %d\n", __func__, ret );
		printf( "res: %s [%d,%d] [%s,%s]\n", res.my_string.c_str(),
				res.vec_int[0], res.vec_int[1],
				res.vec_string[0].c_str(), res.vec_string[1].c_str() );

		return ret;
	}

}

using namespace echo;

void showUsage( const char * program )
{
    printf( "Usage:\n          %s [-c <config>] [-f <func>] [-h]\nExamples:\n", program );

    TestTool::Name2Func_t * name2func = TestTool::GetName2Func();

    for( int i = 0; ; i++ ) {
        TestTool::Name2Func_t * iter = &( name2func[i] );

        if( NULL == iter->name ) break;

        printf( "          %s -c rpc_cli.conf -f %s %s\n", program, iter->name, iter->usage );
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
