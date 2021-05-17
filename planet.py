import pygame
from transporter import Transporter

class Planet:
  def __init__ (self, game_screen, active_trades, parent_system, parent_id, planet_id, x_loc, y_loc, exports, imports):
    self.game_screen = game_screen
    self.active_trades = active_trades
    self.parent_system = parent_system
    self.parent_id = parent_id
    self.planet_id = '%s-%s' % (parent_id, planet_id)
    self.x_loc = x_loc
    self.y_loc = y_loc
    self.exports = exports
    self.imports = imports
    self.orders = []
    self.order_sprites = pygame.sprite.Group()

  # Creates a new open position and records it in the active_trades (historical)
  def place_order (self, trade_res, color, system_seller):
    self.active_trades.append({
      'buyer_system_id': self.parent_id,
      'buyer_planet_id': self.planet_id,
      'seller_system_id': system_seller.parent_id,
      'seller_planet_id': system_seller.planet_id,
      'seller_location': (system_seller.x_loc, system_seller.y_loc),
      'resource': trade_res,
      'unit_price': system_seller.exports[trade_res]['unit_price'],
      'amount': 1
    })
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