#!/usr/bin/env python

import urllib2
import getopt, sys, os, shutil

import WeatherPrinter, BingWallpaperDownloader, FunFactPrinter
from enum import Enum
from random import randint

'''
Check if internet is on
'''
def isInternetOn():
    googleUrl = 'http://216.58.192.142'

    try:
        urllib2.urlopen(googleUrl, timeout=1)
        return True
    except urllib2.URLError: 
        return False

# Different modes for fun fact of the day option
class FunFactMode(Enum):
    OFF = 0
    TEXT_BOX = 1
    SCATTER = 2

'''
Check if 2 boxes intersect
Input: (box1), (box2)
        box info: top left x/y and width, height
'''
def isBoxIntersect((x1, y1, w1, h1),(x2, y2, w2, h2)):
    retVal = True
    
    maxX1 = x1 + w1
    maxY1 = y1 + h1
    maxX2 = x2 + w2
    maxY2 = y2 + h2
    
    retVal &= not (maxX1 < x2)
    retVal &= not (x1 > maxX2)
    retVal &= not (maxY1 < y2)
    retVal &= not (y1 > maxY2)
    
    return retVal

'''
Add fun fact of the day to image
Mode:
    TEXT_BOX: save everything in 1 textbox
    SCATTER:  randomly put various messages throughout the image
    
return    0 on success
          -1 on failed parsing of data
          -2 on failed saving photo
          -3 on invalid mode
'''
def FunFactAdder(photoPath, fontPath, mode=FunFactMode.OFF):
    # first we make sure mode isn't off
    if (FunFactMode.OFF == mode):
        # do nothing
        return 0
    
    # create funfact printer object
    funFact = FunFactPrinter.FunFactPrinter()
    if (funFact.mParseCode != 0):
        print 'Error code ' + str(funFact.mParseCode) + ' parsing fact of the day'
        return -1
    
    funFact.dumpInfo()
    
    if (FunFactMode.TEXT_BOX == mode):
        retVal = funFact.printAllToPhoto(photoPath, 50, 600, 25, fontPath)
        if (retVal != 0):
            print 'Error code ' + str(retVal) + ' printing textbox fun fact'
            return -2
    
    elif (FunFactMode.SCATTER == mode):
        retValOverall = 0
        
        # generate random text smart locations
        minX = 10
        minY = 30
        maxX = 1920
        maxY = 700
        minFontSize = 20
        maxFontSize = 25
        
        # get metrics of textboxes first
        fontSizeThought = randint(minFontSize, maxFontSize)
        fontSizeIdea = randint(minFontSize, maxFontSize)
        fontSizeFact = randint(minFontSize, maxFontSize)
        fontSizeJoke = randint(minFontSize, maxFontSize)
        
        retVal, thoughtW, thoughtH = funFact.printThought(photoPath, 0, 0, fontSizeThought, fontPath, True)
        retVal, ideaW, ideaH = funFact.printThought(photoPath, 0, 0, fontSizeIdea, fontPath, True)
        retVal, factW, factH = funFact.printThought(photoPath, 0, 0, fontSizeFact, fontPath, True)
        retVal, jokeW, jokeH = funFact.printThought(photoPath, 0, 0, fontSizeJoke, fontPath, True)
        
        # print thought
        tmpMaxX = -1
        xThought = yThought = -1
        while (tmpMaxX < minX):
            tmpMaxX = maxX - thoughtW - 10
            yThought = randint(minY, maxY)
            if (yThought < 400): # update maxX because this conflicts with weather text box
                tmpMaxX -= 500
                
        xThought = randint(minX, tmpMaxX)
        shouldPrint = randint(0, 1)
        retVal, resX, resY = funFact.printThought(photoPath, xThought, yThought, fontSizeThought, fontPath, shouldPrint)
        retValOverall += retVal
        
        # print idea
        xIdea = yIdea = -1
        while (True):
            tmpMaxX = maxX - ideaW - 10
            yIdea = randint(minY, maxY)
            if (yIdea < 400): # update maxX because this conflicts with weather text box
                tmpMaxX -= 500

            if (tmpMaxX < minX):
                continue
                        
            xIdea = randint(minX, tmpMaxX)
            # avoid thought box
            if (True == isBoxIntersect((xIdea, yIdea, ideaW, ideaH), (xThought, yThought, thoughtW, thoughtH))):
                continue
            break
            
        shouldPrint = randint(0, 1)
        retVal, resX, resY = funFact.printIdea(photoPath, xIdea, yIdea, fontSizeIdea, fontPath, shouldPrint)
        retValOverall += retVal
        
        # print joke
        xJoke = yJoke = -1
        while (True):
            tmpMaxX = maxX - jokeW - 10
            yJoke = randint(minY, maxY)
            if (yJoke < 400): # update maxX because this conflicts with weather text box
                tmpMaxX -= 500

            if (tmpMaxX < minX):
                continue
                        
            xJoke = randint(minX, tmpMaxX)
            # avoid thought box
            if (True == isBoxIntersect((xJoke, yJoke, jokeW, jokeH), (xThought, yThought, thoughtW, thoughtH))):
                continue
            
            # avoid idea box
            if (True == isBoxIntersect((xJoke, yJoke, jokeW, jokeH), (xIdea, yIdea, ideaW, ideaH))):
                continue
            break
        
        shouldPrint = randint(0, 1)
        retVal, resX, resY = funFact.printJoke(photoPath, xJoke, yJoke, fontSizeJoke, fontPath, shouldPrint)
        retValOverall += retVal
        
        # print fact
        xFact = yFact = -1
        while (True):
            tmpMaxX = maxX - factW - 10
            yFact = randint(minY, maxY)
            if (yFact < 400): # update maxX because this conflicts with weather text box
                tmpMaxX -= 500

            if (tmpMaxX < minX):
                continue
                        
            xFact = randint(minX, tmpMaxX)
            # avoid thought box
            if (True == isBoxIntersect((xFact, yFact, factW, factH), (xThought, yThought, thoughtW, thoughtH))):
                continue
            
            # avoid idea box
            if (True == isBoxIntersect((xFact, yFact, factW, factH), (xIdea, yIdea, ideaW, ideaH))):
                continue
            
            # avoid joke box
            if (True == isBoxIntersect((xFact, yFact, factW, factH), (xJoke, yJoke, jokeW, jokeH))):
                continue
            break        

        shouldPrint = randint(0, 1)
        retVal, resX, resY = funFact.printFact(photoPath, xFact, yFact, fontSizeFact, fontPath, shouldPrint)
        retValOverall += retVal
        
        if (retValOverall != 0):
            return -2
        
    else:
        return -3
    
    return 0

