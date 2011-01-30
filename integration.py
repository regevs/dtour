#
# Integration Score 
#
__all__ = []
__author__ = "Regev Schweiger"

import random
import csv

from utils import *

@public
def random_case():	
	required_radius = [5, 10, 20, 50, 100, 150, 200]
	possible_rating = [1, 2, 3, 4, 5]
	distances = range(5,55,5) + range(50,210,10)

	while True:
		radius = random.choice(required_radius)
		rating1 = random.choice(possible_rating)
		rating2 = random.choice(possible_rating)
		distance1 = random.choice(distances)
		distance2 = random.choice(distances)
		if ((rating1 < rating2) and (distance1 < distance2)) or ((rating2 < rating1) and (distance2 < distance1)):
			break

	return (radius, rating1, distance1, rating2, distance2)


@public
def create_test_cases(n_cases, filename):	
	cases = [random_case() for i in xrange(n_cases)]
	writer = csv.writer(file(filename, 'wb'), lineterminator='\n')
	writer.writerows(cases)

		