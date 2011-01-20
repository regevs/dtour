#
# Recommender Algorithms
#
__all__ = []
__author__ = "Regev Schweiger"

import time


__all__.append('SimpleRecommender')
class SimpleWineryRecommender:

    _legal_sizes = [1,2,3,4]
    _legal_expert_ranks = [1,2,3,4,5]
    _legal_kosher = [True, False]
    _legal_visiting_center = [True, False]
    _legal_visiting_center_free_admission = [True, False]
    
    _delta_time_before_close = 1*60*60       # (in seconds)

    def __init__(self, recommender_data):
        """
        Recommends according to several simple criteria.
        
        recommender_data    - RecommenderData object with the data from which to recommend
        """
        self.recommender_data = recommender_data
        
    def _LegalLatlong(self, latlong):
        if len(latlong) != 2:
            return False
        if not all([isinstance(x, float) for x in latlong]):
            return False
        return True
        
    def _CheckLegalValues(self, parameter_name, parameter, legal_values):
        if (parameter != None) and (parameter not in legal_values):
            raise ValueError("%s should be one of %s (given: %s)" % (parameter_name, str(legal_values), str(parameter)))
      
    
    def Recommend(self,
                  n_items = 1,
                  location = None,
                  size = None,
                  expert_rank = None,
                  kosher = None,
                  visiting_center = None,
                  visiting_center_free_admission = None,
                  visit_time = None                  
                 ):
        
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
                    
            if add_item:
                relevant_places.append(uid)
                
        return relevant_places
                    
            
                
                
            
            
        
        
