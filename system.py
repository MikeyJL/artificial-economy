import pygame
import math
import random

class System (pygame.sprite.Sprite):
	def __init__ (self, game_screen, system_id, galaxy_size, other_systems):
		self.game_screen = game_screen
		self.system_id = str(system_id)
		self.planets = []
		self.galaxy_size = galaxy_size
		self.star_size = random.randint(3, 5)

		MIN_DISTANCE = 10

		# Generates location with constraints to prevent systems being too close
		if len(other_systems) == 0:
			self.x_loc = galaxy_size / 2
			self.y_loc = galaxy_size / 2
		else:
			closest_system_distance = 0
			while closest_system_distance < MIN_DISTANCE:
				x_pos = random.randint(0, self.galaxy_size)
				y_pos = random.randint(0, self.galaxy_size)
				other_systems_x = [other_system.x_loc for other_system in other_systems]
				other_systems_y = [other_system.y_loc for other_system in other_systems]
				closest_system_x = min(other_systems_x, key = lambda x:abs(x - x_pos))
				closest_system_y = min(other_systems_y, key = lambda y:abs(y - y_pos))
				closest_system_distance = math.sqrt((closest_system_x - x_pos) ** 2 + (closest_system_y - y_pos) ** 2)
			self.x_loc = x_pos
			self.y_loc = y_pos
		
		# pygame init
		super(System, self).__init__()
		self.image = pygame.Surface((self.star_size, self.star_size))
		self.image.fill((40, 40, 40))
		self.rect = self.image.get_rect()
		self.rect.center = (self.x_loc, self.y_loc)