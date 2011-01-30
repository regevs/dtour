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
import weather
import integration


# TODO: remove this when stable
reload(utils)
reload(data_processing)
reload(recommenders)
reload(weather)
reload(integration)



#
# TODO: Remove when stable
#
GOOGLE_USER = "israelwineroute@gmail.com"
GOOGLE_API_KEY = "ABQIAAAAW9I8jXDa_ffCaqdiN7Yv_BSlop2PrIEswDUepZEwXTSfTXLhJxTBR-lwf2SKuyYwhBvcgrGPaPygNQ"

WINEDATA_KEY_1 = '0AhuwU_YYO9CzdGxwX04wRWo3dl9mejBNTU1sVl9yZEE'

#
# Where files are held
#

# Build the directories - use the script's directory as reference
scripts_dir = os.path.dirname(inspect.currentframe().f_code.co_filename)
data_dir = os.path.join(scripts_dir, 'data')

GEOCODING_CACHE_FILE = os.path.join(data_dir, "geocache.shelve")
PLACES_FILE = os.path.join(data_dir, "places_db.pcl")


GC = data_processing.GeocodingCache(GEOCODING_CACHE_FILE)
RD = data_processing.RecommenderData(PLACES_FILE, GC)

def sync(passw, reset=True):
    RD.Reset()
    G = data_processing.GoogleSpreadsheetAcquisitor(GOOGLE_USER, passw)
    final = G.GetSpreadsheet(WINEDATA_KEY_1, 0)
    RD.UpdateFromGoogle(final, verbose=True)
    RD.Save()

SW = recommenders.SimpleWineryRecommender(RD, weather.GoogleWeather())
SWJ = recommenders.SimpleWineryRecommender(RD, weather.RainyInJerusalem())


def newid():
    import random
    return hex(random.randrange(0,2**64))[2:-1].rjust(16, '0')


