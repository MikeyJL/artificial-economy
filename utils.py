import csv

# CSV headers
GALAXY_HEADER = ['resource_deviation', 'resource_variation', 'price_modifier', 'allocation']
SYSTEMS_HEADER = ['system_id', 'star_size', 'x_loc', 'y_loc']
TRADE_LEDGER_HEADER = ['system_id', 'seller_system_id', 'seller_location', 'resource', 'price', 'amount', 'issued', 'delivery', 'status']
EXPORTS_HEADER = ['system_id', 'resource', 'amount', 'unit_price']
IMPORTS_HEADER = ['system_id', 'resource', 'inventory']

def init_csv (file_name, has_data, data):
	with open('data/%s.csv' % file_name, 'w', newline='') as file:
		writer = csv.writer(file)
		if has_data:
			writer.writerow(data)

def read_and_return_csv (file_name):
	return_data = []
	with open('data/%s.csv' % file_name, 'r', newline='') as file:
			reader = csv.reader(file)
			for row in reader:
				return_data.append(row)
	return return_data

def overwrite_csv (file_name, update_data):
	with open('data/%s.csv' % file_name, 'w', newline='') as file:
			writer = csv.writer(file)
			for row in update_data:
				writer.writerow(row)
