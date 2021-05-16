import csv

def init_csv (file_name, headers, has_data, data):
	with open('data/%s.csv' % file_name, 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(headers)
		if has_data:
			writer.writerow(data)

def read_and_return_csv (file_name):
	return_data = []
	with open('data/%s.csv' % file_name, 'r', newline='') as file:
			reader = csv.reader(file)
			next(reader, None)
			for row in reader:
				return_data.append(row)
	return return_data

def overwrite_csv (file_name, header, update_data):
	with open('data/%s.csv' % file_name, 'w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(header)
			for row in update_data:
				writer.writerow(row)
