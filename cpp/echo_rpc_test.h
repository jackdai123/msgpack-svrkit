#pragma once

#include "opt_map.h"

namespace echo {

	class TestTool
	{
		public:
			TestTool();
			virtual ~TestTool();

		public:
			virtual int echo( OptMap & bigmap );

		public:
			typedef int (TestTool::*ToolFunc_t) ( OptMap & );

			typedef struct tagName2Func {
				const char * name;
				TestTool::ToolFunc_t func;
				const char * opt_string;
				const char * usage;
			} Name2Func_t;

			static Name2Func_t * GetName2Func()
			{
				static Name2Func_t name2func [] = {
					{ "echo", &TestTool::echo, "c:f:hs:",
						"-s <string>" },
					{ NULL, NULL }
				};

				return name2func;
			};
	};


	class TestToolImpl : public TestTool
	{
		public:
			TestToolImpl();
			virtual ~TestToolImpl();

		public:
			virtual int echo( OptMap & opt_map );
	};

}
