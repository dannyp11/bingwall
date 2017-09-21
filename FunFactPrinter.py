import unittest
import requests, re
from bs4 import BeautifulSoup

from PIL import ImageFont, Image, ImageDraw

'''

'''
class FunFactPrinter:
    def __init__(self):
        self.mThought = ''
        self.mJoke = ''
        self.mFact = ''
        self.mIdea = ''
        self.mParseCode = self._parseData()
        
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
        bsData = BeautifulSoup(webpage.content.decode('utf-8'), 'lxml')
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
        
        return result

    def _parseMainSectionModule(self, section):
        key = ''
        if (len(str(section)) > 10):
            key = str(section)
            
            # strip xml tag
            key = re.sub('<[^>]*>', '', key)
        
        return key

    def _dumpInfo(self):
        print 'Thought: ' + self.mThought
        print 'Idea: ' + self.mIdea
        print 'Joke: ' + self.mJoke
        print 'Fact: ' + self.mFact

###########################################################################
# Unit test area
###########################################################################
class TestFunFact(unittest.TestCase):
    def test_download_success(self):
        funFact = FunFactPrinter()
        self.assertEqual(0, funFact.mParseCode)
        funFact._dumpInfo()
        
if __name__ == '__main__':
    unittest.main()