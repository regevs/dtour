#
# Data acquisition and processing
#
__all__ = []
__author__ = "Regev Schweiger"

import gdata.spreadsheet.service
import geopy.geocoders

import shelve
import warnings
import cPickle
import random
import os.path



__all__.append('GoogleSpreadsheetAcquisitor')
class GoogleSpreadsheetAcquisitor:

    def __init__(self, email, password):
        """
        Create a client that can get a google spreadsheet easily and download its data.
        
        email   - the email/username (e.g., "username@gmail.com")
        pass    - the password
        
        """
        
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.source = 'Spreadsheets GData Sample'
        self.gd_client.ProgrammaticLogin()       
                

    def GetSpreadsheet(self, spreadsheet_key, sheet_number):
        """
        Get the data from a spreadsheet. 
        
        spreadsheet_key     - The key of the spreadsheet; the part after 'ccc?key=*' in the url.
                              e.g., for https://spreadsheets2.google.com/ccc?key=tlDnaV6yZmlw1dXUTf2aXAQ&hl=en#gid=0, 
                              the key is "tlDnaV6yZmlw1dXUTf2aXAQ"
                              
        sheet_number        - The number of the worksheet (this worksheet should exist)
        
        """
        
        worksheet_feed = self.gd_client.GetWorksheetsFeed(spreadsheet_key)
        if len(worksheet_feed.entry) <= sheet_number:
            raise IndexError("No worksheet number %d (total %d)" % (sheet_number,len(worksheet_feed.entry)))
        worksheet_key = worksheet_feed.entry[sheet_number].id.text.split('/')[-1]
        list_feed = self.gd_client.GetListFeed(spreadsheet_key, worksheet_key)
        final_rows = []
        for row in list_feed.entry:
            d = {}
            for k,v in row.custom.iteritems():
                d[k] = v.text
            final_rows.append(d)
        return final_rows
            
__all__.append('GeocodingCache')
class GeocodingCache:
    """
    A geocoder with a builtin file cache. Can be accessed like a dictionary, and return
    a tuple of text representation and a tuple of lat/long (as returned by google).
    
    Use like this:
    
    >>> G = GeocodingCache(filename)
    >>> G["Jerusalem, Israel"]
    (u'Jerusalem, Israel', (31.768861999999999, 35.203856000000002))
    
    
    """
    
    
    def __init__(self, shelve_filename):
        """
        shelve_filename - The shelve filename in which to keep geocoding cached results.              
        
        """
        
        self.shelve_filename = shelve_filename
        self.shelve_obj = shelve.open(self.shelve_filename)        
        self.geocoder = geopy.geocoders.Google(resource="maps", output_format="kml")
    
    def __getitem__(self, key):
        if not self.shelve_obj.has_key(key):
            try:
                self.shelve_obj[key] = self.geocoder.geocode(key)
            except:
                self.shelve_obj[key] = (-1, -1)
        return self.shelve_obj[key]
            
    def __del__(self):
        self.shelve_obj.close()

        

class RecommenderData:
    """
    A class containing data for recommendation.
    
    Data is in the 'data' member.
    """

    data = {}

    def __init__(self, filename, google_key=None, google_email=None):
        """
        filename            - The filename containing the data         
        
        Optional:
        google_key          - A key for the google spreadshete from which the object can be synchronized
        google_email        - The email with which to use google

        """
        
        self.filename = filename

        self.google_key = google_key
        self.google_email = google_email

        if os.path.exists(self.filename):
            self.data = cPickle.load(file(self.filename, 'rb'))
        else:
            self.data = {}
            
    def _ReturnIfLegal(self, uid, parameter, legal_values):
        if isinstance(parameter, str):
            if parameter in legal_values:
                return parameter
            else:
                warnings.warn("ID %s: illegal value %s" % (uid, parameter))
                return None
        else:
            return None
        
    def Sync(self, password, verbose=False, reset=True, sheet_number=0):
        assert self.google_key != None
        if reset:
            self.Reset()
        self.google_spreadsheet_acquisitor = GoogleSpreadsheetAcquisitor(self.google_email, password)
        self.raw_google_results = self.google_spreadsheet_acquisitor.GetSpreadsheet(self.google_key, sheet_number)
        self.UpdateFromGoogle(self.raw_google_results, verbose=verbose)
        self.Save()


    def UpdateFromGoogle(self, google_results, verbose=False):            
        raise NotImplementedError()

    def __getitem__(self, key):
        return self.data[key]

            
    def Save(self):
        """
        Save current state
        """
        cPickle.dump(self.data, file(self.filename, 'wb'), -1)
        
    def Reset(self):
        """
        Reset all data
        """
        self.data = {}
                
    def __del__(self):
        self.Save()
        

