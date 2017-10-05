import unittest, os.path, string
import requests, re
from bs4 import BeautifulSoup

from PIL import ImageFont, Image, ImageDraw

'''
Parse and print fun fact of the day
'''
class FunFactPrinter:
    def __init__(self):
        self.mThought = ''
        self.mJoke = ''
        self.mFact = ''
        self.mIdea = ''
        self.mParseCode = self._parseData()
        
    '''
    For debug purpose
    '''
    def dumpInfo(self):
        printable = set(string.printable) # for logging compatibility
        print 'Thought: ' + filter(lambda x: x in printable, self.mThought)
        print 'Idea: ' + filter(lambda x: x in printable, self.mIdea)
        print 'Joke: ' + filter(lambda x: x in printable, self.mJoke)
        print 'Fact: ' + filter(lambda x: x in printable, self.mFact )   
    
    '''
    Print thought of the day
    '''
    def printThought(self, photoPath, x=0, y=0, fontSize=25, fontPath='DejaVuSans.ttf', dryRun = False):
        return self._printTextToPhoto(self.mThought, photoPath, x, y, fontSize, fontPath, dryRun)
    
    '''
    Print idea of the day
    '''
    def printIdea(self, photoPath, x=0, y=0, fontSize=25, fontPath='DejaVuSans.ttf', dryRun = False):
        return self._printTextToPhoto(self.mIdea, photoPath, x, y, fontSize, fontPath, dryRun)
    
    '''
    Print fact of the day
    '''
    def printFact(self, photoPath, x=0, y=0, fontSize=25, fontPath='DejaVuSans.ttf', dryRun = False):
        return self._printTextToPhoto(self.mFact, photoPath, x, y, fontSize, fontPath, dryRun)
    
    '''
    Print joke of the day
    '''
    def printJoke(self, photoPath, x=0, y=0, fontSize=25, fontPath='DejaVuSans.ttf', dryRun = False):
        return self._printTextToPhoto(self.mJoke, photoPath, x, y, fontSize, fontPath, dryRun)
    
    '''
    Print text to photo
    
    dryRun - if true, guess only mode, don't save to image
    
    return:    retVal = 0 of success
               brX, brY - bottom right pixel of the text
    '''
    def _printTextToPhoto(self, text, photoPath, x, y, fontSize, fontPath, dryRun):
        retVal = 0
        
        # prevent going further
        if (self.mParseCode != 0):
            return -1
        
        # check photoPath exists
        if (os.path.isfile(photoPath) == False):
            return -2
        
        # load image
        img = Image.open(photoPath).convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # setup font
        fontText = ImageFont.truetype(fontPath, fontSize)
        
        # draw text
        draw, resX, resY = self._drawText(text, fontText, draw, x, y)
        
        # save draw if not dry run
        if (dryRun == False):
            img.convert('RGB').save(photoPath)
        
        return retVal, resX, resY
    
    '''
    Export to photo
    
    photoPath - existing photo to print data on
    x,y - top left pixel of the text box
    dryRun - print nothing to image, this is to get size of textbox only
    
    return 0 if success 
            result w, h of the text box
    '''
    def printAllToPhoto(self, photoPath, x=0, y=0, fontSize=30, fontPath = 'DejaVuSans.ttf', dryRun = False):
        retVal = 0
        
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
        retVal, resX, resY = self._printAllText(draw, (x, y), fontSize, fontPath)
        
        # reload image to get rid of text
        img = Image.open(photoPath).convert("RGBA")
        draw = ImageDraw.Draw(img)
                
        # add background box
        boxW = resX - x + fontSize
        boxH = resY - y + 10
        rectDraw = Image.new('RGBA', (boxW, boxH), (0,0,0,100))
        img.paste(rectDraw, (x - fontSize/2, y - 5), rectDraw)
        
        # redraw text
        retVal, resX, resY = self._printAllText(draw, (x, y), fontSize, fontPath)        
        
        # save result img
        if (False == dryRun):
            img.convert('RGB').save(photoPath)
        
        return retVal, boxW, boxH
    
    '''
    Download and parse data to member vars
    
    return 0 on success, >0 otherwise
    '''
    def _parseData(self):
        result = 0
        webUrl = 'https://www.beagreatteacher.com/daily-fun-fact/'
        
        # download the web page
        requests.packages.urllib3.disable_warnings()
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        webpage = ''
        try:
            webpage = requests.get(webUrl, headers=headers, verify=False)
        except requests.exceptions.HTTPError as err:
            print 'Error downloading data ' + str(err)
            result = 1
        
        if (result != 0):
            return result
        
        # convert data to bs format
        bsData = BeautifulSoup(webpage.content, 'lxml')
        mainSection = bsData.find('main', {'class': 'content'})
        if (mainSection is None):
            return 3
        
        mainSection = mainSection.find_all('p')
        if (mainSection is None):
            return 4
        
        result = -4
        
        # get quote
        self.mThought = self._parseMainSectionModule(mainSection[0])
        result += (len(self.mThought) > 0)
                
        # get joke
        self.mJoke = self._parseMainSectionModule(mainSection[1])
        result += (len(self.mJoke) > 0)
        
        # get fact
        self.mFact = self._parseMainSectionModule(mainSection[2])
        result += (len(self.mFact) > 0)
        
        # get idea
        self.mIdea = self._parseMainSectionModule(mainSection[3])
        result += (len(self.mIdea) > 0)
        
        # save data for debugging
        dataFile = open('/tmp/data.funfact','w')
        dataFile.write(bsData.find('main', {'class': 'content'}).prettify(encoding='utf-8'))
        dataFile.close()
        
        return result

    def _parseMainSectionModule(self, section):
        key = ''
        if (len(str(section)) > 10):
            key = str(section.encode('unicode-escape')).decode('unicode-escape')
            
            # strip xml tag
            key = re.sub('<[^>]*>', '', key)
        
        return key

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
    Print all text data to photo
    
    return    retVal = 0 if success
            resX, resY : x ,y of bottom right pixel of text box, useful for calculating background box
    '''
    def _printAllText(self, draw, (x,y), fontSize = 30, fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        # open image & setup font
        fontText = ImageFont.truetype(fontPath, fontSize)
        
        maxX = x
        
        # print thought
        draw, resX, resY = self._drawText('Thought: ' + self.mThought, fontText, draw, x, y)
        if (maxX < resX): maxX = resX
        
        # print fact
        draw, resX, resY = self._drawText('Fact: ' + self.mFact, fontText, draw, x, resY)
        if (maxX < resX): maxX = resX
         
        # print Joke
        draw, resX, resY = self._drawText('Joke: ' + self.mJoke, fontText, draw, x, resY)
        if (maxX < resX): maxX = resX
         
        # print fact
        draw, resX, resY = self._drawText('Idea: ' + self.mIdea, fontText, draw, x, resY)
        if (maxX < resX): maxX = resX
        
        return 0, maxX, resY

###########################################################################
# Unit test area
###########################################################################
class TestFunFact(unittest.TestCase):
    def test_parse_success(self):
        funFact = FunFactPrinter()
        self.assertEqual(0, funFact.mParseCode)
        funFact.dumpInfo()
        
    def test_print_to_photo(self):
        funFact = FunFactPrinter()
        self.assertEqual(0, funFact.mParseCode)
        
        # create test image
        testImage = 'image2.jpg'
        img = Image.new('RGB', (1920, 1080), "white")
        img.save(testImage)
        
        # print to img
        self.assertEquals(funFact.printAllToPhoto(testImage, x=100, y=100, fontSize=20), 0)
        
    def test_print_single_to_photo(self):
        funFact = FunFactPrinter()
        self.assertEqual(0, funFact.mParseCode)
        
        # create test image
        testImage = 'image1.jpg'
        img = Image.new('RGB', (1920, 1080), "white")
        img.save(testImage)
        
        # print thought to img
        x = 50
        y = 50
        retVal, resX, resY = funFact.printThought(testImage, x, y)
        self.assertEquals(retVal, 0)
        self.assertGreater(resX, x)
        self.assertGreater(resY, y)
        
        # print idea to img
        x = 50
        y = 2*y
        retVal, resX, resY = funFact.printIdea(testImage, x, y)
        self.assertEquals(retVal, 0)
        self.assertGreater(resX, x)
        self.assertGreater(resY, y)
        
        # print joke to img
        x = 50
        y = 2*y
        retVal, resX, resY = funFact.printJoke(testImage, x, y)
        self.assertEquals(retVal, 0)
        self.assertGreater(resX, x)
        self.assertGreater(resY, y)
        
        # print fact to img
        x = 50
        y = 2*y
        retVal, resX, resY = funFact.printFact(testImage, x, y)
        self.assertEquals(retVal, 0)
        self.assertGreater(resX, x)
        self.assertGreater(resY, y)
if __name__ == '__main__':
    unittest.main()