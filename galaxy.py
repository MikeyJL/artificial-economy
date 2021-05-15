import csv
from os import write
import shutil
import random
import matplotlib.pyplot as plt
import numpy as np
from system import System
from tempfile import NamedTemporaryFile

class Galaxy:
	def __init__(self, galaxy_radius, system_count, allocation, resource_deviation, resource_variation, price_modifier):
		self.system_count = system_count
		self.resource_deviation = resource_deviation
		self.resource_variation = resource_variation
		self.price_modifier = price_modifier
		self.allocation = allocation
		self.systems = []
		self.resources = []
		self.trades = []

		# Inits data store
		with open('data/galaxy.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([
				'resource_deviation',
				'resource_variation',
				'price_modifier',
				'allocation'
			])
			writer.writerow([
				self.resource_deviation,
				self.resource_variation,
				self.price_modifier,
				self.allocation
			])
		with open('data/systems.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([
				'system_id',
				'x_loc',
				'y_loc',
				'exports',
				'imports'
			])
		with open('data/trade_ledger.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([
				'system_id',
				'seller_system_id',
				'resource',
				'price',
				'amount',
				'delivery',
				'time_issued',
				'status'
			])

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

		x = [system.x_loc for system in self.systems]
		y = [system.y_loc for system in self.systems]
		plt.scatter(np.array(x), np.array(y), s = np.random.randint(1, 3, len(x)))
		plt.show()

	def load_galaxy ():
		return
		
	def step (self, time):
		self.check_orders(time)
		self.order_resources(time)

	def order_resources (self, time):
		for system_buyer in self.systems:
			for trade_res in system_buyer.imports:
				SYSTEMS_WITH_RES = [{
					'seller_system_id': system.system_id,
					'resource': trade_res,
					'price': system.exports[trade_res]['unit_price']
				} for system in self.systems if trade_res in system.exports]
				BEST_PRICE = 0
				for system_seller in SYSTEMS_WITH_RES:
					if BEST_PRICE == 0:
						BEST_PRICE = system_seller
					elif system_seller['price'] < BEST_PRICE['price']:
						BEST_PRICE = system_seller
				system_buyer.place_order(time, system_seller)

	def check_orders (self, time):
		update_data = []
		with open('data/trade_ledger.csv', 'r', newline='') as file:
			reader = csv.reader(file)
			for row in reader:
				update_data.append(row)
		for row in update_data:
			if row[0] != 'system_id':
				if int(row[5]) == time and row[7] == 'open':
					row[7] = 'resolved'
		with open('data/trade_ledger.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			for row in update_data:
				writer.writerow(row)
