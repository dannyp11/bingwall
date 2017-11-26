#!/usr/bin/env python

import urllib2
import getopt, sys, os, shutil

import WeatherPrinter, BingWallpaperDownloader
from FunfactPrinterManager import FunFactManager, FunFactMode

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
    funFact = FunFactManager(mode, fontPath)
    if (0 != funFact.mResultCode):
        print 'Error code ' + str(funFact.mResultCode) + ' initing funfact manager'
        return -1
    
    # debug message
    funFact.dumpInfo()
    
    # print data
    result = funFact.exportToImage(photoPath)
    if (0 != result):
        print 'Error code ' + str(result) + ' exporting funfact to ' + photoPath
        return -2
    
    return 0

'''
Print weather info with zipcode 
Requires api key from openweathermap.org

zipcode    - city zipcode
apiKeyPath - path to api key
photoPath  - path to photo that needs weather info printed on
fontPath   - path to font file

return  retVal, width, height, x, y of weather box   
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
    
    return weatherCity.addWeatherToPhoto(photoPath, x, y, 40, fontPath), x, y   

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
    
    # build fun fact mgr object
    funFactMgr = FunFactManager(funFactMode, fontPath)
    if (0 != funFactMgr.mResultCode):
        print 'Error code ' + str(funFactMgr.mResultCode) + ' initing funfact manager'
    
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
    exportResult, y_description = wallpaper.ExportImage(outputImg, offsetPix) 
    if (exportResult == 0):
        # rm input, change output as input name
        os.remove(inputImg)
        shutil.move(outputImg, inputImg)
        
        # update fun fact manager obstacle set
        funFactMgr.addObstacleBox((0, 1080 - y_description, 1920, y_description))
    else:
        print "Error: can't export image " + str(outputImg)                                        
    
    # add weather info
    weatherWidth = weatherHeight = 0
    if (result == 0 and addWeather == 1):
        if (weatherX >= 0 and weatherY >= 0):
            (result, weatherWidth, weatherHeight), weatherX, weatherY = WeatherAdder(weatherZipcode, apiKeyPath, inputImg, fontPath, (weatherX, weatherY))
        else:
            (result, weatherWidth, weatherHeight), weatherX, weatherY = WeatherAdder(weatherZipcode, apiKeyPath, inputImg, fontPath)
        
        if (result != 0):
            print 'Error code ' + str(result) + ' printing weather to ' + imgPath
        else:
            # update fun fact manager obstacle set
            funFactMgr.addObstacleBox((weatherX, weatherY, weatherWidth, weatherHeight))
    
    # add fact of the day
    if (funFactMode != FunFactMode.OFF):
        # debug message
        funFactMgr.dumpInfo()
        
        # print data
        result = funFactMgr.exportToImage(imgPath)
        if (0 != result):
            print 'Error code ' + str(result) + ' exporting funfact to ' + imgPath
            result = 0 # still process even though fun fact parser fails
    
    # make sure img is there
    if (False == os.path.isfile(imgPath)):
        print 'Error: final image ' + imgPath + ' not exists'
        result = -1
    
    if (result == 0):
        print "Successfully saved " + imgPath
    else:
        print "Error code " + str(result)
        
    return result

if __name__ == "__main__":
    main()
