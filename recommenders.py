#
# Final Recommenders
#
__all__ = []
__author__ = "Regev S"

import geopy.distance


# Self imports
import integration

import recommender_systems
import recommender_systems.simple
import recommender_systems.item_based
import recommender_systems.user_based


class NiceList(list):
    
    def __init__(self, iterable=None, fields=None):
        list.__init__(self, iterable)
        self.fields = fields

    def __repr__(self):
        if self.fields == None:
            use_fields = map(str, range(self.__len__()))
        else:
            use_fields = self.fields
        return '\t'.join(["%s = %s" % (field, str(value)) for field, value in zip(use_fields, self)])


class Recommender:

    def __init__(self, places_recommender_data, weather_client, integration_sorter_class, integration_filter_class, recommender_system):
        self._places_recommender_data = places_recommender_data
        self._weather_client = weather_client
        self._integration_sorter_class = integration_sorter_class
        self._integration_filter_class = integration_filter_class
        self._recommender_system = recommender_system

        self._check_userid = False



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

    def _CheckLegalValues(self, parameter_name, parameter, legal_values):
        if (parameter != None) and (parameter not in legal_values):
            raise ValueError("%s should be one of %s (given: %s)" % (parameter_name, str(legal_values), str(parameter)))    

        


    _legal_sizes = [1,2,3,4]
    _legal_expert_ranks = [1,2,3,4,5]
    _legal_kosher = [True, False]
    _legal_visiting_center = [True, False]
    _legal_visiting_center_free_admission = [True, False]         


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

        if (self._check_userid and userid == ""):
            raise ValueError("Nonempty User ID should be given")

        #
        # Make sure the input is legal
        #
        self._CheckLegalValues("size", size, self._legal_sizes)
        self._CheckLegalValues("expert_rank", expert_rank, self._legal_expert_ranks)
        self._CheckLegalValues("kosher", kosher, self._legal_kosher)
        self._CheckLegalValues("visiting_center", visiting_center, self._legal_visiting_center)
        self._CheckLegalValues("visiting_center_free_admission", visiting_center_free_admission, self._legal_visiting_center_free_admission)


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
        self._aux_data = {}
        for uid in relevant_places:

            distance    = self._Distance(self._places_recommender_data[uid]['latlong'], location)                    
            rating      = self._recommender_system.PredictRating(userid, uid, True)            
                
            self._aux_data[uid] = (uid, self._places_recommender_data[uid]['raw']['wineryname'], distance / 1000.0, rating)
            self._scores[uid] = self._integration_sorter.Score(distance=distance, rating=rating, required_radius=required_radius)
        
        best = sorted(relevant_places, key=lambda uid: self._scores[uid], reverse=True)[:n_items]
        with_data = [NiceList(self._aux_data[b], ["ID", "Name", "Distance (km)", "Predicted Rating"]) for b in best] 
                        
        return with_data








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
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = recommender_systems.simple.ExpertRating(places_recommender_data))

        
__all__.append('SlopeOneRecommender')
class SlopeOneRecommender(Recommender):


    def __init__(self, 
                 places_recommender_data,
                 users_recommender_data,
                 rating_recommender_data, 
                 weather_client=None):
        
        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = recommender_systems.item_based.SlopeOneRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data, False)
                             )

        self._check_userid = True
        
__all__.append('WeightedSlopeOneRecommender')
class WeightedSlopeOneRecommender(Recommender):


    def __init__(self, 
                 places_recommender_data,
                 users_recommender_data,
                 rating_recommender_data, 
                 weather_client=None):
        
        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = recommender_systems.item_based.SlopeOneRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data, True)
                             )        
        self._check_userid = True

      
__all__.append('PearsonRecommender')
class PearsonRecommender(Recommender):


    def __init__(self, 
                 places_recommender_data,
                 users_recommender_data,
                 rating_recommender_data, 
                 weather_client=None):
        
        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = recommender_systems.user_based.PearsonRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data)
                             )        
           
        self._check_userid = True
    
                    
            
__all__.append('TFIDFRecommender')
class TFIDFRecommender(Recommender):


    def __init__(self, 
                 places_recommender_data,
                 users_recommender_data,
                 rating_recommender_data, 
                 weather_client=None):
        
        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = recommender_systems.item_based.TFIDFRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data, 
                                                                    [], 
                                                                    ['kosher', 'visiting_center', 'size', 'expert_rank'])
                             )        
           
        self._check_userid = True
                    
                
__all__.append('HybridLinearRecommender')
class HybridLinearRecommender(Recommender):


    def __init__(self, 
                 places_recommender_data,
                 users_recommender_data,
                 rating_recommender_data, 
                 weather_client=None):
        
        collab_rs = recommender_systems.user_based.PearsonRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data)

        content_rs = recommender_systems.item_based.TFIDFRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data, 
                                                                    [], 
                                                                    ['kosher', 'visiting_center', 'size', 'expert_rank'])

        hybrid_rs = recommender_systems.hybrid.LinearHybridRecommender([collab_rs, content_rs], [ 1.03326833, -0.03694432])

        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = hybrid_rs
                             )        
           
        self._check_userid = True            
            
        
__all__.append('HybridAugmentedRecommender')
class HybridAugmentedRecommender(Recommender):


    def __init__(self, 
                 places_recommender_data,
                 users_recommender_data,
                 rating_recommender_data, 
                 weather_client=None):
        
        collab_rs = recommender_systems.user_based.PearsonRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data)

        content_rs_class = recommender_systems.item_based.TFIDFRecommenderSystem


        hybrid_rs = recommender_systems.hybrid.FeatureAugmentRecommender(content_rs_class, collab_rs, [], ['kosher', 'visiting_center', 'size', 'expert_rank'])

        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = hybrid_rs
                             )        
           
        self._check_userid = True              


__all__.append('DemographicRecommender')
class DemographicRecommender(Recommender):


    def __init__(self, 
                 places_recommender_data,
                 users_recommender_data,
                 rating_recommender_data, 
                 weather_client=None):
        
        Recommender.__init__(self, 
                             places_recommender_data            = places_recommender_data,
                             weather_client                     = weather_client,
                             integration_sorter_class           = integration.LinearIntegratorSorter,
                             integration_filter_class           = integration.BasicIntegratorFilter,
                             recommender_system                 = recommender_systems.user_based.DemographicRecommenderSystem(
                                                                    places_recommender_data,
                                                                    users_recommender_data,
                                                                    rating_recommender_data, 
                                                                    ['sex', 'job', 'zip'], 
                                                                    ['age'])
                             )        
           
        self._check_userid = True

