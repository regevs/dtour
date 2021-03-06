#
# Integration Score 
#
__all__ = []
__author__ = "Regev S"

# Python imports
import geopy.distance
import time
import random
import csv
import inspect



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


__all__.append("LinearIntegratorSorter")
class LinearIntegratorSorter(IntegratorSorter):
    """
    A linear integrator sorter.

    There is no consideration here for the required radius. 
    The weights have been learned according to a user survey.
    """

    _beta = -0.028

    def Score(self, distance, rating, required_radius=None):
        res = rating + self._beta * distance * 1000
        return res










        

#
# Helping functions for the analysis of tests cases for the integration sorter
#


def create_test_cases(n_cases, filename):   

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

            # don't put cases which are trivial 
            if ((rating1 < rating2) and (distance1 < distance2)) or ((rating2 < rating1) and (distance2 < distance1)):
                break

        return (radius, rating1, distance1, rating2, distance2)

    cases = [random_case() for i in xrange(n_cases)]
    writer = csv.writer(file(filename, 'wb'), lineterminator='\n')
    writer.writerows(cases)


def anaylze_integration_survey(filename=r"c:\temp\Integration Score Survey.csv", required_radius=None, consensus=6):
    import misc

    thres = consensus
    filt_rad = required_radius

    def find_frequent(a):        
        c = misc.count(a)
        m = max([(v,k) for k,v in c.items()])[1]
        return m

    def count_frequent(a):
        m = find_frequent(a)
        return len([x for x in a if x == m])

    # read all lines and turn into integers
    lines = [map(int, l) for l in list(csv.reader(file(filename, 'rb')))[1:]]
    
    # switch it so the lower rating will be left
    newlines = []
    for l in lines:
        if l[1]<l[3]:
            newlines.append(l)
        else:
            nl = [l[0]] + l[3:5] + l[1:3] + [(1 if x==2 else 2) for x in l[5:]]
            newlines.append(nl)

    # sort according to consistency
    newlines = [x + [count_frequent(x[5:])] for x in newlines]
    res = sorted(newlines, key=lambda x: (x[-1], find_frequent(x[5:5+7]), x[0], x[2], x[4], x[1], x[3]))

    # make regression input
    reg = [(x[:5], find_frequent(x[5:5+7])) for x in res if x[-1] >= thres and (filt_rad == None or x[0] == filt_rad)]

    return reg

def find_best_linear(input):
    # reorder so right should be chosen, throw radius
    a = [(x[0][1:5] if x[1]==2 else x[0][3:5]+x[0][1:3]) for x in input]
    b = [((float(x[0]-x[2])/float(x[3]-x[1])), float(x[3]-x[1])>0) for x in a]
    rng = min([x[0] for x in b]), max([x[0] for x in b])
    step = 0.001
    scores = [(len([x for x in b if x[1]==True and x[0]<beta]) + len([x for x in b if x[1]!=True and x[0]>beta])  , beta) for beta in arange(rng[0], rng[1]+step, step)]
    x = sorted(scores)[-1]
    return (x[1], x[0], len(input))







