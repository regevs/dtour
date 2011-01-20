#
# Weather 
#
__all__ = []
__author__ = "Regev Schweiger"


import pywapi

class WeatherAcquisitor:

    good_for_winery_dict = { u"": True,
                             u"Clear": True,
                             u"Cloudy": True,
                             u"Fog": True,
                             u"Haze": True,
                             u"Light Rain": False,
                             u"Mostly Cloudy": True,
                             u"Overcast": True,
                             u"Partly Cloudy": True,
                             u"Rain": False,
                             u"Rain Showers": False,
                             u"Showers": False,
                             u"Thunderstorm": False,
                             u"Chance of Showers": False,
                             u"Chance of Snow": False,
                             u"Chance of Storm": False,
                             u"Mostly Sunny": True,
                             u"Partly Sunny": True,
                             u"Scattered Showers": False,
                             u"Sunny": True,
                             u"Ice/Snow": False,
                             u"Freezing Rain": False,
                             u"Freezing Drizzle": False,
                             u"Flurries": False,
                             u"Rain and Snow": False,
                             u"Snow Showers": False,
                             u"Isolated Thunderstorms": False}  

    def GoodForWinery(self, condition):
        return self.good_for_winery_dict[condition]
        
    def GetCondition(self, latlong):
        raise NotImplementedError

__all__.append('GoogleWeather')
class GoogleWeather(WeatherAcquisitor):

    def GetCondition(self, latlong):
        try:
            res = pywapi.get_weather_from_google(",,,%d,%d" % tuple([int(round(x * (10**6))) for x in latlong]))        
            return res['current_conditions']['condition']
        except:
            return u""
        
__all__.append('RainyInJerusalem')
class RainyInJerusalem(WeatherAcquisitor):      
    def GetCondition(self, latlong, radius_km=50):
        import geopy.distance
        dist = geopy.distance.distance(latlong, (31.768862, 35.203856)).m
        if dist < radius_km*1000:
            return u"Rain"
        else:
            return u"Sunny"




