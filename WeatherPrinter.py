'''
Created on Jun 27, 2017

@author: danny
'''

import os.path, sys
import unittest

'''
Fetch weather info based on zipcode

input:    zipcode  - city zipcode
          appId    - api key from 
return: json of city
        -1 on error
'''
def getWeatherInfo(zipcode, appId):    
    retVal = -1
    
    
    
    return retVal

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
        self.assertEqual('foo'.upper(), 'FOO')
        
        

if __name__ == '__main__':
    unittest.main()