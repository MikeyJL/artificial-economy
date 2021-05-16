import random
import pandas as pd
from pandas.core.tools.datetimes import to_time
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

for time in range(1, MAX_TIME_STEP + 1):
	galaxy.step(time)
	if time == MAX_TIME_STEP or time == 1:
		print('\n--- Galaxy ---\n')
		print('time_step: %s' % time)
		print('total_value: %s' % galaxy.total_value)
		print('\n--- Systems ---\n')
		print(pd.read_csv('data/systems.csv').to_string(index = False))
		print('\n--- Exports ---\n')
		print(pd.read_csv('data/exports.csv').to_string(index = False))
		print('\n--- Imports ---\n')
		print(pd.read_csv('data/imports.csv').to_string(index = False))