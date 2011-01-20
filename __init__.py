#
# Main dtour package file
#

# Python imports
import inspect
import os, os.path

# Self imports
import utils
import data_processing
import recommenders



# TODO: remove this when stable
reload(utils)
reload(data_processing)
reload(recommenders)



#
# TODO: Remove when stable
#
GOOGLE_USER = "israelwineroute@gmail.com"

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

def sync():
    G = data_processing.GoogleSpreadsheetAcquisitor(GOOGLE_USER, "dangivol")
    final = G.GetSpreadsheet(WINEDATA_KEY_1, 0)
    RD.UpdateFromGoogle(final, verbose=True)

SW = recommenders.SimpleWineryRecommender(RD)