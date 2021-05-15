import random
from agents import Economy

# Constants
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

Economy(10, RES_ALLOCATION, .1, 10)