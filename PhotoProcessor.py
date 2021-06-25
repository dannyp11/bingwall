import os.path
import unittest, textwrap
import urllib.request, urllib.error, urllib.parse, urllib.request, urllib.parse, urllib.error

from PIL import ImageFont, Image, ImageDraw

'''
Base image downloader & processing class
This will download image, put caption & description if passed
 and export to given path

This class should be inherited
'''
class PhotoProcessor:
    def __init__(self, photoUrl = 0, imagePath = 0):
        self.photoUrl = photoUrl
        self.captionText = ''
        self.descriptionText = ''
        self.fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        self.imgPath = '/tmp/image.jpg'
        self.dlResultCode = 1
        
        if ( 0 != imagePath):
            self.imgPath = imagePath
                            
        if (photoUrl != 0):
            self.dlResultCode = self._downloadImage()
    
    # protected setter methods
    def _setPhotoUrl(self, url = 0):        
        if (url != 0):
            self.photoUrl = url
            self.dlResultCode = self._downloadImage()
            return self.dlResultCode
        else:
            return 1
    
    def _setFontPath(self, fontPath = 0):        
        if (fontPath != 0):
            self.fontPath = fontPath
            return 0
        else:
            return 1
    
    def _setCaption(self, captionText = 0):        
        if (captionText != 0):
            self.captionText = captionText
            return 0
        else:
            return 1
        
    def _setDescription(self, descriptionText = 0):        
        if (descriptionText != 0):
            self.descriptionText = descriptionText
            return 0
        else:
            return 1
    
        
    '''
    Add caption & description to image if found
    
    outputImg: path to output
    offsetPixels: y-offset for caption/description, useful for bottom taskbar
    
    return result = 0 if success
            y_text: top left y of result image
    '''
    def ExportImage(self, outputImg = 0, offsetPixels = 0):   
        result = 0
        
        # load image    
        img = Image.open(self.imgPath)
        
        # draw text first
        img, y_text = self._printAllText(img, offsetPixels)    
        
        # reload image to get rid of text
        img = Image.open(self.imgPath)
        imgW, imgH = img.size
        
        # draw background box
        rectDraw = Image.new('RGBA', (imgW, y_text), (0,0,0,80))
        img.paste(rectDraw, (0, imgH - y_text), rectDraw)    
        
        # draw text again
        img, y_text = self._printAllText(img, offsetPixels)
        
        # save img
        if (outputImg != 0):
            img.save(outputImg)
        else:
            img.save(self.imgPath)
        
        return result, y_text
    
    
    ###################################################################
    # Below functions are private to base class only
    ###################################################################
    def _downloadImage(self):
        retVal = 0
        
        # try to download image
        try:
            urllib.request.urlopen(self.photoUrl)
        except urllib.error.HTTPError:
            ++retVal
        except urllib.error.URLError:
            ++retVal
        
        if (0 == retVal):
            urllib.request.urlretrieve(self.photoUrl, self.imgPath)
            # imgPath has to exist from here now
            if (os.path.isfile(self.imgPath) == 0):
                ++retVal          
        
        # some more sanity check
                
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
    Print caption and description on image
    return image, text_height in pixel
    '''
    def _printAllText(self, image, captionOffset = 0):
        # if draw nothing, return for best performance
        if (0 == len(self.captionText) and (0 == len(self.descriptionText))):
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
        y_text = fontSize + 2 + captionOffset
        
        # draw description
        if (0 != len(self.descriptionText)):
            description_lines = textwrap.wrap(self.descriptionText, charLimiter * 3)
        
            y_text = fontSizeDescription + 5 + captionOffset    
            if (description_lines != 0):
                for line in reversed(description_lines):
                    txtW, txtH = draw.textsize(line, fontDescription) # get text size on draw
                    width, height = fontDescription.getsize(line) # get 1 character size
                    draw = self._drawText(line, fontDescription, draw, imgW - txtW - 5, imgH - y_text)
                    y_text += txtH + 2
                    
                y_text += 5    
            else:
                y_text = fontSize + 5 + captionOffset
        
        # draw caption
        if (0 < len(self.captionText)):
            height = -1
            for line in reversed(caption_lines):
                txtW, txtH = draw.textsize(line, font) # get text size on draw
                width, height = font.getsize(line) # get 1 character size
                draw = self._drawText(line, font, draw, imgW - txtW - 5, imgH - y_text)
                y_text += height
            y_text -= height
        
        return img, y_text

# Unit test area ##################################################################################
###################################################################################################

class TestPhotoProcessor(unittest.TestCase):

    imgUrl = 'http://via.placeholder.com/640x480.jpg'
    imgUrlHd = 'http://via.placeholder.com/1920x1080.jpg'

    def test_download_image(self):        
        processor = PhotoProcessor(self.__class__.imgUrl)
        self.assertEqual(0, processor.dlResultCode)
        processor2 = PhotoProcessor(self.__class__.imgUrlHd)
        self.assertEqual(0, processor2.dlResultCode)
        
    def test_print_image(self):        
        processor = PhotoProcessor(self.__class__.imgUrl)
        self.assertEqual(0, processor.dlResultCode)
        self.assertEqual(0, processor.ExportImage('img1.jpg')[0])
        processor2 = PhotoProcessor(self.__class__.imgUrlHd)
        self.assertEqual(0, processor2.dlResultCode)
        self.assertEqual(0, processor2.ExportImage('imghd.jpg')[0])
    
    def test_add_caption(self):
        processor = PhotoProcessor(self.__class__.imgUrlHd)
        self.assertEqual(0, processor.dlResultCode)
        self.assertEqual(0, processor._setCaption('caption here (below text)'))
        self.assertEqual(0, processor.ExportImage('caption.jpg', 0)[0])
        
    def test_add_description(self):
        processor = PhotoProcessor(self.__class__.imgUrlHd)
        self.assertEqual(0, processor.dlResultCode)
        desc = ''
        for i in range(0,10):
            desc += 'sample descritpion text, should be long text'
        
        self.assertEqual(0, processor._setDescription(desc))
        self.assertEqual(0, processor.ExportImage('desc.jpg', 0)[0])
        
    def test_comprehensive(self):
        processor = PhotoProcessor(self.__class__.imgUrlHd)
        self.assertEqual(0, processor.dlResultCode)
        
        desc = ''
        for i in range(0,10):
            desc += 'sample descritpion text, should be long text'
        self.assertEqual(0, processor._setCaption('caption here (below text)'))
        self.assertEqual(0, processor._setDescription(desc))
        self.assertEqual(0, processor.ExportImage('fulloackage.jpg', 0)[0])
        
if __name__ == '__main__':
    unittest.main()