#
# Final Recommenders
#
__all__ = []
__author__ = "Regev Schweiger"

import geopy.distance


# Self imports
import integration
import recommender_systems.simple

# TODO: remove when stable
reload(recommender_systems.simple)



class Recommender:
    def __init__(self, places_recommender_data, weather_client, integration_sorter_class, integration_filter_class, recommender_system):
        self._places_recommender_data = places_recommender_data
        self._weather_client = weather_client
        self._integration_sorter_class = integration_sorter_class
        self._integration_filter_class = integration_filter_class
        self._recommender_system = recommender_system

    def _Distance(self, latlong1, latlong2):
        if latlong1 == None or latlong2 == None:
            return 0
        return geopy.distance.distance(latlong1, latlong2).m
        
    def _LegalLatlong(self, latlong):
        if len(latlong) != 2:
            return False
        if not all([isinstance(x, float) for x in latlong]):
            return False
        return True         


    def Recommend(self,
                  n_items = 10,
                  userid = "",
                  required_radius = 0,                  
                  location = None,                  
                  size = None,
                  expert_rank = None,
                  kosher = None,
                  visiting_center = None,
                  visiting_center_free_admission = None,
                  visit_time = None,
                  use_weather = False,
                  use_only_ids = None
                 ):
        """
        Recommend a winery according to the specified parameters.
        
        userid      - The user ID according to which to recommend (default is empty)
        required_radius     - The radius which is considered "reasonable" for the query

        n_items     - The number of items to recommend (1 or more)
        location    - a lat/long tuple, around which to search; can be None

        size        - minimal size of a winery (1..4); can be None
        expert_rank - minimal expert rank of a winery (1..5); can be None
        kosher      - True is kosher is required, False or None else
        visiting_center     - True is a visiting center is required, False or None else
        visiting_center_free_admission -    True if a free visiting center is reuiqred, False or None else
        visit_time          - Time around which to time your visit; given in seconds since epoch; can be None (and be ignored)
                              e.g., for the current time; give time.time()
        use_weather         - Use current weather conditions to filter out places (True/False, default is False)

        use_only_ids        - (debugging) Pretend only these place IDs exist.
        """        
        
        #
        # Make sure the input is legal
        #
        if not (isinstance(n_items, int) and n_items > 0):
            raise ValueError("n_items should be a positive integer (given: %s)" % str(n_items))
        
        if (location != None) and (not self._LegalLatlong(location)):
            raise ValueError("location was not a legal latlong tuple (given: %s)" % str(location))


        #
        # Create sorter and integrator
        #
        self._integration_sorter = self._integration_sorter_class()
        self._integration_filter = self._integration_filter_class(  size = size,
                                                                  expert_rank = expert_rank,
                                                                  kosher = kosher,
                                                                  visiting_center = visiting_center,
                                                                  visiting_center_free_admission = visiting_center_free_admission,
                                                                  visit_time = visit_time,
                                                                  use_weather = use_weather,
                                                                  use_only_ids = use_only_ids,
                                                                  weather_client = self._weather_client)

            
        #
        # Filter all irrelevant places
        #
        relevant_places = []
        
        for uid, info in self._places_recommender_data.data.iteritems():          
            if self._integration_filter.Filter(info):
                relevant_places.append(uid)
                
        #
        # Sort all relevant places
        #
        self._scores = {}
        for uid in relevant_places:

            distance    = self._Distance(self._places_recommender_data[uid]['latlong'], location)                    
            rating      = self._recommender_system.PredictRating(userid, uid)            
                
            self._scores[uid] = self._integration_sorter.Score(distance=distance, rating=rating, required_radius=required_radius)
        
        best = sorted(relevant_places, key=lambda uid: self._scores[uid], reverse=True)[:n_items]
                        
        return best








__all__.append('SimpleWineryRecommender')
class SimpleWineryRecommender(Recommender):



    def __init__(self, places_recommender_data, weather_client=None):
        """
        Recommends according to several simple criteria.
        
        places_recommender_data    - PlacesRecommenderData object with the data from which to recommend
        weather_client             - A client to have weather info
        """                    
        
        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.StupidIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = recommender_systems.simple.ExpertRating(places_recommender_data))

        
   
      
    
           
    
    
                    
            
                
                
            
            
        
        
