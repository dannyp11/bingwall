import unittest
import requests
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
        if (len(str(mainSection[0])) > 10):
            self.mThought = str(mainSection[0])
            result +=1
                
        # get joke
        if (len(str(mainSection[1])) > 10):
            self.mJoke = str(mainSection[1])
            result +=1
        
        # get fact
        if (len(str(mainSection[2])) > 10):
            self.mFact = str(mainSection[3])
            result +=1
            
        # get idea
        if (len(str(mainSection[3])) > 10):
            self.mIdea = str(mainSection[3])
            result +=1
        
        return result


###########################################################################
# Unit test area
###########################################################################
class TestFunFact(unittest.TestCase):
    def test_download_success(self):
        funFact = FunFactPrinter()
        self.assertEqual(0, funFact.mParseCode)
        
if __name__ == '__main__':
    unittest.main()