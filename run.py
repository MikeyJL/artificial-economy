import random
from galaxy import Galaxy

# Constants
FORCE = True
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

MAX_TIME_STEP = 10
galaxy = Galaxy(galaxy_radius = 500,
				system_count = 15,
				allocation = RES_ALLOCATION,
				resource_deviation = .1,
				resource_variation = 2,
				price_modifier = 10)

for time in range(MAX_TIME_STEP):
	galaxy.time_step = time + 1
	galaxy.step(time)