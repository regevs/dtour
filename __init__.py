#
# Main dtour package file
#

# Python imports
import inspect
import os, os.path

# Self imports
from utils import *
import data_processing



# TODO: remove this when stable
reload(utils)
reload(data_processing)



#
# TODO: Remove when stable
#
GOOGLE_USER = "israelwineroute@gmail.com"
GOOGLE_PASS = "dangivol"

WINEDATA_KEY_1 = '0AhuwU_YYO9CzdGxwX04wRWo3dl9mejBNTU1sVl9yZEE'

#
# Where files are held
#

# Build the directories - use the script's directory as reference
scripts_dir = os.path.dirname(inspect.currentframe().f_code.co_filename)
data_dir = os.path.join(os.path.split(scripts_dir)[0], 'data')

GEOCODING_CACHE = os.path.join(data_dir, "geocache.shelve")




