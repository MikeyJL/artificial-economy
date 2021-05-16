import pygame

class Transporter (pygame.sprite.Sprite):
  def __init__ (self, game_screen, origin_system_id, current_x_y, target_system_id, target_x_y, target_system, color):
    self.game_screen = game_screen
    self.origin_system_id = origin_system_id
    self.target_system_id = target_system_id
    self.target_x_y = target_x_y
    self.target_system = target_system

    # pygame init
    super(Transporter, self).__init__()
    self.image = pygame.Surface((3, 3))
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.rect.center = current_x_y
  
  def move (self):
    current_x, current_y = self.rect.center
    target_x, target_y = self.target_x_y

    if current_x < target_x:
      self.rect.move_ip(1, 0)
    elif current_x > target_x:
      self.rect.move_ip(-1, 0)

    if current_y < target_y:
      self.rect.move_ip(0, 1)
    elif current_y > target_y:
      self.rect.move_ip(0, -1)
    
    self.game_screen.blit(self.image, (current_x, current_y))

    return pygame.sprite.collide_rect(self, self.target_system)