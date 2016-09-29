###### compiler and linker #####
CC = gcc
AR = ar cru
LINKER = $(CC)
RM = /bin/rm -f

##### path define #####
MSGPACK_INC_PATH = /usr/local/include
MSGPACK_LIB_PATH = /usr/local/lib
MSGPACKRPC_INC_PATH = /usr/local/include
MSGPACKRPC_LIB_PATH = /usr/local/lib
MPIO_LIB_PATH = /usr/local/lib

##### cflags and ldflags #####
CFLAGS = -std=c++03 -DMSGPACK_USE_CPP03 -Wall -D_REENTRANT -D_GNU_SOURCE -fPIC -g2 -I$(MSGPACK_INC_PATH) -I$(MSGPACKRPC_INC_PATH)
STATICFLAGS = -Wl,-static
STATICLIBS = -L$(MSGPACKRPC_LIB_PATH) -ljubatus_msgpack-rpc -L$(MSGPACK_LIB_PATH) -lmsgpack -L$(MPIO_LIB_PATH) -ljubatus_mpio
DYNAMICFLAGS = -Wl,-call_shared
DYNAMICLIBS = -lstdc++ -lpthread -lm

##### make rules #####
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
%.o: %.cc
	$(CC) $(CFLAGS) -c $< -o $@
%.o: %.cpp
	$(CC) $(CFLAGS) -c $< -o $@

##### objs for compiling #####
COM_OBJS = log_utils.o file_utils.o config.o opt_map.o
CLI_OBJS = $(COM_OBJS) echo_rpc_cli.o
SVR_OBJS = $(COM_OBJS) echo_rpc_handler.o echo_svr.o

##### target for compiling #####
TARGETS = libecho_rpc_cli.a echo_rpc_test echo_svr

##### make targets #####
all: $(TARGETS)

libecho_rpc_cli.a: $(CLI_OBJS)
	$(AR) $@ $^

echo_rpc_test: echo_rpc_test.o libecho_rpc_cli.a
	$(LINKER) $^ $(STATICFLAGS) -L. -lecho_rpc_cli $(STATICLIBS) $(DYNAMICFLAGS) $(DYNAMICLIBS) -o $@

echo_svr: $(SVR_OBJS)
	$(LINKER) $^ $(STATICFLAGS) $(STATICLIBS) $(DYNAMICFLAGS) $(DYNAMICLIBS) -o $@

clean:
	@($(RM) $(TARGETS))
	@($(RM) *.o)

