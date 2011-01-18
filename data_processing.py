#
# Data acquisition and processing
#
__all__ = []
__author__ = "Regev Schweiger"

import gdata.spreadsheet.service
import geopy.geocoders
import shelve



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

    def __init___(self, shelve_filename):
        """
        shelve_filename - The shelve filename in which to keep geocoding cached results.
        
        """
        
        self.shelve_filename = shelve_filename
        self.shelve = shelve.open(self.shelve_filename)        
    
    __get__ = self.shelve.__get__
    __set__ = self.shelve.__set__
    
    def __del__(self):
        self.shelve.close()

