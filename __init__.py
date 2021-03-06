#
# Main dtour package file
#

# Python imports
import inspect
import os, os.path
import time

# Self imports
import misc
import data_processing
import recommenders
import recommender_systems
import recommender_systems.base
import recommender_systems.simple
import recommender_systems.user_based
import recommender_systems.item_based
import recommender_systems.hybrid
import recommender_systems.evaluation
import weather
import integration


# TODO: remove this when stable
reload(misc)
reload(data_processing)
reload(recommenders)
reload(recommender_systems.base)
reload(recommender_systems.simple)
reload(recommender_systems.user_based)
reload(recommender_systems.item_based)
reload(recommender_systems.hybrid)
reload(recommender_systems.evaluation)
reload(weather)
reload(integration)






#
# TODO: Remove when stable (?)
#
GOOGLE_USER = "israelwineroute@gmail.com"
GOOGLE_API_KEY = "ABQIAAAAW9I8jXDa_ffCaqdiN7Yv_BSlop2PrIEswDUepZEwXTSfTXLhJxTBR-lwf2SKuyYwhBvcgrGPaPygNQ"

PLACES_KEY_1 	= 'tlp_N0Ej7v_fz0MMMlV_rdA'
USERS_KEY_1 	= 't2ps1aNIOmQKb-qXMjtWfFg'
RATING_KEY_1 	= 'tvAEWLlgopSFsWrdwyWOURg'

#
# Where files are held
#

# Build the directories - use the script's directory as reference
scripts_dir = os.path.dirname(inspect.currentframe().f_code.co_filename)
data_dir = os.path.join(scripts_dir, 'data')

GEOCODING_CACHE_FILE = os.path.join(data_dir, "geocache.shelve")

PLACES_FILE 	= os.path.join(data_dir, "places_db.pcl")
USERS_FILE 		= os.path.join(data_dir, "users_db.pcl")
RATING_FILE 	= os.path.join(data_dir, "rating_db.pcl")

MOVIELENS_100K_FILE = os.path.join(data_dir, "datasets", "movielens", "100k", "u.data")


GC = data_processing.GeocodingCache(GEOCODING_CACHE_FILE)

RD_places 	= data_processing.PlacesRecommenderData(PLACES_FILE, GC, PLACES_KEY_1, GOOGLE_USER)
RD_users 	= data_processing.UsersRecommenderData(USERS_FILE, USERS_KEY_1, GOOGLE_USER)
RD_rating 	= data_processing.RatingRecommenderData(RATING_FILE, RATING_KEY_1, GOOGLE_USER)


# (to match old docs)
RD = RD_places


# Different versions of recommenders
SLO = recommenders.SlopeOneRecommender(RD_places, RD_users, RD_rating, weather.GoogleWeather())
WSLO = recommenders.WeightedSlopeOneRecommender(RD_places, RD_users, RD_rating, weather.GoogleWeather())

PEAR = recommenders.PearsonRecommender(RD_places, RD_users, RD_rating, weather.GoogleWeather())

SW = recommenders.SimpleWineryRecommender(RD_places, weather.GoogleWeather())
SWJ = recommenders.SimpleWineryRecommender(RD_places, weather.RainyInJerusalem())


TF = recommenders.TFIDFRecommender(RD_places, RD_users, RD_rating, weather.GoogleWeather())
HY = recommenders.HybridLinearRecommender(RD_places, RD_users, RD_rating, weather.GoogleWeather())
HY2 = recommenders.HybridAugmentedRecommender(RD_places, RD_users, RD_rating, weather.GoogleWeather())

DEMO = recommenders.DemographicRecommender(RD_places, RD_users, RD_rating, weather.GoogleWeather())





# Evaluators
MAE = recommender_systems.evaluation.AllButOneMeanAverageError()


#
# Convenience Functions
#

def newid():
    import random
    return hex(random.randrange(0,2**64))[2:-1].rjust(16, '0')

def csvwrite(rows, filename=r"c:\temp\regev.csv"):
	import csv
	csv.writer(file(filename, 'wb'), lineterminator='\n').writerows(rows)

def geocode(place):
	return GC[place][1]

def random_user():
	import random
	return random.choice(RD_users.keys())

def syncall(passwd):
	RD_places.Sync(passwd)
	RD_users.Sync(passwd)
	RD_rating.Sync(passwd)
