#
# Data acquisition and processing
#
__all__ = []
__author__ = "Regev Schweiger"

import gdata.spreadsheet.service
import geopy.geocoders
import shelve
import cPickle
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

        
__all__.append('RecommenderData')        
class RecommenderData:    
    def __init__(self, filename, geocoding_cache):
        """
        filename            - The filename containing the data 
        geocoding_cache     - An instance of GeocodingCache that contains geocoding info
        
        """
        
        self.filename = filename
        self.geocoding_cache = geocoding_cache
        if os.path.exists(self.filename):
            self.data = cPickle.load(file(self.filename, 'rb'))
        else:
            self.data = {}
            
        self.NO_LATLONG = None
        
    def UpdateFromGoogle(self, google_results, verbose=False):
        """
        Add or update information from data download from a google spreadsheet using GoogleSpreadsheetAcquisitor.
        
        google_results  - the results (return of GoogleSpreadsheetAcquisitor.GetSpreadsheet)
        """
        for n_result, result in enumerate(google_results):
            if verbose:
                print "Updating %d / %d - %s " % (n_result+1, len(google_results), result['address'])
                
            self.data[result['id']] = result
            address = result['address']
            if isinstance(address, str):
                self.data[result['id']]['latlong'] = self.geocoding_cache[address][1]
            else:
                self.data[result['id']]['latlong'] = self.NO_LATLONG
            if self.data[result['id']]['latlong'] == -1:
                self.data[result['id']]['latlong'] = self.NO_LATLONG
            
    def Save(self):
        """
        Save current state
        """
        cPickle.dump(self.data, file(self.filename, 'wb'), -1)
                
    def __del__(self):
        self.Save()
        
