import pygame
import random
from galaxy import Galaxy

RES_ALLOCATION = {
	'iron': {
		'color': (237, 146, 0),
		'init_amount': random.randint(4000, 8000),
		'instances': 0,
		'total_amount': 0
	},
	'zinc': {
		'color': (0, 119, 237),
		'init_amount': random.randint(5000, 8000),
		'instances': 0,
		'total_amount': 0
	},
	'potassium': {
		'color': (0, 168, 17),
		'init_amount': random.randint(5000, 8000),
		'instances': 0,
		'total_amount': 0
	},
	'aluminium': {
		'color': (201, 201, 201),
		'init_amount': random.randint(12000, 15000),
		'instances': 0,
		'total_amount': 0
	},
	'copper': {
		'color': (255, 148, 0),
		'init_amount': random.randint(10000, 11000),
		'instances': 0,
		'total_amount': 0
	},
	'helium': {
		'color': (212, 166, 255),
		'init_amount': random.randint(9000, 11000),
		'instances': 0,
		'total_amount': 0
	},
	'hydrogen': {
		'color': (255, 200, 166),
		'init_amount': random.randint(10000, 15000),
		'instances': 0,
		'total_amount': 0
	},
	'uranium': {
		'color': (35, 217, 89),
		'init_amount': random.randint(500, 600),
		'instances': 0,
		'total_amount': 0
	}
}

# Plots systems on a scatter for visuals
pygame.init()
FPS = 24
GALAXY_SIZE = 800
clock = pygame.time.Clock()
screen = pygame.display.set_mode([GALAXY_SIZE, GALAXY_SIZE])
galaxy = Galaxy(game_screen = screen,
								galaxy_size = GALAXY_SIZE,
								system_count = 10,
								allocation = RES_ALLOCATION,
								resource_deviation = .1,
								resource_variation = 5,
								price_modifier = 10)
running = True
while running:
	screen.fill((255, 255, 255))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	galaxy.step()
	pygame.display.flip()
	clock.tick(FPS)
pygame.quit()
