			if not rpc_server_manager_dead:
				rpc_server_manager.join(1)
				if not rpc_server_manager.is_alive():
					rpc_server_manager_dead = True

