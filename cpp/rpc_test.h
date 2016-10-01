#pragma once

#include "opt_map.h"

namespace ${app} {

	class TestTool {
		public:
			TestTool();
			virtual ~TestTool();

		public:
${api}
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
${arg}
					{ NULL, NULL }
				};

				return name2func;
			};
	};


	class TestToolImpl : public TestTool {
		public:
			TestToolImpl();
			virtual ~TestToolImpl();

		public:
${api}
	};

}
