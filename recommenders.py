#
# Recommender Algorithms
#
__all__ = []
__author__ = "Regev Schweiger"


import geopy.distance
import time


__all__.append('SimpleWineryRecommender')
class SimpleWineryRecommender:

    _legal_sizes = [1,2,3,4]
    _legal_expert_ranks = [1,2,3,4,5]
    _legal_kosher = [True, False]
    _legal_visiting_center = [True, False]
    _legal_visiting_center_free_admission = [True, False]
    
    _delta_time_before_close = 1*60*60       # (in seconds)
    _default_expert_rank = 3

    def __init__(self, recommender_data, weather_client):
        """
        Recommends according to several simple criteria.
        
        recommender_data    - RecommenderData object with the data from which to recommend
        weather_client      - A client to have weather info
        """
        self.recommender_data = recommender_data
        self.weather_client = weather_client
        
    def _LegalLatlong(self, latlong):
        if len(latlong) != 2:
            return False
        if not all([isinstance(x, float) for x in latlong]):
            return False
        return True
        
    def _CheckLegalValues(self, parameter_name, parameter, legal_values):
        if (parameter != None) and (parameter not in legal_values):
            raise ValueError("%s should be one of %s (given: %s)" % (parameter_name, str(legal_values), str(parameter)))
      
    def _Distance(self, latlong1, latlong2):
        return geopy.distance.distance(latlong1, latlong2).m 

    def _CombinedScore(self, distance, expert_rank):    
        weights = [0.8, 0.2]
        max_distance = 30 * 1000
        
        if distance > max_distance:
            normalized_distance = 0
        else:
            normalized_distance = float(max_distance - distance) / max_distance
        normalized_expert_rank = (expert_rank - 1.0)/4.0        
        return normalized_distance*weights[0] + normalized_expert_rank*weights[1]
        
    
    def Recommend(self,
                  n_items = 10,
                  location = None,
                  size = None,
                  expert_rank = None,
                  kosher = None,
                  visiting_center = None,
                  visiting_center_free_admission = None,
                  visit_time = None,
                  use_weather = False
                 ):
        """
        Recommend a winery according to the specified parameters.
        
        """        
        #
        # Make sure the input is legal
        #
        if not (isinstance(n_items, int) and n_items > 0):
            raise ValueError("n_items should be a positive integer (given: %s)" % str(n_items))
        
        if (location != None) and (not self._LegalLatlong(location)):
            raise ValueError("location was not a legal latlong tuple (given: %s)" % str(location))
            
        self._CheckLegalValues("size", size, self._legal_sizes)
        self._CheckLegalValues("expert_rank", expert_rank, self._legal_expert_ranks)
        self._CheckLegalValues("kosher", kosher, self._legal_kosher)
        self._CheckLegalValues("visiting_center", visiting_center, self._legal_visiting_center)
        self._CheckLegalValues("visiting_center_free_admission", visiting_center_free_admission, self._legal_visiting_center_free_admission)
        
        if (visit_time != None) and (not isinstance(visit_time, float)):
            raise ValueError("visit_time was not a legal time float. visit_time should be since the epoch, (e.g. time.time()) (given: %s)" % str(visit_time))
            
        #
        # Filter all irrelevant places
        #
        relevant_places = []
        
        for uid, info in self.recommender_data.data.iteritems():
            
            add_item = True
            
            if add_item and (info['latlong'] == None):
                add_item = False
            
            if add_item and (size != None) and (info['size'] < size):
                add_item = False
                
            if add_item and (expert_rank != None) and (info['expert_rank'] < expert_rank):
                add_item = False
                
            if add_item and (kosher != None) and (kosher == True and info['kosher'] == False):
                add_item = False
                
            if add_item and (visiting_center != None) and (visiting_center == True and info['visiting_center'] == False):
                add_item = False
                
            if add_item and (visiting_center_free_admission != None) and (visiting_center_free_admission == True and info['visiting_center_free_admission'] == False):
                add_item = False
                
            if add_item and visit_time != None:
                day_of_visit = time.strftime("%A", time.localtime(visit_time)).lower()
                if info['hours'][day_of_visit] != None:
                    closing_at_that_day = time.mktime(time.strptime(time.strftime("%A, %d %b %Y", time.localtime(visit_time)) + " %d:00:00" % (info['hours'][day_of_visit]), "%A, %d %b %Y %H:%M:%S"))
                    if visit_time > (closing_at_that_day - self._delta_time_before_close):
                        add_item = False
                if day_of_visit == 'saturday' and kosher == True:
                    add_item = False
                        
            if add_item and use_weather:                
                if not self.weather_client.GoodForWinery(self.weather_client.GetCondition(info['latlong'])):
                    add_item = False
                
            if add_item:
                relevant_places.append(uid)
                
        #
        # Sort all relevant places
        #
        self.scores = {}
        for uid in relevant_places:
            if location != None:
                distance = self._Distance(self.recommender_data.data[uid]['latlong'], location)
            else:
                distance = 0
                    
            if self.recommender_data.data[uid]['expert_rank'] != None:
                expert_rank = self.recommender_data.data[uid]['expert_rank']
            else:
                expert_rank = self._default_expert_rank
            self.scores[uid] = self._CombinedScore(distance, expert_rank)
        
        best = sorted(relevant_places, key=lambda uid: self.scores[uid], reverse=True)[:n_items]
                        
        return best
                    
            
                
                
            
            
        
        
