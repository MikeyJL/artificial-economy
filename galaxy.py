import random
import matplotlib.pyplot as plt
import numpy as np
from system import System
from utils import init_csv, read_and_return_csv, overwrite_csv

# CSV headers
GALAXY_HEADER = ['resource_deviation', 'resource_variation', 'price_modifier', 'allocation']
SYSTEMS_HEADER = ['system_id', 'x_loc', 'y_loc']
TRADE_LEDGER_HEADER = ['system_id', 'seller_system_id', 'resource', 'price', 'amount', 'issued', 'delivery', 'status']
EXPORTS_HEADER = ['system_id', 'resource', 'amount', 'unit_price']
IMPORTS_HEADER = ['system_id', 'resource', 'inventory']

class Galaxy:
	def __init__(self, galaxy_radius, system_count, allocation, resource_deviation, resource_variation, price_modifier):
		self.system_count = system_count
		self.resource_deviation = resource_deviation
		self.resource_variation = resource_variation
		self.price_modifier = price_modifier
		self.allocation = allocation
		self.systems = []
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
			self.systems.append(System(system_id, exports_builder, imports_builder, galaxy_radius, self.systems))

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

		# Creates the total value of the economy and generates an average unit price for each resource based on scarcity
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
		for res in self.resources:
			res_unit_count = 0
			for system in self.systems:
				for system_res in system.exports:
					if res == system_res:
						res_unit_count += system.exports[system_res]['amount']
			self.allocation[res]['avg_res_unit'] = round(res_unit_count / self.allocation[res]['instances'])
		
		# Creates a system/local price based off the global total resource and local scarcity
		for system in self.systems:
			for system_res in system.exports:
				ADJUSTED_PRICE_INDEX = self.allocation[system_res]['avg_res_unit'] / system.exports[system_res]['amount']
				system.exports[system_res]['unit_price'] = round(ADJUSTED_PRICE_INDEX * self.allocation[system_res]['global_unit_price'], 2)
			system.save_init_state()

		# Plots systems on a scatter for visuals
		x = [system.x_loc for system in self.systems]
		y = [system.y_loc for system in self.systems]
		plt.scatter(np.array(x), np.array(y), s = np.random.randint(1, 3, len(x)))
		plt.show()
		
	def step (self, time):
		
		# Checks the global trade ledger for deliveries arriving at current time
		self.check_orders(time)

		# Opens new orders for required resources for each system
		self.order_resources(time)


	def order_resources (self, time):

		# Then places on order and recorded on the global trade ledger
		for system_buyer in self.systems:
			for trade_res in system_buyer.imports:

				# Lists all the systems selling the required resource
				SYSTEMS_WITH_RES = [{
					'seller_system_id': system.system_id,
					'resource': trade_res,
					'price': system.exports[trade_res]['unit_price']
				} for system in self.systems if trade_res in system.exports]
				
				# Finds the best price for a resource that a system needs
				BEST_PRICE = 0
				for system_seller in SYSTEMS_WITH_RES:
					if BEST_PRICE == 0:
						BEST_PRICE = system_seller
					elif system_seller['price'] < BEST_PRICE['price']:
						BEST_PRICE = system_seller
				system_buyer.place_order(time, BEST_PRICE)

			# Removes amount from the selling system
			for system in self.systems:
				if system.system_id == BEST_PRICE['seller_system_id']:
					for export_res in system.exports:
						if export_res == BEST_PRICE['resource']:
							system.exports[export_res]['amount'] -= 1
							system.update_system_exports()

	def check_orders (self, time):

		# Gets all data from global trade ledger
		update_data = read_and_return_csv('trade_ledger')

		# Updates the ledger if resource has been delivered
		for row in update_data:
			if int(row[6]) == time and row[7] == 'open':
				row[7] = 'resolved'
				for system in self.systems:
					if system.system_id == int(row[0]):
						for imported_res in system.imports:
							if imported_res == row[2]:
								system.imports[imported_res]['inventory'] += 1
								system.update_system_imports()

		# Overwrites the ledger with new data
		overwrite_csv('trade_ledger', TRADE_LEDGER_HEADER, update_data)