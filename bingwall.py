#!/usr/bin/env python

import urllib2
import getopt, sys, os, shutil

import WeatherPrinter, WallpaperDownloader

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
Print weather info with zipcode 
Requires api key from openweathermap.org

zipcode    - city zipcode
apiKeyPath - path to api key
photoPath  - path to photo that needs weather info printed on
fontPath   - path to font file

return    0  on success
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
def usage():
    print "Usage: python " + (sys.argv[0]) + " OPTION [VALUE]"
    print "    -p {path}         where to save the image, default " + imgPath
    print "    -c                add caption to image" 
    print "    -d                add description to image" 
    print "    -f {fontPath}     path to text font for caption & description. This will also trigger -c, default " + fontPath
    print "    -w {zipcode}      turn on weather feature, must also use -k option"
    print "    -k {api.key path} path to api key file for http://openweathermap.org/appid, must also use -w"
    print "    -x {top left x}   topleft x pixel of weather info (optional)"
    print "    -y {top left y}   topleft y pixel of weather info (optional)"    

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
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:hdcf:w:k:x:y:', ['path=','help'])
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
            
    # check internet
    if (isInternetOn() == False):
        print "Internet is off"
        return 1
    
    # check if weather option is chosen
    if (apiKeyPath != 0 and weatherZipcode > 0):
        addWeather = 1
    
    # build wallpaperDownloader object
    wallpaper = WallpaperDownloader.BingWallpaper(imgPath, fontPath)
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
    if (wallpaper.ExportImage(outputImg) == 0):
        # rm input, change output as input name
        os.remove(inputImg)
        shutil.move(outputImg, inputImg)                                        
    
    # add weather info
    if (result == 0 and addWeather == 1):
        if (weatherX >= 0 and weatherY >= 0):
            result = WeatherAdder(weatherZipcode, apiKeyPath, inputImg, fontPath, (weatherX, weatherY))
        else:
            result = WeatherAdder(weatherZipcode, apiKeyPath, inputImg, fontPath)
    
    if (result == 0):
        print "Successfully saved " + imgPath
    else:
        print "Error code " + str(result)
        
    return result

if __name__ == "__main__":
    main()
