import pygame
import csv
import math
import random
from transporter import Transporter
from utils import read_and_return_csv, overwrite_csv, EXPORTS_HEADER, IMPORTS_HEADER

class System (pygame.sprite.Sprite):
	def __init__ (self, game_screen, system_id, exports, imports, galaxy_size, other_systems):
		self.game_screen = game_screen
		self.system_id = system_id
		self.exports = exports
		self.imports = imports
		self.galaxy_size = galaxy_size
		self.star_size = random.randint(3, 5)
		self.orders = []
		self.order_sprites = pygame.sprite.Group()

		MIN_DISTANCE = 10

		# Generates seller_location with constraints to prevent systems being too close
		if len(other_systems) == 0:
			self.x_loc = galaxy_size / 2
			self.y_loc = galaxy_size / 2
		else:
			closest_system_distance = 0
			while closest_system_distance < MIN_DISTANCE:
				'''
				This code is for negative and positive sizes
				x_pos = random.randint(-self.galaxy_size, self.galaxy_size)
				y_pos = random.randint(-self.galaxy_size, self.galaxy_size)
				'''
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
		
		# Appends system data to systems.csv
		with open('data/systems.csv', 'a+', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([
				self.system_id,
				self.x_loc,
				self.y_loc,
				self.star_size
			])

	# This function inits the csv exports and imports data
	def save_init_state (self):
		with open('data/exports.csv', 'a+', newline='') as file:
			writer = csv.writer(file)
			for export_res in self.exports:
				writer.writerow([
					self.system_id,
					export_res,
					self.exports[export_res]['amount'],
					self.exports[export_res]['unit_price']
				])
		with open('data/imports.csv', 'a+', newline='') as file:
			writer = csv.writer(file)
			for import_res in self.imports:
				writer.writerow([
					self.system_id,
					import_res,
					self.imports[import_res]['inventory']
				])

	# This function updates the system exports in csv with the latest data
	def update_system_exports (self):

		# Reads the csv and loads into updater array
		update_data = read_and_return_csv('exports')

		# Updates the data with latest from self.exports
		for row in update_data:
			for export_res in self.exports:
				if int(row[0]) == self.system_id:
					if row[1] == export_res:
						row[2] = self.exports[export_res]['amount']
						row[3] = self.exports[export_res]['unit_price']

		# Overwrites csv with latest data
		overwrite_csv('exports', EXPORTS_HEADER, update_data)
	
	# This function updates the system imports in csv with the latest data
	def update_system_imports (self):
		
		# Reads the csv and loads into updater array
		update_data = read_and_return_csv('imports')
		
		# Updates the data with latest from self.imports
		for row in update_data:
			for import_res in self.imports:
				if int(row[0]) == self.system_id:
					if row[1] == import_res:
						row[2] = self.imports[import_res]['inventory']
		
		# Overwrites csv with latest data
		overwrite_csv('imports', IMPORTS_HEADER, update_data)

	# Creates a new open position and records it in the csv trade_ledger (historical)
	def place_order (self, time, trade_res, system_seller):
		with open('data/trade_ledger.csv', 'a+', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([
				self.system_id,
				system_seller.system_id,
				(system_seller.x_loc, system_seller.y_loc),
				trade_res,
				system_seller.exports[trade_res]['unit_price'],
				1,
				time,
				'-',
				'open'
			])
		NEW_ORDER = Transporter(self.game_screen,
														system_seller.system_id,
														(system_seller.x_loc, system_seller.y_loc),
														self.system_id,
														(self.x_loc, self.y_loc),
														self)
		self.orders.append(NEW_ORDER)
		self.order_sprites.add(NEW_ORDER)