'''
Print weather info with zipcode 
Requires api key from openweathermap.org

zipcode    - city zipcode
apiKeyPath - path to api key
photoPath  - path to photo that needs weather info printed on
fontPath   - path to font file

return  retVal, width, height of weather box   
        retVal: 
           0  on success
          -1 on invalid key
          -2 on invalid zipcode
          -3 on fail getting weather info
'''
def WeatherAdder(zipcode, apiKeyPath, photoPath, fontPath, (x,y) = (1450,200)):    
    # invalid api key
    if (os.path.isfile(apiKeyPath) == False):
        return "Error " + apiKeyPath + " not found"
    
    # invalid zipcode, quick n dirty check
    if (int(zipcode) < 501 or int(zipcode) > 99950):
        return "Error " + str(zipcode) + " is invalid zipcode"
    
    # create weather printer object
    weatherCity = WeatherPrinter.WeatherCity(zipcode, apiKeyPath)
    
    if (weatherCity.mParseCode != 0):
        return "Error code " + str(weatherCity.mParseCode) + " parsing weather info"
    
    return weatherCity.addWeatherToPhoto(photoPath, x, y, 40, fontPath)        

imgPath = '/tmp/image.jpg'
fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
addDescription = 0
offsetPix = 0
def usage():
    print "Usage: python " + (sys.argv[0]) + " OPTION [VALUE]"
    print "   Common options:"
    print "    -p {path}         where to save the image, default " + imgPath
    print "    -f {fontPath}     path to text font for everything, default " + fontPath
    print ""
    print "   Photo of the day options:"
    print "    -c                add caption to image" 
    print "    -d                add description to image" 
    print ""
    print "   Weather options:"
    print "    -w {zipcode}      turn on weather feature, must also use -k option"
    print "    -k {api.key path} path to api key file for http://openweathermap.org/appid, must also use -w"
    print "    -x {top left x}   topleft x pixel of weather info (optional)"
    print "    -y {top left y}   topleft y pixel of weather info (optional)"
    print "    -o {offset}       offset pixels from bottom for caption/description, default: " + str(offsetPix)
    print ""
    print "   Fun X of the day options:"
    print "    -a {mode}         optional fun fact/joke/quote/idea of the day to image, mode: 0(text box), 1(scatter)"

