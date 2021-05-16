import pygame
import random
from galaxy import Galaxy
import time as t

RES_ALLOCATION = {
	'iron': {
		'init_amount': random.randint(4000, 8000),
		'instances': 0,
		'total_amount': 0
	},
	'zinc': {
		'init_amount': random.randint(5000, 8000),
		'instances': 0,
		'total_amount': 0
	},
	'uranium': {
		'init_amount': random.randint(500, 600),
		'instances': 0,
		'total_amount': 0
	}
}

# Plots systems on a scatter for visuals
pygame.init()
FPS = 40
clock = pygame.time.Clock()
screen = pygame.display.set_mode([500, 500])
screen.fill((255, 255, 255))
galaxy = Galaxy(game_screen = screen,
								galaxy_size = 500,
								system_count = 15,
								allocation = RES_ALLOCATION,
								resource_deviation = .1,
								resource_variation = 2,
								price_modifier = 10)
running = True
time = 0
while running:
	screen.fill((255, 255, 255))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	galaxy.step(time)
	pygame.display.flip()
	time += 1
	clock.tick(FPS)
pygame.quit()