__all__.append("PlacesRecommenderData")
class PlacesRecommenderData(RecommenderData):

    NO_LATLONG = None
    
    _legal_sizes = map(str, [1,2,3,4])
    _legal_expert_ranks = map(str, [1,2,3,4,5])
    _legal_kosher = ['Yes', 'No']
    _legal_visiting_center = ['Yes', 'No']


    def __init__(self, filename, geocoding_cache, google_key=None, google_email=None):
        """
        filename            - The filename containing the data 
        geocoding_cache     - An instance of GeocodingCache that contains geocoding info
        
        Optional:
        google_key          - A key for the google spreadshete from which the object can be synchronized
        google_email        - The email with which to use google

        """
        RecommenderData.__init__(self, filename, google_key, google_email)
        self.geocoding_cache = geocoding_cache

   
    def UpdateFromGoogle(self, google_results, verbose=False):
        """
        Add or update information from data download from a google spreadsheet using GoogleSpreadsheetAcquisitor.
        
        google_results  - the results (return of GoogleSpreadsheetAcquisitor.GetSpreadsheet)
        """
        for n_result, result in enumerate(google_results):
            if verbose:
                print "Updating %d / %d - %s " % (n_result+1, len(google_results), result['address'])
            
            # Fill information from the spreadsheet
            uid = result['id']
            if not self.data.has_key(uid):
                self.data[uid] = {}
            
            # Raw information
            self.data[uid]['raw'] = result
            
            # latlong (try geocoding if necessary)
            address = result['address']
            if isinstance(address, str):
                self.data[uid]['latlong'] = self.geocoding_cache[address][1]
            else:
                self.data[uid]['latlong'] = self.NO_LATLONG
            if self.data[uid]['latlong'] == -1:
                self.data[uid]['latlong'] = self.NO_LATLONG
                
            # size
            self.data[uid]['size'] = self._ReturnIfLegal(uid, result['size'], self._legal_sizes)
            if self.data[uid]['size'] != None:
                self.data[uid]['size'] = int(self.data[uid]['size'])
              
            # expert rank
            self.data[uid]['expert_rank'] = self._ReturnIfLegal(uid, result['rogovrank'], self._legal_expert_ranks)
            if self.data[uid]['expert_rank'] != None:
                self.data[uid]['expert_rank'] = int(self.data[uid]['expert_rank'])
            
            # kosher
            self.data[uid]['kosher'] = (self._ReturnIfLegal(uid, result['kosher'], self._legal_kosher) == 'Yes')
            
            # visiting center
            self.data[uid]['visiting_center'] = (self._ReturnIfLegal(uid, result['visitingcenter'], self._legal_visiting_center) == 'Yes')
            
            # visiting center free admission
            val = result['visitorcenteradmition']
            if val == None:
                self.data[uid]['visiting_center_free_admission'] = None
            elif val == "Free":
                self.data[uid]['visiting_center_free_admission'] = True
            else:
                self.data[uid]['visiting_center_free_admission'] = False
                
            # time
            if not self.data[uid].has_key('hours'):
                self.data[uid]['hours'] = {}                
            for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:            
                val = result[day]
                if val == None:
                    self.data[uid]['hours'][day] = None
                elif val.isdigit():
                    self.data[uid]['hours'][day] = int(val)
                else:
                    self.data[uid]['hours'][day] = None



__all__.append("UsersRecommenderData")
class UsersRecommenderData(RecommenderData):

    def UpdateFromGoogle(self, google_results, verbose=False):
        """
        Add or update information from data download from a google spreadsheet using GoogleSpreadsheetAcquisitor.
        
        google_results  - the results (return of GoogleSpreadsheetAcquisitor.GetSpreadsheet)
        """
        for n_result, result in enumerate(google_results):
            if verbose:
                print "Updating %d / %d - %s " % (n_result+1, len(google_results), result['id'])    

            # Fill information from the spreadsheet
            uid = result['id']
            if not self.data.has_key(uid):
                self.data[uid] = {}
            
            # Raw information
            self.data[uid]['raw'] = result

__all__.append("RatingRecommenderData")
class RatingRecommenderData(RecommenderData):

    _legal_rating = map(str, [1,2,3,4,5])

    def UpdateFromGoogle(self, google_results, verbose=False):
        """
        Add or update information from data download from a google spreadsheet using GoogleSpreadsheetAcquisitor.
        
        google_results  - the results (return of GoogleSpreadsheetAcquisitor.GetSpreadsheet)
        """
        for n_result, result in enumerate(google_results):
            if verbose:
                print "Updating %d / %d - (%s, %s) " % (n_result+1, len(google_results), result['placeid'], result['userid'])    

            # Fill information from the spreadsheet
            placeid = result['placeid']
            userid = result['userid']
            uid = (placeid, userid)
            if not self.data.has_key(uid):
                self.data[uid] = {}
            
            # Raw information
            self.data[uid]['raw'] = result   
            self.data[uid]['placeid'] = placeid
            self.data[uid]['userid'] = userid

            # rating
            self.data[uid]['rating'] = self._ReturnIfLegal(uid, result['rating'], self._legal_rating)
            if self.data[uid]['rating'] != None:
                self.data[uid]['rating'] = int(self.data[uid]['rating'])

def select_rating_subset(movielens_filename, user_ids, places_ids):
    n_users = len(user_ids)
    n_places = len(places_ids)

    lines = [map(int, x.split('\t')[:3]) for x in open(movielens_filename).read().split('\n') if x]                
    total_users = len(set([l[0] for l in lines]))
    total_places = len(set([l[1] for l in lines]))

    assert n_users <= total_users
    subset_users = random.sample(range(1,total_users+1), n_users)

    assert n_places <= total_places
    subset_places = random.sample(range(1,total_places+1), n_places)

    subset_rating = [[user_ids[subset_users.index(l[0])], places_ids[subset_places.index(l[1])], l[2]] for l in lines if l[0] in subset_users and l[1] in subset_places]
    return subset_rating

