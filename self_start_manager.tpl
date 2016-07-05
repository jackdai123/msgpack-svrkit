			if self_server_manager_dead:
				self_server_manager = self.create_self_server_manager()
				self_server_manager.start()
				self_server_manager_dead = False

