import csv
import math
import random

class System:
	def __init__ (self, system_id, exports, imports, galaxy_radius, other_systems):
		self.system_id = system_id
		self.exports = exports
		self.imports = imports
		self.galaxy_radius = galaxy_radius

		MIN_DISTANCE = 10

		# Generates location with constraint
		if len(other_systems) == 0:
			self.x_loc = 0
			self.y_loc = 0
		else:
			closest_system_distance = 0
			while closest_system_distance < MIN_DISTANCE:
				x_pos = random.randint(-self.galaxy_radius, self.galaxy_radius)
				y_pos = random.randint(-self.galaxy_radius, self.galaxy_radius)
				other_systems_x = [other_system.x_loc for other_system in other_systems]
				other_systems_y = [other_system.y_loc for other_system in other_systems]
				closest_system_x = min(other_systems_x, key = lambda x:abs(x - x_pos))
				closest_system_y = min(other_systems_y, key = lambda y:abs(y - y_pos))
				closest_system_distance = math.sqrt((closest_system_x - x_pos) ** 2 + (closest_system_y - y_pos) ** 2)
			self.x_loc = x_pos
			self.y_loc = y_pos

	def save_init_state (self):
		with open('data/systems.csv', 'a+', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([
				self.system_id,
				self.x_loc,
				self.y_loc,
				self.exports,
				self.imports
			])

	def place_order (self, time, system_seller):
		with open('data/trade_ledger.csv', 'a+', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([
				self.system_id,
				system_seller['seller_system_id'],
				system_seller['resource'],
				system_seller['price'],
				1,
				random.randint(1, 5),
				time,
				'open'
			])