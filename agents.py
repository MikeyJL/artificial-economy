import random

class Economy:
	def __init__(self, system_count, allocation, resource_deviation, price_modifier):
		self.system_count = system_count
		self.resource_deviation = resource_deviation
		self.price_modifier = price_modifier
		self.allocation = allocation
		self.systems = []
		self.resources = []

		# Adds resources to its own array
		for res in allocation:
			self.resources.append(res)

		# Generates star systems
		for system_id in range(self.system_count):
			ALLOCATED_RES = random.choice(self.resources)
			self.allocation[ALLOCATED_RES]['instances'] += 1
			self.systems.append({
				'id': system_id,
				'resource': ALLOCATED_RES,
				'amount': 0
			})

		# Fills each system's resources
		for system in self.systems:
			SELECTED_RES = self.allocation[system['resource']]
			LOWER_VAL = round((SELECTED_RES['init_amount'] / SELECTED_RES['instances']) * (1 - self.resource_deviation))
			UPPER_VAL = round((SELECTED_RES['init_amount'] / SELECTED_RES['instances']) * (1 + self.resource_deviation))
			system['amount'] = random.randint(LOWER_VAL, UPPER_VAL)

		# Removes init_amount and adds all units of resources in the economy
		for system in self.systems:
			SELECTED_RES = self.allocation[system['resource']]
			SELECTED_RES['total_amount'] += system['amount']
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
				if res == system['resource']:
					res_unit_count += system['amount']
			self.allocation[res]['avg_res_unit'] = round(res_unit_count / self.allocation[res]['instances'])
		
		# Creates a system/local price based off the global total resource and local scarcity
		for system in self.systems:
			ADJUSTED_PRICE_INDEX = self.allocation[system['resource']]['avg_res_unit'] / system['amount']
			system['unit_price'] = round(ADJUSTED_PRICE_INDEX * self.allocation[system['resource']]['global_unit_price'], 2)

		# Degbugging
		print('\n\n---------- ALLOCATION ----------')
		for res in self.allocation:
			print('\nresource: %s' % res)
			print('instances: %s' % self.allocation[res]['instances'])
			print('total_amount: %s' % self.allocation[res]['total_amount'])
			print('avg_res_unit: %s' % self.allocation[res]['avg_res_unit'])
			print('global_unit_price: %s' % self.allocation[res]['global_unit_price'])
		print ('\ntotal_economy_value:', self.total_value)

		print('\n\n---------- SYSTEMS ----------')
		for system in self.systems:
			print('\nid: %s' % system['id'])
			print('resource: %s' % system['resource'])
			print('amount: %s' % system['amount'])
			print('unit_price: %s' % system['unit_price'])