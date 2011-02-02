#
# Integration Score 
#
__all__ = []
__author__ = "Regev Schweiger"

# Python imports
import geopy.distance
import time
import random
import csv
import inspect

# Self imports
from utils import *


#
# Intergation filters
#
# These classes are in charge of filtering a list of places .
#

class IntegratorFilter(object):
    """An integration filter abstract class"""
    pass

       









__all__.append("BasicIntegratorFilter")
class BasicIntegratorFilter(IntegratorFilter):

    
    _delta_time_before_close = 1*60*60       # (in seconds)    

    def __init__(self, 
                  size = None,
                  expert_rank = None,
                  kosher = None,
                  visiting_center = None,
                  visiting_center_free_admission = None,
                  visit_time = None,
                  use_weather = False,
                  use_only_ids = None,
                  weather_client = None):
        #
        # Copy all arguments to members
        #
        args, dummy, dummy, values = inspect.getargvalues(inspect.currentframe())
        for arg in args:
            if arg != "self":
                setattr(self, arg, values[arg])




    def Filter(self, info):
        """
        Gets an information for an item.

        Return whether it should be filtered or not.
        """

        add_item = True
        
        if add_item and (self.use_only_ids != None) and (uid not in self.use_only_ids):
            add_item = False
        
        if add_item and (info['latlong'] == None):
            add_item = False
        
        if add_item and (self.size != None) and (info['size'] < self.size):
            add_item = False
            
        if add_item and (self.expert_rank != None) and (info['expert_rank'] < self.expert_rank):
            add_item = False
            
        if add_item and (self.kosher != None) and (self.kosher == True and info['kosher'] == False):
            add_item = False
            
        if add_item and (self.visiting_center != None) and (self.visiting_center == True and info['visiting_center'] == False):
            add_item = False
            
        if add_item and (self.visiting_center_free_admission != None) and (self.visiting_center_free_admission == True and info['visiting_center_free_admission'] == False):
            add_item = False
            
        if add_item and self.visit_time != None:
            day_of_visit = time.strftime("%A", time.localtime(self.visit_time)).lower()
            if info['hours'][day_of_visit] != None:
                closing_at_that_day = time.mktime(time.strptime(time.strftime("%A, %d %b %Y", time.localtime(self.visit_time)) + " %d:00:00" % (info['hours'][day_of_visit]), "%A, %d %b %Y %H:%M:%S"))
                if self.visit_time > (closing_at_that_day - self._delta_time_before_close):
                    add_item = False
            if day_of_visit == 'saturday' and self.kosher == True:
                add_item = False
                    
        if add_item and self.use_weather:                
            if not self.weather_client.GoodForWinery(self.weather_client.GetCondition(info['latlong'])):
                add_item = False
            
        return add_item
                




#
# Intergation sorters
#
# These classes are in charge of sorting a list of places after they have been filtered.
#




class IntegratorSorter(object):
    """An integration score abstract class"""

    def Score(self, distance, rating, required_radius):
        raise NotImplementedError()
        






__all__.append("StupidIntegrator")
class StupidIntegratorSorter(IntegratorSorter):
    """
    A very simple integrator sorter.

    80%% for location, 20%% for rank.
    Location has maximal cutoff
    """

    _weights = [0.8, 0.2]
    _max_distance = 30 * 1000

    _min_rating = 1
    _max_rating = 5

    def Score(self, distance, rating, required_radius=None):
        if distance > self._max_distance:
            normalized_distance = 0
        else:
            normalized_distance = float(self._max_distance - distance) / self._max_distance

        normalized_expert_rank = float(rating - self._min_rating)/(self._max_rating - self._min_rating)        
        res = normalized_distance * self._weights[0] + normalized_expert_rank * self._weights[1]    
        return res












        

#
# Helping functions for the generation of tests cases for the integration sorter
#

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

