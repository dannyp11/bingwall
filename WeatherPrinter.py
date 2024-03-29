'''
Created on Jun 27, 2017

@author: danny
'''

import os.path, sys, time
import unittest
import urllib.request, urllib.error, urllib.parse, json, urllib.request, urllib.parse, urllib.error

from PIL import ImageFont, Image, ImageDraw

'''
Read api key from api.key

return api key or -1 if error
'''
def getApiKey(fileName = 'api.key'):
    if (os.path.isfile(fileName) == True):
        # return 1st line of fileName
        with open(fileName, 'r') as f:
            return f.readline().rstrip('\n')
    else:
        return -1

'''
Struct that contains location lat & lon
'''
class _locationData:
    def __init__(self):
        self.lat = -200
        self.lon = -200
        
    def isValid(self):
        return (abs(self.lat) <= 180 and abs(self.lon) <= 180)

class WeatherCity:
    def __init__(self, zipCode = 0, keyFile = 'api.key'):
        '''
        All temps are in C
        '''
        self.mParseCode = -1
        self.mApiKey = -1
        self.mCityName = 0 
        self.mMaxTemp = -300
        self.mCurTemp = -300
        self.mMinTemp = -300
        self.mIconUrl = 0 # url for weather icon
        self.mWeatherDescription = 0
        self.mSunRise = -1
        self.mSunSet = -1
        self.mHumid = -1
        self.mWindspeed = -1
        self.mZipcodeLocation = _locationData()
        self.mZipcode = str(zipCode)
        
        self.mApiKey = getApiKey(keyFile)
        
        if (self._isInternetOn() == False):
            print("Error creating WeatherCity object for " + self.mZipcode + ": no internet connection")
            return

        # If zipCode is invalid, try getting current location
        #  this is provided by geocode service that tracks ip address
        if (self.mZipcode == '0'):
            locReq = urllib.request.urlopen('http://freegeoip.net/json')
            locData = json.loads(locReq.read())
            self.mZipcodeLocation.lat = float(locData['latitude'])
            self.mZipcodeLocation.lon = float(locData['longitude'])
            self.mCityName = locData['city']
            print(json.dumps(locData, indent=4, sort_keys=True))
        
        else:
            # use zippotamus api to get lat & lon for zipcode
            zipcodeUrl = 'http://api.zippopotam.us/us/' + self.mZipcode
            locReq = urllib.request.urlopen(zipcodeUrl)
            locData = json.loads(locReq.read())
            print(json.dumps(locData, indent=4, sort_keys=True))
            
            self.mZipcodeLocation.lat = float(locData['places'][0]['latitude'])
            self.mZipcodeLocation.lon = float(locData['places'][0]['longitude'])
            self.mCityName = locData['places'][0]['place name']
            

        if (self.mApiKey == -1):
            print("Error creating WeatherCity object for " + self.mCityName + ": invalid apikey file " + keyFile)
            return
        
        resultJson = self._getWeatherData() 
        # for debug purpose
        print(json.dumps(resultJson, indent=4, sort_keys=True))
        
        parseResult = self._parseWeatherJson(resultJson)
        if (0 != parseResult):
            print("Error parsing WeatherCity object for " + self.mCityName + " code " + str(parseResult))
            self._dumpInfo()
            return
        
    '''
    Check if internet is on
    '''
    def _isInternetOn(self):
        googleUrl = 'http://216.58.192.142'
    
        try:
            urllib.request.urlopen(googleUrl, timeout=1)
            return True
        except urllib.error.URLError: 
            return False
        
    '''
    Draw fileColor text with black outline (if hasOutline = true)
    
    text - input
    font - font
    draw - draw object
    x, y - upperleft position of text
    fillcolor - color of text, default: white
    hasOutline - print outline or not, default: true
    
    return draw - result draw
            brX, brY - bottom right X and Y of textbox
    '''
    def _drawText(self, text, font, draw, x , y, fillColor = (255, 255, 255, 255), hasOutline = True):
        shadowcolor = (0,0,0,255)
        
        # thicker border, draw stroke
        if (hasOutline):
            draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
            draw.text((x+1, y+1), text, font=font, fill=shadowcolor)
            draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
            draw.text((x-1, y+1), text, font=font, fill=shadowcolor)
        
        # now draw the text over it
        draw.text((x, y), text, font=font, fill=fillColor)
        
        # get bottom right of text box
        txtW, txtH = draw.textsize(text, font)    
        brX = x + txtW
        brY = y + txtH
        
        return draw , brX, brY
    
    '''
    Draw icon onto photoImage using offset x, y
    
    return  img - result Image
            brX, brY - bottom right X and Y of icon
    '''
    def _pasteWeatherIcon(self, photoPath, photoImage, x, y):
        iconPath = photoPath + '.png'
        iconW = iconH = 0
        
        urllib.request.urlretrieve(self.mIconUrl, iconPath)        
        if (os.path.isfile(iconPath)):                        
            # paste icon to draw
            iconImg = Image.open(iconPath)                 
            
            croppedIconImg = iconImg
            imW, imH = croppedIconImg.size
            pix = croppedIconImg.load()
              
            # crop zero alpha area
            for pix_x in range(0, imW):
                for pix_y in range(0, imH):
                    (r,g,b,a) = pix[pix_x, pix_y]
                       
                    if (a == 0):
                        pix[pix_x, pix_y] = (0,0,0,0)
                         
            croppedIconImg = croppedIconImg.crop(croppedIconImg.getbbox())      
            iconW, iconH = croppedIconImg.size     
              
            # paste updated icon
            photoImage.paste(croppedIconImg, (x, y), croppedIconImg)
            
            # clean up iconPath
            os.remove(iconPath)  
        
        return photoImage, iconW + x, iconH + y
        
    '''
    Print all text data to photo
    
    return    retVal = 0 if success
            resX, resY : x ,y of bottom right pixel of text box, useful for calculating background box
    '''
    def _printAllText(self, draw, img, xxx_todo_changeme, photoPath, fontSize = 30, fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        
        (x,y) = xxx_todo_changeme
        curTempFontSize = fontSize
        otherTempFontSize = int(fontSize / 2)
        
        _column1 = x # city name, rain/snow...
        _column2 = _column1 + 100 # icon, temp
        
        # open image & setup font
        fontCurTemp = ImageFont.truetype(fontPath, curTempFontSize)
        fontCityName = ImageFont.truetype(fontPath, curTempFontSize)
        fontOther = ImageFont.truetype(fontPath, otherTempFontSize)                
        
        # print column 1
        col1MaxX = _column1
        
        #  print city name
        draw, resX, resY = self._drawText(self.mCityName, fontCityName, draw, _column1, y)
        if (col1MaxX < resX) : col1MaxX = resX
                 
        #  print weather description
        draw, resX, resY = self._drawText(self.mWeatherDescription.capitalize(), fontOther, draw, _column1, resY + 20)
        if (col1MaxX < resX) : col1MaxX = resX
        
        #  print sunrise
        draw, resX, resY = self._drawText('Sunrise ' + self.mSunRise, fontOther, draw, _column1, resY + 10) 
        if (col1MaxX < resX) : col1MaxX = resX
        
        #  print sunset
        draw, resX, resY = self._drawText('Sunset  ' + self.mSunSet, fontOther, draw, _column1, resY + 10) 
        if (col1MaxX < resX) : col1MaxX = resX
        maxY = resY # track max of Y compared to column 2
        
        # print column 2
        if (_column2 < col1MaxX + 50): _column2 = col1MaxX + 50
        
        #  print cur temp         
        draw, resX, resY = self._drawText(str(self.mCurTemp) + '\N{DEGREE SIGN}' + 'C', fontCurTemp, draw, _column2, y)
        
        #  paste weather icon
        img, resX, iconY = self._pasteWeatherIcon(photoPath, img, _column2, resY + 20)
                 
        #  print min/max temp
        minMaxTempTxt = str(self.mMinTemp) + '/' + str(self.mMaxTemp)          
        draw, resX, resY = self._drawText( minMaxTempTxt, fontOther, draw, resX + 5, resY + 20)
        
        #  print humid
        draw, resX, resY = self._drawText( "Humid " + str(self.mHumid) + '%', fontOther, draw, _column2, resY + 10)
        
        #  print wind
        draw, resX, resY = self._drawText( "Wind " + str(self.mWindspeed) + ' m/s', fontOther, draw, _column2, resY + 10)
        
        if (resY > maxY):
            maxY = resY
        
        return 0, resX, maxY
        
    # dump object data
    def _dumpInfo(self):
        print('City: ' + self.mCityName)
        print('Temp: ' + str(self.mMinTemp) + '/' + str(self.mCurTemp) + '/' + str(self.mMaxTemp))
        print('Humid: ' + str(self.mHumid))
        print('Desc: ' + self.mWeatherDescription)
        print('Sunrise: ' + self.mSunRise)
        print('Sunset: ' + self.mSunSet)
        print('Weather icon url: ' + self.mIconUrl)
        
    # parse to class member given json response of api    
    def _parseWeatherJson(self, jsonString):
        self.mCityName = jsonString['name']
        self.mCurTemp = int(jsonString['main']['temp']) 
        self.mMaxTemp = int(jsonString['main']['temp_max'])
        self.mMinTemp = int(jsonString['main']['temp_min'])
        self.mHumid = int(jsonString['main']['humidity'])
        self.mWeatherDescription = jsonString['weather'][0]['description']
        self.mIconUrl = "http://openweathermap.org/img/w/" + str(jsonString['weather'][0]['icon']) + ".png"
        self.mSunRise = jsonString['sys']['sunrise']
        self.mSunSet = jsonString['sys']['sunset']
        
        # convert to local time
        self.mSunRise =  time.strftime('%H:%M', time.localtime(self.mSunRise))
        self.mSunSet =  time.strftime('%H:%M', time.localtime(self.mSunSet))
        
        self.mWindspeed = jsonString['wind']['speed']
        
        return self._sanityCheck()

    '''
    Check if member data makes sense such as feasible temp, alive url
    return 0 if passed
    '''
    def _sanityCheck(self):
        isGood = 31        
        isGood -= 1*(self.mCurTemp > -50) & (self.mCurTemp < 50)
        isGood -= 2*((self.mMaxTemp > -50) & (self.mMaxTemp < 50))
        isGood -= 4*((self.mMinTemp > -50) & (self.mMinTemp < 50))
        isGood -= 8*((self.mHumid >= 0) & (self.mWindspeed >= 0))
        isGood -= 16*((len(self.mSunRise) == 5) & (len(self.mSunSet) == 5))
        
        # check if icon url is alive        
        try:
            urllib.request.urlopen(self.mIconUrl)
        except Exception:
            isGood += 32
        
        self.mParseCode = isGood        
        return isGood
    
    '''
    Helper for getting api response back from openweather
    '''
    def _getJsonResponse(self, queryPart, urlName = "weather url"):
        apiUrl = 'http://api.openweathermap.org/data/2.5/' + queryPart + "&units=metric&appid=" + self.mApiKey
        print(urlName + ' ' + apiUrl)
        apiResponse = urllib.request.urlopen(apiUrl)
        return json.loads(apiResponse.read())
    
    '''
    Json weather data getter
    '''
    def _getWeatherData(self):
        defaultQuery = "weather?zip=" + str(self.mZipcode)
        
        eligibleCitiName = self.mCityName.replace("_", "%20")
        eligibleCitiName = eligibleCitiName.replace(" ", "%20")
        
        if (len(eligibleCitiName) == 0 or False == self.mZipcodeLocation.isValid()):
            # easy way first, get direct response with zipcode
            # usually inaccurate result
            return self._getJsonResponse(defaultQuery)
            
        # Now to the hard part, let's get city id from cityName
        # Find all city names here, will give a list of locations
        cityQueryResponse = self._getJsonResponse("find?q=" + eligibleCitiName + ",us&type=accurate", "city finder")
        if ('count' not in cityQueryResponse or 'list' not in cityQueryResponse):
            print('Error reading city query response, falling back to direct query')
            return self._getJsonResponse(defaultQuery)
         
        # For each city in response, get the closest to mZipcodeLocation
        cityList = cityQueryResponse['list']
        goodCity = cityList[0]
        curMinDist = 2*360*360
        for cityItem in cityList:
            lat = float(cityItem['coord']['lat'])
            lon = float(cityItem['coord']['lon'])
            goodLat = self.mZipcodeLocation.lat
            goodLon = self.mZipcodeLocation.lon
            
            dist = (lat - goodLat)**2 + (lon - goodLon)**2
            if (dist < curMinDist):
                # Found better city
                curMinDist = dist 
                goodCity = cityItem
        
        print("Found best match city " + str(cityList.index(goodCity) + 1) + "/" + str(len(cityList)))
         
        # Now get the good city data
        return self._getJsonResponse("weather?id=" + str(goodCity['id']))
    
    '''
    Main function of this class
    Add weather info to photoPath picture file
    
    x, y - top left pixel position of weather info
    
    return 0 if success , width and height of weather box
    '''
    def addWeatherToPhoto(self, photoPath, x = 540, y = 10, fontSize = 30, fontPath = 'DejaVuSans.ttf'):
        # prevent going further
        if (self.mParseCode != 0):
            return -1
        
        # check photoPath exists
        if (os.path.isfile(photoPath) == False):
            return -2
        
        # load image
        img = Image.open(photoPath).convert("RGBA")
        draw = ImageDraw.Draw(img)                 
        
        # draw text
        retVal, resX, resY = self._printAllText(draw, img, (x, y), photoPath, fontSize, fontPath)
        
        # reload image to get rid of text
        img = Image.open(photoPath).convert("RGBA")
        draw = ImageDraw.Draw(img)
                
        # add background box
        rectDraw = Image.new('RGBA', (resX - x + 20, resY - y + 20), (0,0,0,100))
        img.paste(rectDraw, (x - 10, y), rectDraw)
        
        # redraw text
        retVal, resX, resY = self._printAllText(draw, img, (x, y), photoPath, fontSize, fontPath)        
        
        # save result img
        img.convert('RGB').save(photoPath)
        
        return retVal, resX - x, resY -y

##########################################################################
# unit test area
##########################################################################
class TestWeatherPrinter(unittest.TestCase):

    def test_api_exist(self):
        apiKeyFile = 'api.key'
        
        if (os.path.isfile(apiKeyFile) != True):
            print(" Error: " + apiKeyFile + " not exists")
            print(" Perhaps you may need to register a free key with https://openweathermap.org/price")
            print(" and put the key inside " + apiKeyFile + " file on the same directory as this unit test script")
            sys.exit(1)

    def test_info_success(self):        
        losAngeles = WeatherCity(90089)
        lagunaHills = WeatherCity(92653)
        self.assertEqual(losAngeles.mParseCode, 0)
        self.assertEqual(lagunaHills.mParseCode, 0)
        
        self.assertEqual(losAngeles.mCityName, 'Los Angeles')
        self.assertEqual(lagunaHills.mCityName, 'Laguna Hills')
        
    # get current city info
    def test_get_current_city(self):
        curCity = WeatherCity()
        self.assertEqual(curCity.mParseCode, 0)
        self.assertGreater(len(curCity.mCityName), 0)
        self.assertTrue(curCity.mZipcodeLocation.isValid())
        
    # this doesn't require bingwall
    def test_print_blankpicture(self):
        # create test image
        testImage = 'image2.jpg'
        img = Image.new('RGB', (1920, 1080), "white")
        img.save(testImage)
        
        # get test weather info
        losAngeles = WeatherCity(90089)
        retVal, w, h = losAngeles.addWeatherToPhoto(testImage, fontSize=50)
        self.assertEqual(retVal, 0)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)
    
    # comprehensive test, requires functional bingwall
    # the reason for this is that I can't test bingwall directly, so this is more like integration test
    def test_print_picture_withbingwall(self):
        testImage = 'image.jpg'        
        bingwallFile = 'bingwall.py'
        
        # download test image
        downloadSuccess = os.system('python ' + bingwallFile + ' -p ' + testImage + '>/dev/null')        
        self.assertEqual(downloadSuccess, 0)
        
        # print weather info
        losAngeles  = WeatherCity(90089)
        retVal, w, h = losAngeles.addWeatherToPhoto(testImage, fontSize=50)
        self.assertEqual(retVal, 0)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)
        print("Check out weather info in " + testImage)
    
if __name__ == '__main__':
    unittest.main()
