			if not self_server_manager_dead:
				self_server_manager.join(1)
				if hasattr(self_server_manager, 'is_alive'):
					self_server_manager_dead = not self_server_manager.is_alive()
				else:
					self_server_manager_dead = self_server_manager.dead

