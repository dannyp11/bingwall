'''
Created on Aug 6, 2017

@author: danny
'''

import unittest
import urllib2, json, urllib
from bs4 import BeautifulSoup
import re

from PhotoProcessor import PhotoProcessor

class BingWallpaper(object):
    '''
    This class will download Bing photo of the day
    Then it will figure out caption & description and put 
    those info onto the image nicely
    
    The caption & description adders are best effort attemps,
    meaning that if it can't parse, it will save the image anyway
    '''


    def __init__(self, imgPath = "/tmp/image.jpg", 
                 fontPath = 'DejavuSans.ttf'):
        '''
        Constructor
        '''
        self.url = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
        self.captionText = ""
        self.descriptionText = ""
        self.descriptionLink = ""
        self.addDescription = False
        self.addCaption = False
        self.imgPath = imgPath
        self.fontPath = fontPath
        self.photoProcessor = PhotoProcessor(imagePath=imgPath)
        self.photoProcessor._setFontPath(fontPath)

        self.dlResultCode = self._downloadWallpaper()
        
    '''
    Most crucial function, it will try downloading the image from Bing.com
    '''
    def _downloadWallpaper(self):
        retVal = 0
        
        # get json from bing api
        response = urllib.urlopen(self.url)        
        data = json.loads(response.read())
        imgLink = "http://bing.com" +  data["images"][0]["url"]
        
        # parse for later use 
        self.descriptionLink = data["images"][0]["copyrightlink"]
        self.captionText = data["images"][0]["copyright"]
        
        # try to download image
        self.photoProcessor._setPhotoUrl(imgLink)
        retVal += self.photoProcessor.dlResultCode       
        
        # for debug purpose
        print json.dumps(data, indent=4, sort_keys=True)
        
        return retVal
    
    '''
    Put caption to image    
    '''
    def ParseCaption(self):
        self.addCaption = True
        return self.photoProcessor._setCaption(self.captionText)
    
    '''
    Get description of image given bing link and image title
    return: 0 on success
    '''
    def ParseDescription(self):
        result = 0
        self.addDescription = True
        
        # check if description url is valid
        if (0 == len(self.descriptionLink)):
            return 1
        
        # load url
        webpage = ""
        try:
            webpage = urllib2.urlopen(self.descriptionLink)
        except urllib2.HTTPError:
            result = 1
        except urllib2.URLError:
            result = 2
        
        if (result != 0):
            return result
        
        # convert data to bs format
        bsData = BeautifulSoup(webpage.read().decode('utf-8'), 'lxml')
        descSection = bsData.find('div', {'class': 'b_vPanel'})
        if (descSection is None):
            return 3        
        
        descSection = descSection.find('div')
        if (descSection is None):
            return 4
        
        # traverse thru div list
        descSection = descSection.nextSibling
        descSection = descSection.nextSibling
        descSection = descSection.nextSibling
        
        if (len(str(descSection)) > 30):
            self.descriptionText = str(descSection.prettify().encode('unicode-escape')).decode('unicode-escape')
            
            # strip xml tag
            self.descriptionText = re.sub('<[^>]*>', '', self.descriptionText)
            
            if (len(self.descriptionText) < 30):
                result = 6
            
        else:
            result = 5
            
        # save data for debugging
        dataFile = open('/tmp/data.bing','w')
        dataFile.write(bsData.prettify(encoding='utf-8'))
        dataFile.close()
        
        descFile = open('/tmp/descData.bing','w')
        descFile.write(bsData.find('div', {'class': 'b_vPanel'}).prettify(encoding='utf-8'))
        descFile.close()
        
        if (0 == result):
            return self.photoProcessor._setDescription(self.descriptionText)
        
        return result
    
    '''
    Add caption & description to image if found
    
    outputImg: path to output
    offsetPixels: y-offset for caption/description, useful for bottom taskbar
    '''
    def ExportImage(self, outputImg = 0, offsetPixels = 0):
        return self.photoProcessor.ExportImage(outputImg, offsetPixels)

# Unit test area ##################################################################################
###################################################################################################

class TestBingWallpaper(unittest.TestCase):

    imgPath = 'image.jpg'

    def test_download_image(self):        
        wallpaper = BingWallpaper(self.__class__.imgPath)
        self.assertEqual(0, wallpaper.dlResultCode)
    
    def test_addCaption(self):
        wallpaper = BingWallpaper(self.__class__.imgPath)
        self.assertEqual(0, wallpaper.dlResultCode)
        self.assertEqual(0, wallpaper.ParseCaption())
    
    def test_addDescription(self):
        wallpaper = BingWallpaper(self.__class__.imgPath)
        self.assertEqual(0, wallpaper.dlResultCode)
        self.assertEqual(0, wallpaper.ParseDescription())
        
    def test_addBoth(self):
        wallpaper = BingWallpaper(self.__class__.imgPath)
        self.assertEqual(0, wallpaper.dlResultCode)
        self.assertEqual(0, wallpaper.ParseDescription())
        self.assertEqual(0, wallpaper.ParseCaption())    
        
    def test_comprehensive(self):
        wallpaper = BingWallpaper('img.jpg', fontPath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.assertEqual(0, wallpaper.dlResultCode)
        self.assertEqual(0, wallpaper.ParseDescription())
        self.assertEqual(0, wallpaper.ParseCaption())
        self.assertEqual(0, wallpaper.ExportImage('img2.jpg'))
    
    def test_comprehensiveOffset(self):
        wallpaper = BingWallpaper(self.__class__.imgPath, fontPath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.assertEqual(0, wallpaper.dlResultCode)
        self.assertEqual(0, wallpaper.ParseDescription())
        self.assertEqual(0, wallpaper.ParseCaption())
        self.assertEqual(0, wallpaper.ExportImage('img3.jpg', 100))
        
if __name__ == '__main__':
    unittest.main()
