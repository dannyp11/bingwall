'''
Created on Aug 6, 2017

@author: danny
'''

import os.path, sys, time
import unittest, textwrap
import urllib2, json, urllib

from PIL import ImageFont, Image, ImageDraw

class BingWallpaper(object):
    '''
    This class will download Bing photo of the day
    Then it will figure out caption & description and put 
    those info onto the image nicely
    
    The caption & description adders are best effort attemps,
    meaning that if it can't parse, it will save the image anyway
    '''


    def __init__(self, imgPath = "/tmp/image.jpg", 
                 fontPath = 'DejaVuSans.ttf'):
        '''
        Constructor
        '''
        self.url = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-AU"
        self.captionText = ""
        self.descriptionText = ""
        self.descriptionLink = ""
        self.addDescription = False
        self.addCaption = False
        self.imgPath = imgPath
        self.fontPath = fontPath
                    
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
        try:
            urllib2.urlopen(imgLink)
        except urllib2.HTTPError:
            ++retVal
        except urllib2.URLError:
            ++retVal
        
        if (0 == retVal):
            urllib.urlretrieve(imgLink, self.imgPath)
            # imgPath has to exist from here now
            if (os.path.isfile(self.imgPath) == 0):
                ++retVal          
        
        # some more sanity check
        
        
        # for debug purpose
        print json.dumps(data, indent=4, sort_keys=True)
        
        return retVal
    
    '''
    Draw white text with black outline
    
    text - input
    font - font
    draw - draw object
    x, y - upperleft position of text
    fillcolor - color of text, default: white
    '''
    def _drawText(self, text, font, draw, x , y, fillColor = (255, 255, 255, 255)):
        shadowcolor = (0,0,0,255)
        
        # thicker border, draw stroke
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor)
        
        # now draw the text over it
        draw.text((x, y), text, font=font, fill=fillColor)
        
        return draw
    
    '''
    Put caption to image    
    '''
    def ParseCaption(self):
        result = 0
        self.addCaption = True
        return result
    
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
        
        # strip title out of copyright portion
        strDelimiter = " ("
        caption_index = self.captionText.find(strDelimiter)    
        caption =  self.captionText[0:caption_index]
        
        # load url
        webpage = ""
        try:
            webpage = urllib2.urlopen(self.descriptionLink)
        except urllib2.HTTPError:
            result = 1
        except urllib2.URLError:
            result = 1
        
        if (result != 0):
            return result    
        
        dataRaw = webpage.read()
        data = dataRaw.decode('utf-8')
        
        # query caption to find description
        query_start = "<h2 class=\"\">" + caption + "</h2></div><div>"
        query_start2 = "</h2></div><div>" # backup if query_start return invalid
        query_stop = "</div>"
    
        #print query_start
    
        found = data.find(query_start)
        index_start = found + len(query_start)
        index_stop = data.find(query_stop, index_start)
    
        # 2nd try
        if (index_stop > index_start + 10000):
            found = data.find(query_start2)
            index_start = found + len(query_start2)
            index_stop = data.find(query_stop, index_start)
    
        # check if we still get garbage
        if (index_stop > index_start + 10000):
            self.descriptionText = ''
            result = 3
        else:
            self.descriptionText = data[index_start: index_stop]
    
        # save data for debugging
        dataFile = open('/tmp/data.bing','w')
        dataFile.write(dataRaw)
        dataFile.close()
    
        return result
    
    '''
    Print caption and description on image
    return image, text_height in pixel
    '''
    def _printAllText(self, image):
        # if draw nothing, return for best performance
        if ((False == self.addCaption or 0 == len(self.captionText)) and False == self.addDescription):
            return image, 0
        
        # format text
        fontSize = 20
        fontSizeDescription = fontSize - 2;
            
        # open input
        font = ImageFont.truetype(self.fontPath, fontSize)
        fontDescription = ImageFont.truetype(self.fontPath, fontSizeDescription)
        img = image
        imgW, imgH = img.size
        draw = ImageDraw.Draw(img)    
        
        # determine text box size
        charLimiter = 50
        strDelimiter = "("
        
        caption_lines = self.captionText.split(strDelimiter)
        caption_lines[-1] = "(" + caption_lines[-1]            
        
        description_lines = 0
        y_text = fontSize + 2
        
        # draw description
        if (0 != len(self.descriptionText) and True == self.addDescription):
            description_lines = textwrap.wrap(self.descriptionText, charLimiter * 3)
        
            y_text = fontSizeDescription + 5    
            if (description_lines != 0):
                for line in reversed(description_lines):
                    txtW, txtH = draw.textsize(line, fontDescription) # get text size on draw
                    width, height = fontDescription.getsize(line) # get 1 character size
                    draw = self._drawText(line, fontDescription, draw, imgW - txtW - 5, imgH - y_text)
                    y_text += txtH + 2
                    
                y_text += 5    
            else:
                y_text = fontSize + 5
        
        # draw caption
        if (True == self.addCaption):
            height = -1
            for line in reversed(caption_lines):
                txtW, txtH = draw.textsize(line, font) # get text size on draw
                width, height = font.getsize(line) # get 1 character size
                draw = self._drawText(line, font, draw, imgW - txtW - 5, imgH - y_text)
                y_text += height
            y_text -= height
        
        return img, y_text
    
    '''
    Add caption & description to image if found
    
    inputImg : path to input
    outputImg: path to output
    fontPath : path to dejavu font
    description: optional description to print
    '''
    def ExportImage(self, outputImg = 0):    
        
        result = 0
        
        # load image    
        img = Image.open(self.imgPath)
        
        # draw text first
        img, y_text = self._printAllText(img)    
        
        # reload image to get rid of text
        img = Image.open(self.imgPath)
        imgW, imgH = img.size
        
        # draw background box
        rectDraw = Image.new('RGBA', (imgW, y_text), (0,0,0,80))
        img.paste(rectDraw, (0, imgH - y_text), rectDraw)    
        
        # draw text again
        img, y_text = self._printAllText(img)
        
        # save img
        if (outputImg != 0):
            img.save(outputImg)
        else:
            img.save(self.imgPath)
        
        return result

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
        wallpaper = BingWallpaper(self.__class__.imgPath)
        self.assertEqual(0, wallpaper.dlResultCode)
        self.assertEqual(0, wallpaper.ParseDescription())
        self.assertEqual(0, wallpaper.ParseCaption())
        self.assertEqual(0, wallpaper.ExportImage('img2.jpg'))
        
if __name__ == '__main__':
    unittest.main()