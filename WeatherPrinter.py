'''
Created on Jun 27, 2017

@author: danny
'''

import os.path, sys
import unittest
import urllib2, json, httplib

'''
Read api key from api.key

return api key or -1 if error
'''
def getApiKey(fileName = 'api.key'):
    if (os.path.isfile(fileName) == True):
        # return 1st line of fileName
        with open(fileName, 'r') as f:
            return f.readline()
    else:
        return -1

class WeatherCity:
    '''
    All temps are in C
    '''
    mParseCode = -1
    mApiKey = -1
    mCityName = 0
    mZipcode = 12345
    mMaxTemp = -300
    mCurTemp = -300
    mMinTemp = -300
    mIconUrl = 0 # url for weather icon
    mWeatherDescription = 0
    
    def __init__(self, zipcode, keyFile = 'api.key'):
        self.mApiKey = getApiKey(keyFile)
        self.mZipcode = zipcode

        if (self.mApiKey == -1):
            print "Error creating WeatherCity object for " + str(zipcode)
            return
        
        # build api call
        apiUrl = "http://api.openweathermap.org/data/2.5/weather?zip=" + str(zipcode) + ",us&appid=" + self.mApiKey
        apiResponse = urllib2.urlopen(apiUrl)
        resultJson = json.loads(apiResponse.read())        
        if (0 != self.parseWeatherJson(resultJson)):
            print "Error parsing WeatherCity object for " + str(zipcode)
            return
        
    # parse to class member given json response of api    
    def parseWeatherJson(self, jsonString):
        kelvin = 273
        
        self.mCityName = jsonString['name']
        self.mCurTemp = jsonString['main']['temp'] - kelvin 
        self.mMaxTemp = jsonString['main']['temp_max'] - kelvin
        self.mMinTemp = jsonString['main']['temp_min'] - kelvin
        self.mWeatherDescription = jsonString['weather'][0]['description']
        self.mIconUrl = "http://openweathermap.org/img/w/" + str(jsonString['weather'][0]['icon']) + ".png"
        
        return self.sanityCheck()

    '''
    Check if member data makes sense such as feasible temp, alive url
    return 0 if passed
    '''
    def sanityCheck(self):
        isGood = True        
        isGood &= (self.mCurTemp > -50) & (self.mCurTemp < 50)
        isGood &= (self.mMaxTemp > -50) & (self.mMaxTemp < 50)
        isGood &= (self.mMinTemp > -50) & (self.mMinTemp < 50)
        
        # check if icon url is alive        
        try:
            urllib2.urlopen(self.mIconUrl)
        except Exception:
            isGood = False
        
        self.mParseCode = not isGood        
        return (not isGood)
    
    # todo - implement
    '''
    Main function of this class
    Add weather info to photoPath picture file
    
    x, y - top left pizel position of weather info 
    '''
    def addWeatherToPhoto(self, photoPath, x = 540, y = 10, fontSize = 30, fontPath = 'usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', style = 1):
        pass

##########################################################################
# unit test area
##########################################################################
class TestWeatherPrinter(unittest.TestCase):

    def test_api_exist(self):
        apiKeyFIle = 'api.key'
        
        if (os.path.isfile(apiKeyFIle) != True):
            print " Error: " + apiKeyFIle + " not exists"
            print " Perhaps you may need to register a free key with https://openweathermap.org/price"
            print " and put the key inside " + apiKeyFIle + " file on the same directory as this unit test script"
            sys.exit(1)

    def test_info_success(self):        
        chaska = WeatherCity(55318)
        self.assertEqual(chaska.mParseCode, 0)
        

if __name__ == '__main__':
    unittest.main()