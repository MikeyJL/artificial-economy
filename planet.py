import pygame
import csv
from transporter import Transporter
from utils import read_and_return_csv, overwrite_csv

class Planet:
  def __init__ (self, game_screen, parent_system, parent_id, planet_id, x_loc, y_loc, exports, imports):
    self.game_screen = game_screen
    self.parent_system = parent_system
    self.parent_id = parent_id
    self.planet_id = '%s-%s' % (parent_id, planet_id)
    self.x_loc = x_loc
    self.y_loc = y_loc
    self.exports = exports
    self.imports = imports
    self.orders = []
    self.order_sprites = pygame.sprite.Group()

  # This function inits the csv exports and imports data
  def save_init_state (self):
    with open('data/exports.csv', 'a+', newline='') as file:
      writer = csv.writer(file)
      for export_res in self.exports:
        writer.writerow([
          self.parent_id,
          self.planet_id,
          export_res,
          self.exports[export_res]['amount'],
          self.exports[export_res]['unit_price']
        ])
    with open('data/imports.csv', 'a+', newline='') as file:
      writer = csv.writer(file)
      for import_res in self.imports:
        writer.writerow([
          self.parent_id,
          self.planet_id,
          import_res,
          self.imports[import_res]['inventory']
        ])

	# This function updates the system exports in csv with the latest data
  def update_planet_exports (self):

		# Reads the csv and loads into updater array
    update_data = read_and_return_csv('exports')

    # Updates the data with latest from self.exports
    for row in update_data:
      for export_res in self.exports:
        if self.parent_id == row[0]and self.planet_id == row[1] and export_res == row[2]:
            row[3] = self.exports[export_res]['amount']
            row[4] = self.exports[export_res]['unit_price']

    # Overwrites csv with latest data
    overwrite_csv('exports', update_data)
	
	# This function updates the system imports in csv with the latest data
  def update_planet_imports (self):

    # Reads the csv and loads into updater array
    update_data = read_and_return_csv('imports')

    # Updates the data with latest from self.imports
    for row in update_data:
      for import_res in self.imports:
        if self.parent_id == row[0] and self.planet_id == row[1] and import_res == row[2]:
            row[3] = self.imports[import_res]['inventory']

    # Overwrites csv with latest data
    overwrite_csv('imports', update_data)

  # Creates a new open position and records it in the csv trade_ledger (historical)
  def place_order (self, time, trade_res, color, system_seller):
    with open('data/trade_ledger.csv', 'a+', newline='') as file:
      writer = csv.writer(file)
      writer.writerow([
        self.parent_id,
        self.planet_id,
        system_seller.parent_id,
        system_seller.planet_id,
        (system_seller.x_loc, system_seller.y_loc),
        trade_res,
        system_seller.exports[trade_res]['unit_price'],
        1,
        time,
        '-',
        'open'
      ])
    NEW_ORDER = Transporter(self.game_screen,
                            system_seller.parent_id,
                            system_seller.planet_id,
                            (system_seller.x_loc, system_seller.y_loc),
                            self.parent_id,
                            (self.x_loc, self.y_loc),
                            self.parent_system,
                            color)
    self.orders.append(NEW_ORDER)
    self.order_sprites.add(NEW_ORDER)