import pygame
import random
from system import System
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
						 GALAXY_HEADER,
						 True,
						 [self.resource_deviation, self.resource_variation, self.price_modifier, self.allocation])
		init_csv('systems', SYSTEMS_HEADER, False, None)
		init_csv('trade_ledger', TRADE_LEDGER_HEADER, False, None)
		init_csv('exports', EXPORTS_HEADER, False, None)
		init_csv('imports', IMPORTS_HEADER, False, None)

		# Adds resources to its own array
		for res in allocation:
			self.resources.append(res)

		# Generates star systems
		for system_id in range(self.system_count):
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
			NEW_SYSTEM = System(game_screen, system_id, exports_builder, imports_builder, galaxy_size, self.systems)
			self.systems.append(NEW_SYSTEM)
			self.system_sprites.add(NEW_SYSTEM)

		# Fills each system's resources
		for system in self.systems:
			for system_res in system.exports:
				SELECTED_RES = self.allocation[system_res]
				LOWER_VAL = round((SELECTED_RES['init_amount'] / SELECTED_RES['instances']) * (1 - self.resource_deviation))
				UPPER_VAL = round((SELECTED_RES['init_amount'] / SELECTED_RES['instances']) * (1 + self.resource_deviation))
				system.exports[system_res]['amount'] = random.randint(LOWER_VAL, UPPER_VAL)

		# Removes init_amount and adds all units of resources in the economy
		for system in self.systems:
			for system_res in system.exports:
				SELECTED_RES = self.allocation[system_res]
				SELECTED_RES['total_amount'] += system.exports[system_res]['amount']
				if 'init_amount' in SELECTED_RES:
					SELECTED_RES.pop('init_amount')

		self.calculate_global_total_value()
		self.calculate_global_avg_resource_units()
		self.calculate_local_system_price(0)
		
	def step (self, time):		

		# Move transporters
		for system_buyer in self.systems:
			self.game_screen.blit(system_buyer.image, system_buyer.rect)

			if len(system_buyer.orders) < 5:

				# Then places on order and recorded on the global trade ledger
				for trade_res in system_buyer.imports:

					# Lists all the systems selling the required resource
					SYSTEMS_WITH_RES = [system for system in self.systems if trade_res in system.exports]
					
					# Finds the best price for a resource that a system needs
					BEST_PRICE = 0
					for system_seller in SYSTEMS_WITH_RES:
						if BEST_PRICE == 0:
							BEST_PRICE = system_seller
						elif system_seller.exports[trade_res]['unit_price'] < BEST_PRICE.exports[trade_res]['unit_price']:
							BEST_PRICE = system_seller
					system_buyer.place_order(time, trade_res, self.allocation[trade_res]['color'], BEST_PRICE)

					# Removes amount from the selling system
					for system in self.systems:
						if system.system_id == BEST_PRICE.system_id:
							for export_res in system.exports:
								if export_res == trade_res:
									system.exports[export_res]['amount'] -= 1
									system.update_system_exports()
			else:
				for order in system_buyer.orders:
					if order.move():
						# Gets all data from global trade ledger
						update_data = read_and_return_csv('trade_ledger')

						# Updates the ledger if resource has been delivered
						for row in update_data:
							if row[8] == 'open' and system_buyer.system_id == int(row[0]) and order.origin_system_id == int(row[1]):
								row[7] = time
								row[8] = 'resolved'
								for target_system in self.systems:
									if target_system.system_id == int(row[0]):
										for imported_res in target_system.imports:
											if imported_res == row[3]:
												target_system.imports[imported_res]['inventory'] += 1
												target_system.update_system_imports()

						# Overwrites the ledger with new data
						overwrite_csv('trade_ledger', TRADE_LEDGER_HEADER, update_data)
						order.kill()
						system_buyer.orders.remove(order)

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
				for export_res in system.exports:
					if res == export_res:
						res_unit_count += system.exports[export_res]['amount']
				for import_res in system.imports:
					if res == import_res:
						res_unit_count += system.imports[import_res]['inventory']
			self.allocation[res]['avg_res_unit'] = round(res_unit_count / self.allocation[res]['instances'])
	
	# Creates a system/local price based off the global total resource and local scarcity
	def calculate_local_system_price (self, time):
		for system in self.systems:
			for system_res in system.exports:
				ADJUSTED_PRICE_INDEX = self.allocation[system_res]['avg_res_unit'] / system.exports[system_res]['amount']
				system.exports[system_res]['unit_price'] = round(ADJUSTED_PRICE_INDEX * self.allocation[system_res]['global_unit_price'], 2)
			if time == 0:
				system.save_init_state()