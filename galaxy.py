import csv
import pygame
import random
from system import System
from planet import Planet
from utils import init_csv, read_and_return_csv, overwrite_csv, GALAXY_HEADER, SYSTEMS_HEADER, EXPORTS_HEADER, IMPORTS_HEADER, TRADE_LEDGER_HEADER

class Galaxy:
	def __init__(self, game_screen, galaxy_size, system_count, allocation, resource_deviation, resource_variation, price_modifier):
		self.game_screen = game_screen
		self.system_count = system_count
		self.resource_deviation = resource_deviation
		self.resource_variation = resource_variation
		self.price_modifier = price_modifier
		self.allocation = allocation
		self.systems = []
		self.system_sprites = pygame.sprite.Group()
		self.resources = []
		self.trade_ledger = []

		# Inits data store
		init_csv('galaxy',
						 True,
						 [self.resource_deviation, self.resource_variation, self.price_modifier, self.allocation])
		init_csv('systems', False, None)
		init_csv('planets', False, None)
		init_csv('trade_ledger', False, None)
		init_csv('exports', False, None)
		init_csv('imports', False, None)

		# Adds resources to its own array
		for res in allocation:
			self.resources.append(res)

		# Generates star systems
		for system_id in range(self.system_count):
			
			# Generates the system obj
			NEW_SYSTEM = System(game_screen, system_id, galaxy_size, self.systems)
			with open('data/systems.csv', 'a+', newline='') as file:
				writer = csv.writer(file)
				writer.writerow([
					NEW_SYSTEM.system_id,
					NEW_SYSTEM.x_loc,
					NEW_SYSTEM.y_loc,
					NEW_SYSTEM.star_size
				])

			# Generates planets
			for planet_id in range(random.randint(2, 4)):
				naming_convention = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

				# Builds the resources
				exports_builder = {}
				imports_builder = {}
				while len(exports_builder) < random.randint(1, self.resource_variation) and self.resource_variation < len(self.allocation):
					ALLOCATED_RES = random.choice(self.resources)
					if ALLOCATED_RES not in exports_builder:
						exports_builder[ALLOCATED_RES] = {
							'amount': 0
						}
						self.allocation[ALLOCATED_RES]['instances'] += 1
				for res in self.resources:
					if res not in exports_builder:
						imports_builder[res] = {
							'inventory': 0
						}
				
				# Inits the planet
				NEW_PLANET = Planet(game_screen, NEW_SYSTEM, NEW_SYSTEM.system_id, naming_convention[planet_id], NEW_SYSTEM.x_loc, NEW_SYSTEM.y_loc, exports_builder, imports_builder)
				NEW_SYSTEM.planets.append(NEW_PLANET)
				with open('data/planets.csv', 'a+', newline='') as file:
					writer = csv.writer(file)
					writer.writerow([
						NEW_PLANET.parent_id,
						NEW_PLANET.planet_id
					])

			self.systems.append(NEW_SYSTEM)
			self.system_sprites.add(NEW_SYSTEM)

		# Fills each planet's resources and adds to total
		for system in self.systems:
			for planet in system.planets:
				for planet_res in planet.exports:
					SELECTED_RES = self.allocation[planet_res]
					LOWER_VAL = round((SELECTED_RES['init_amount'] / SELECTED_RES['instances']) * (1 - self.resource_deviation))
					UPPER_VAL = round((SELECTED_RES['init_amount'] / SELECTED_RES['instances']) * (1 + self.resource_deviation))
					planet.exports[planet_res]['amount'] = random.randint(LOWER_VAL, UPPER_VAL)
					SELECTED_RES['total_amount'] += planet.exports[planet_res]['amount']

		self.calculate_global_total_value()
		self.calculate_global_avg_resource_units()
		self.calculate_local_system_price(0)
		
	def step (self, time):		

		# Move transporters
		for system_buyer in self.systems:
			self.game_screen.blit(system_buyer.image, system_buyer.rect)
		
			for planet_buyer in system_buyer.planets:
				# Can only have less than 5 orders
				if len(planet_buyer.orders) < 5:

					# Then places on order and recorded on the global trade ledger
					for trade_res in planet_buyer.imports:
						
						PLANETS_WITH_RES = []
						
						# Lists all the systems selling the required resource
						for scan_system in self.systems:
							for scan_planet in scan_system.planets:
								if trade_res in scan_planet.exports:
									PLANETS_WITH_RES.append(scan_planet)
						
						# Finds the best price for a resource that a system needs
						BEST_PRICE = 0
						for planet_seller in PLANETS_WITH_RES:
							if BEST_PRICE == 0:
								BEST_PRICE = planet_seller
							elif planet_seller.exports[trade_res]['unit_price'] < BEST_PRICE.exports[trade_res]['unit_price']:
								BEST_PRICE = planet_seller
						planet_buyer.place_order(time, trade_res, self.allocation[trade_res]['color'], BEST_PRICE)

						# Removes amount from the selling system
						for system in self.systems:
							for planet in system.planets:
								if system.system_id == BEST_PRICE.parent_id and planet.planet_id == BEST_PRICE.planet_id:
									for export_res in planet.exports:
										if export_res == trade_res:
											planet.exports[export_res]['amount'] -= 1
											planet.update_planet_exports()

				for planet_buyer in system_buyer.planets:
					for order in planet_buyer.orders:
						if order.move():
							# Gets all data from global trade ledger
							update_data = read_and_return_csv('trade_ledger')

							# Updates the ledger if resource has been delivered
							for row in update_data:
								if row[10] == 'open' and planet_buyer.parent_id == row[0] and planet_buyer.planet_id == row[1] and order.origin_system_id == row[2] and order.origin_planet_id == row[3]:
									row[9] = time
									row[10] = 'resolved'
									for target_system in self.systems:
										for target_planet in target_system.planets:
											if target_system.system_id == row[0] and target_planet.planet_id == row[1]:
												for imported_res in target_planet.imports:
													if imported_res == row[5]:
														target_planet.imports[imported_res]['inventory'] += 1
														target_planet.update_planet_imports()

							# Overwrites the ledger with new data
							overwrite_csv('trade_ledger', update_data)
							order.kill()
							planet_buyer.orders.remove(order)

							# Updates economy
							self.calculate_global_total_value()
							self.calculate_global_avg_resource_units()
							self.calculate_local_system_price(time)

	# Creates the total value of the economy and generates an average unit price for each resource based on scarcity
	def calculate_global_total_value (self):
		total_amount = 0
		total_amount_all = 0
		for res in self.allocation:
			total_amount_all += self.allocation[res]['total_amount']
		for res in self.allocation:
			global_unit_price = round(total_amount_all / self.allocation[res]['total_amount'] * self.price_modifier, 2)
			self.allocation[res]['global_unit_price'] = global_unit_price
			total_amount += global_unit_price * self.allocation[res]['total_amount']
		self.total_value = round(total_amount, 2)

	# Calculates the global average resource units
	def calculate_global_avg_resource_units (self):
		for res in self.resources:
			res_unit_count = 0
			for system in self.systems:
				for planet in system.planets:
					for export_res in planet.exports:
						if res == export_res:
							res_unit_count += planet.exports[export_res]['amount']
					for import_res in planet.imports:
						if res == import_res:
							res_unit_count += planet.imports[import_res]['inventory']
			self.allocation[res]['avg_res_unit'] = round(res_unit_count / self.allocation[res]['instances'])
	
	# Creates a system/local price based off the global total resource and local scarcity
	def calculate_local_system_price (self, time):
		for system in self.systems:
			for planet in system.planets:
				for export_res in planet.exports:
					ADJUSTED_PRICE_INDEX = self.allocation[export_res]['avg_res_unit'] / planet.exports[export_res]['amount']
					planet.exports[export_res]['unit_price'] = round(ADJUSTED_PRICE_INDEX * self.allocation[export_res]['global_unit_price'], 2)
				if time == 1:
					planet.save_init_state()