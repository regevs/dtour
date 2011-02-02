#
# Main dtour package file
#

# Python imports
import inspect
import os, os.path
import time

# Self imports
import utils
import data_processing
import recommenders
import recommender_systems.evaluation
import weather
import integration


# TODO: remove this when stable
reload(utils)
reload(data_processing)
reload(recommenders)
reload(recommender_systems.evaluation)
reload(weather)
reload(integration)






#
# TODO: Remove when stable (?)
#
GOOGLE_USER = "israelwineroute@gmail.com"
GOOGLE_API_KEY = "ABQIAAAAW9I8jXDa_ffCaqdiN7Yv_BSlop2PrIEswDUepZEwXTSfTXLhJxTBR-lwf2SKuyYwhBvcgrGPaPygNQ"

#PLACES_KEY_1 = '0AhuwU_YYO9CzdGxwX04wRWo3dl9mejBNTU1sVl9yZEE'
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

SW = recommenders.SimpleWineryRecommender(RD_places, weather.GoogleWeather())
SWJ = recommenders.SimpleWineryRecommender(RD_places, weather.RainyInJerusalem())




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

