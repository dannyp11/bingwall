'''
Created on Jun 27, 2017

@author: danny
'''

import os.path, sys, time
import unittest
import urllib2, json, urllib

from PIL import ImageFont, Image, ImageDraw

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
    mSunRise = -1
    mSunSet = -1
    mHumid = -1
    mWindspeed = -1
    
    def __init__(self, zipcode, keyFile = 'api.key'):
        self.mApiKey = getApiKey(keyFile)
        self.mZipcode = zipcode

        if (self.mApiKey == -1 or self._isInternetOn() == False):
            print "Error creating WeatherCity object for " + str(zipcode) + ":",
            if (self.mApiKey == -1):
                print "invalid apikey file " + keyFile
            else:
                print " no internet connection"
            return
        
        # build api call
        apiUrl = "http://api.openweathermap.org/data/2.5/weather?zip=" + str(zipcode)  +  ",us&units=metric&appid=" + self.mApiKey
        print "weather url " + apiUrl
        
        apiResponse = urllib2.urlopen(apiUrl)
        resultJson = json.loads(apiResponse.read())
        # for debug purpose
        print json.dumps(resultJson, indent=4, sort_keys=True)
                
        if (0 != self.parseWeatherJson(resultJson)):
            print "Error parsing WeatherCity object for " + str(zipcode)
            return
        
    '''
    Check if internet is on
    '''
    def _isInternetOn(self):
        googleUrl = 'http://216.58.192.142'
    
        try:
            urllib2.urlopen(googleUrl, timeout=1)
            return True
        except urllib2.URLError: 
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
        
        urllib.urlretrieve(self.mIconUrl, iconPath)        
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
        
    # parse to class member given json response of api    
    def parseWeatherJson(self, jsonString):
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
        isGood &= (self.mHumid >= 0) & (self.mWindspeed >= 0)
        isGood &= (len(self.mSunRise) == 5) & (len(self.mSunSet) == 5)
        
        # check if icon url is alive        
        try:
            urllib2.urlopen(self.mIconUrl)
        except Exception:
            isGood = False
        
        self.mParseCode = not isGood        
        return (not isGood)
    
    '''
    Main function of this class
    Add weather info to photoPath picture file
    
    x, y - top left pixel position of weather info
    
    return 0 if success 
    '''
    def addWeatherToPhoto(self, photoPath, x = 540, y = 10, fontSize = 30, fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        retVal = 0
        
        # prevent going further
        if (self.mParseCode != 0):
            return -1
        
        # check photoPath and fontPath exists
        if (os.path.isfile(photoPath) == False or os.path.isfile(fontPath) == False):
            return -2
        
        curTempFontSize = fontSize
        otherTempFontSize = fontSize / 2
        
        _column1 = x # city name, rain/snow...
        _column2 = _column1 + 100 # icon, temp
        
        # open image & setup font
        fontCurTemp = ImageFont.truetype(fontPath, curTempFontSize)
        fontCityName = ImageFont.truetype(fontPath, curTempFontSize)
        fontOther = ImageFont.truetype(fontPath, otherTempFontSize)
        img = Image.open(photoPath)
        draw = ImageDraw.Draw(img)                         
        
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
        
        # print column 2
        if (_column2 < col1MaxX + 50): _column2 = col1MaxX + 50
        
        #  print cur temp         
        draw, resX, resY = self._drawText(str(self.mCurTemp) + u'\N{DEGREE SIGN}' + 'C', fontCurTemp, draw, _column2, y)
        
        #  paste weather icon
        img, resX, iconY = self._pasteWeatherIcon(photoPath, img, _column2, resY + 20)
                 
        #  print min/max temp
        minMaxTempTxt = str(self.mMinTemp) + '/' + str(self.mMaxTemp)          
        draw, resX, resY = self._drawText( minMaxTempTxt, fontOther, draw, resX + 5, resY + 20)
        
        #  print humid
        draw, resX, resY = self._drawText( "Humid " + str(self.mHumid) + '%', fontOther, draw, _column2, resY + 10)
        
        #  print wind
        draw, resX, resY = self._drawText( "Wind " + str(self.mWindspeed) + ' m/s', fontOther, draw, _column2, resY + 10)
        
        # save result img
        img.save(photoPath)
        
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
        chaska = WeatherCity(55318)
        lagunaHills = WeatherCity(92653)
        self.assertEqual(chaska.mParseCode, 0)
        self.assertEqual(lagunaHills.mParseCode, 0)
        
        self.assertEqual(chaska.mCityName, 'Chaska')
        self.assertEqual(lagunaHills.mCityName, 'Laguna Hills')
        
    # require Internet on
    def test_print_picture(self):
        testImage = 'image.jpg'        
        bingwallFile = 'bingwall.py'
        
        # download test image
        downloadSuccess = os.system('python ' + bingwallFile + ' -p ' + testImage + '>/dev/null')        
        self.assertEqual(downloadSuccess, 0)
        
        # print weather info
        chaska  = WeatherCity(55318)
        self.assertEqual(chaska.addWeatherToPhoto(testImage, fontSize=50), 0)
        print "Check out weather info in " + testImage
        
        
if __name__ == '__main__':
    unittest.main()