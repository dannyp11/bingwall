import unittest, os.path, string
from enum import IntEnum
from random import randint
from sets import Set
from PIL import Image

from FunFactPrinter import FunFactPrinter

# Different modes for fun fact of the day option
class FunFactMode(IntEnum):
    OFF = 0
    TEXT_BOX = 1    # save everything in 1 textbox
    SCATTER = 2     # randomly put various messages throughout the image
    
'''
Manage fun fact printer
Use this object instead of FunfactPrinter itself
'''
class FunFactManager():
    '''
    Input:
    funfactMode  - choose from FunFactMode
    photoPath    - path to existing image to print to
    fontPath     - optional font path
    '''
    def __init__(self, funfactMode, fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        self.mFunFactPrinter = FunFactPrinter()
        self.mFontPath = fontPath
        self.mFactMode = funfactMode
        self.mExistingBoxes = Set([])
        self.mResultCode = self._initialize()
        
    '''
    Init the object
    
    return 0 on success
           -2 on failed fun fact onject init
           -3 on other error
    '''
    def _initialize(self):
        # init funfact object
        if (0 != self.mFunFactPrinter.mParseCode):
            print 'Error code ' + str(self.mFunFactPrinter.mParseCode) + ' printing textbox fun fact'
            return -2
        
        # make sure mode is valid
        if (self.mFactMode < 0 or self.mFactMode >= len(FunFactMode)):
            print 'Invalid fact mode ' + str(self.mFactMode)
            return -3
        
        return 0
    
    '''
    Check if 2 boxes intersect
    Input: (box1), (box2)
            box info: top left x/y and width, height
    '''
    def _isBoxIntersect(self, (x1, y1, w1, h1), (x2, y2, w2, h2)):
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
    Print in text box mode
    '''
    def _printTextBoxMode(self, photoPath):
        retVal, boxW, boxH = self.mFunFactPrinter.printAllToPhoto(photoPath, 0, 0, 25, self.mFontPath, dryRun=True)
        if (retVal != 0):
            print 'Error code ' + str(retVal) + ' geting size textbox fun fact'
        
        boxX, boxY = self._getEligibleBox((boxW, boxH))
        if (boxX < 0 or boxY < 0):
            retVal = -1
            print 'Error getting position of text box'
        else:
            retVal, tmpW, tmpH = self.mFunFactPrinter.printAllToPhoto(photoPath, boxX, boxY, 25, self.mFontPath, dryRun=False)
            
        return retVal
    
    '''
    Print in scatter mode
    '''
    def _printScatterMode(self, photoPath):
        retValOverall = 0
        
        minFontSize = 18
        maxFontSize = 22
        
        # get metrics of textboxes first
        fontSizeThought = randint(minFontSize, maxFontSize)
        fontSizeIdea = randint(minFontSize, maxFontSize)
        fontSizeFact = randint(minFontSize, maxFontSize)
        fontSizeJoke = randint(minFontSize, maxFontSize)
        
        # get size of all facts
        retVal, thoughtW, thoughtH = self.mFunFactPrinter.printThought(photoPath, 0, 0, fontSizeThought, self.mFontPath, True)
        retVal, ideaW, ideaH = self.mFunFactPrinter.printThought(photoPath, 0, 0, fontSizeIdea, self.mFontPath, True)
        retVal, factW, factH = self.mFunFactPrinter.printThought(photoPath, 0, 0, fontSizeFact, self.mFontPath, True)
        retVal, jokeW, jokeH = self.mFunFactPrinter.printThought(photoPath, 0, 0, fontSizeJoke, self.mFontPath, True)
    
        # print thought
        if (randint(0, 1)):
            x, y = self._getEligibleBox((thoughtW, thoughtH))
            if (x != -1 and y != -1):
                retVal, resX, resY = self.mFunFactPrinter.printThought(photoPath, 
                                        x, y, fontSizeThought, self.mFontPath)
                retValOverall += retVal
                if (0 == retVal):
                    self.addObstacleBox((x, y, thoughtW, thoughtH))   
                                 
        # print idea
        if (randint(0, 1)):
            x, y = self._getEligibleBox((ideaW, ideaH))
            if (x != -1 and y != -1):
                retVal, resX, resY = self.mFunFactPrinter.printIdea(photoPath, 
                                        x, y, fontSizeIdea, self.mFontPath)
                retValOverall += retVal
                if (0 == retVal):
                    self.addObstacleBox((x, y, ideaW, ideaH))  
        
        # print joke
        if (randint(0, 1)):
            x, y = self._getEligibleBox((jokeW, jokeH))
            if (x != -1 and y != -1):
                retVal, resX, resY = self.mFunFactPrinter.printJoke(photoPath, 
                                        x, y, fontSizeJoke, self.mFontPath)
                retValOverall += retVal
                if (0 == retVal):
                    self.addObstacleBox((x, y, jokeW, jokeH))  
                    
        # print fact
        if (randint(0, 1)):
            x, y = self._getEligibleBox((factW, factH))
            if (x != -1 and y != -1):
                retVal, resX, resY = self.mFunFactPrinter.printFact(photoPath, 
                                        x, y, fontSizeFact, self.mFontPath)
                retValOverall += retVal
                if (0 == retVal):
                    self.addObstacleBox((x, y, factW, factH))  
                 
        return retValOverall
    '''
    Will randomly generate x and y of box that has width and height
    obstacle boxes will be avoided when generating
    
    Input: w,h of target box
    Output: x,y of eligible box
            x = y = -1 on error generating, usually out of luck
    '''
    def _getEligibleBox(self, (width, height)):
        resultX = resultY = -1
        
        minX = 10
        minY = 30
        maxX = 1920 - width
        maxY = 1080 - height
        
        # limit to maxTries tries
        maxTries = 50
        numTries = 0
        while (numTries < maxTries):
            # get random x, y
            tmpX = randint(minX, maxX)
            tmpY = randint(minY, maxY)
            
            # now iterate thru all obstacle to determine if it intersects
            # with any obstacle or not
            isValidResult = True
            for obstacle in self.mExistingBoxes:
                if (self._isBoxIntersect((tmpX - 5, tmpY - 5, width + 5, height + 5), obstacle)):
                    isValidResult = False
                    break
            
            if (isValidResult):
                resultX = tmpX
                resultY = tmpY
                break
            
            ++numTries
            
        return resultX, resultY
    
    '''
    Public function: add box that the text should avoid
    input: top left x, y, width, height
    '''
    def addObstacleBox(self, (x, y, w, h)):
        self.mExistingBoxes.add((x, y, w, h))

    '''
    Print to photoPath
    
    return 0 on success
            -1 on photopath not exists
            -2 on print failure
    '''
    def exportToImage(self, photoPath = 0):
        if (False == os.path.isfile(photoPath)):
            return -1
        
        if (FunFactMode.TEXT_BOX == self.mFactMode):
            if (0 != self._printTextBoxMode(photoPath)):
                return -2
            
        elif (FunFactMode.SCATTER == self.mFactMode):
            if (0 != self._printScatterMode(photoPath)):
                return -2
    
        return 0
    
    '''
    Dump everything in its member vars
    '''
    def dumpInfo(self):
        self.mFunFactPrinter.dumpInfo()
        print 'Fact mode: ' + str(self.mFactMode)
        
        for box in self.mExistingBoxes:
            print ' Obstacle ' + str(box[0]) + ' ' + str(box[1]) + ' ' + str(box[2]) + ' ' + str(box[3])
        
##########################################################################
# unit test area
##########################################################################
class TestFunFactManager(unittest.TestCase):

    def test_parse_success(self):
        # create test image
        testImage = 'testImage1.jpg'
        img = Image.new('RGB', (1920, 1080), "white")
        img.save(testImage)
        
        # should return success for all modes
        factMgr = FunFactManager(FunFactMode.OFF)
        self.assertEqual(0, factMgr.mResultCode)
        
        factMgr = FunFactManager(FunFactMode.SCATTER)
        self.assertEqual(0, factMgr.mResultCode)
        
        factMgr = FunFactManager(FunFactMode.TEXT_BOX)
        self.assertEqual(0, factMgr.mResultCode)
    
    def test_offmode_print(self):
        # create test image
        testImage = 'testImage2.jpg'
        img = Image.new('RGB', (1920, 1080), "white")
        img.save(testImage)
        
        # draw box to img
        img = Image.open(testImage).convert("RGBA")
        boxX = boxY = 100
        boxW = boxH = 700
        rectDraw = Image.new('RGBA', (boxW, boxH), (0,0,0,150))
        img.paste(rectDraw, (boxX, boxY), rectDraw)
        img.convert('RGB').save(testImage)
    
        # now create fun fact mgr
        factMgr = FunFactManager(FunFactMode.OFF)
        self.assertEqual(0, factMgr.mResultCode)
        
        # add obstacle to fact mgr
        factMgr.addObstacleBox((boxX, boxY, boxW, boxH))
        
        # print to image, expect nothing new printed
        self.assertEqual(0, factMgr.exportToImage(testImage))
    
    def test_textbox_print(self):
        # create test image
        testImage = 'testImage3.jpg'
        img = Image.new('RGB', (1920, 1080), "white")
        img.save(testImage)
        
        # draw box to img
        img = Image.open(testImage).convert("RGBA")
        boxX = boxY = 100
        boxW = boxH = 200
        rectDraw = Image.new('RGBA', (boxW, boxH), (0,0,0,150))
        img.paste(rectDraw, (boxX, boxY), rectDraw)
        img.paste(rectDraw, (boxX + 300, boxY + 300), rectDraw)
        img.convert('RGB').save(testImage)
    
        # now create fun fact mgr
        factMgr = FunFactManager(FunFactMode.TEXT_BOX)
        self.assertEqual(0, factMgr.mResultCode)
        
        # add obstacle to fact mgr
        factMgr.addObstacleBox((boxX, boxY, boxW, boxH))
        factMgr.addObstacleBox((boxX + 300, boxY + 300, boxW, boxH))
        
        # print to image, expect a textbox
        self.assertEqual(0, factMgr.exportToImage(testImage))
    
    def test_scatter_print(self):
        # create test image
        testImage = 'testImage4.jpg'
        img = Image.new('RGB', (1920, 1080), "white")
        img.save(testImage)
        
        # draw box to img
        img = Image.open(testImage).convert("RGBA")
        boxX = boxY = 100
        boxW = boxH = 700
        rectDraw = Image.new('RGBA', (boxW, boxH), (0,0,0,150))
        img.paste(rectDraw, (boxX, boxY), rectDraw)
        img.convert('RGB').save(testImage)
    
        # now create fun fact mgr
        factMgr = FunFactManager(FunFactMode.SCATTER)
        self.assertEqual(0, factMgr.mResultCode)
        
        # add obstacle to fact mgr
        factMgr.addObstacleBox((boxX, boxY, boxW, boxH))
        
        # print to image, expect scattered messages
        self.assertEqual(0, factMgr.exportToImage(testImage))
    
if __name__ == '__main__':
    unittest.main()