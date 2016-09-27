			if rpc_server_manager_dead:
				rpc_server_manager = self.create_rpc_server_manager()
				rpc_server_manager.start()
				rpc_server_manager_dead = False