def main():    
    
    result = 0
    apiKeyPath = 0
    weatherZipcode = 0
    imgPath = '/tmp/image.jpg'
    fontPath = 'DejaVuSans.ttf'
    addCaption = 0
    addDescription = 0   
    addWeather = 0
    weatherX = -1
    weatherY = -1
    offsetPix = 0
    funFactMode = FunFactMode.OFF
        
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:hdcf:w:k:x:y:o:a:', ['path=','help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-p', '--path='):
            imgPath = arg
        elif opt in ('-f'):
            fontPath = arg                            
        elif opt in ('-d'):
            addDescription = 1
        elif opt in ('-c'):
            addCaption = 1
        elif opt in ('-k'):
            apiKeyPath = arg
        elif opt in ('-w'):
            weatherZipcode = arg
        elif opt in ('-x'):
            weatherX = int(arg)
        elif opt in ('-y'):
            weatherY = int(arg)
        elif opt in ('-o'):
            offsetPix = int(arg)
            if (offsetPix < 0):
                offsetPix = 0
        elif opt in ('-a'):
            funFactMode = FunFactMode(int(arg) + 1)
            
    # check internet
    if (isInternetOn() == False):
        print "Internet is off"
        return 1
    
    # check if weather option is chosen
    if (apiKeyPath != 0 and weatherZipcode > 0):
        addWeather = 1
    
    # build wallpaperDownloader object
    wallpaper = BingWallpaperDownloader.BingWallpaper(imgPath, fontPath)
    if (0 != wallpaper.dlResultCode):
        print 'Error code ' + str(wallpaper.dlResultCode) + ' getting wallpaper' 
        return 2
    
    # add description to image        
    if (addDescription == 1):        
        resultDesc = wallpaper.ParseDescription()
        if (0 != resultDesc):
            print 'Error code ' + str(resultDesc) + ' parsing description'
    
    # add caption to image
    if (addCaption == 1):
        result = wallpaper.ParseCaption()
        if (0 != result):
            print 'Error code ' + str(resultDesc) + ' parsing caption'
            # we return because caption is a must-ok for bing image
            return result
    
    inputImg = imgPath
    outputImg = "/tmp/bing-wall-output.jpg"  
    
    # now we can export caption & description to image
    if (wallpaper.ExportImage(outputImg, offsetPix) == 0):
        # rm input, change output as input name
        os.remove(inputImg)
        shutil.move(outputImg, inputImg)
    else:
        print "Error: can't export image " + str(outputImg)                                        
    
    # add weather info
    weatherWidth = weatherHeight = 0
    if (result == 0 and addWeather == 1):
        if (weatherX >= 0 and weatherY >= 0):
            result, weatherWidth, weatherHeight = WeatherAdder(weatherZipcode, apiKeyPath, inputImg, fontPath, (weatherX, weatherY))
        else:
            result, weatherWidth, weatherHeight = WeatherAdder(weatherZipcode, apiKeyPath, inputImg, fontPath)
        
        if (result != 0):
            print 'Error code ' + str(result) + ' printing weather to ' + imgPath
    
    # add fact of the day
    if (funFactMode != FunFactMode.OFF):
        result = FunFactAdder(inputImg, fontPath, funFactMode)
        if (result != 0):
            print 'Error code ' + str(result) + ' adding fun fact to ' + imgPath
    
    if (result == 0):
        print "Successfully saved " + imgPath
    else:
        print "Error code " + str(result)
        
    return result

if __name__ == "__main__":
    main()
