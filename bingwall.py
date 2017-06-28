#!/usr/bin/env python

import urllib, json, urllib2
import getopt, sys, os, shutil, textwrap
from PIL import ImageFont, Image, ImageDraw

import WeatherPrinter

'''
Check if internet is on
'''
def isInternetOn():
    googleUrl = 'http://216.58.192.142'

    try:
        urllib2.urlopen(googleUrl, timeout=1)
        return True
    except urllib2.URLError as err: 
        return False

'''
Draw white text with black outline

text - input
font - font
draw - draw object
x, y - upperleft position of text
fillcolor - color of text, default: white
'''
def DrawText(text, font, draw, x , y, fillColor = (255, 255, 255, 255)):
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
Get description of image given bing link and image title

url    : description link
title  : image title
'''
def GetImgDescription(url, title):
    
    result = 0
    
    # strip title out of copyright portion
    strDelimiter = " ("
    caption_index = title.find(strDelimiter)    
    caption =  title[0:caption_index]
    
    # load url
    webpage = ""
    try:
        webpage = urllib2.urlopen(url)
    except urllib2.HTTPError:
        result = 1
    except urllib2.URLError:
        result = 1
    
    if (result != 0):
        return result    
    
    data = webpage.read()
    data = data.decode('utf-8')
    
    # query caption to find description
    query_start = "<h2 class=\"\">" + caption + "</h2></div><div>"
    query_stop = "</div>"
    
    found = data.find(query_start)
    index_start = found + len(query_start)
    index_stop = data.find(query_stop, index_start)
    
    description = data[index_start: index_stop]

    return result, description

'''
Add caption to image

inputImg : path to input
outputImg: path to output
fontPath : path to dejavu font
description: optional description to print
'''
def CaptionAdder(inputImg, outputImg, fontPath, text, description = 0):    
    
    result = 0
    
    # format text
    fontSize = 20
    fontSizeDescription = fontSize - 2;
        
    # open input
    font = ImageFont.truetype(fontPath, fontSize)
    fontDescription = ImageFont.truetype(fontPath, fontSizeDescription)
    img = Image.open(inputImg)
    imgW, imgH = img.size
    draw = ImageDraw.Draw(img)    
    
    # determine text box size
    charLimiter = 50
    strDelimiter = "("
    
    caption_lines = text.split(strDelimiter)
    caption_lines[-1] = "(" + caption_lines[-1]            
    
    description_lines = 0
    
    # draw description
    if (description != 0):
        description_lines = textwrap.wrap(description, charLimiter * 3)
    
    y_text = fontSizeDescription + 5    
    if (description_lines != 0):
        for line in reversed(description_lines):
            txtW, txtH = draw.textsize(line, fontDescription) # get text size on draw
            width, height = fontDescription.getsize(line) # get 1 character size
            draw = DrawText(line, fontDescription, draw, imgW - txtW - 5, imgH - y_text)
            y_text += txtH + 2
            
        y_text += 5    
    else:
        y_text = fontSize + 5
    
    # draw caption
    for line in reversed(caption_lines):
        txtW, txtH = draw.textsize(line, font) # get text size on draw
        width, height = font.getsize(line) # get 1 character size
        draw = DrawText(line, font, draw, imgW - txtW - 5, imgH - y_text)
        y_text += height    
    
    # save img
    img.save(outputImg)
    
    return result

imgPath = '/tmp/image.jpg'
fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
addDescription = 0
def usage():
    print "Usage: python " + (sys.argv[0]) + " OPTION [VALUE]"
    print "    -p    where to save the image, default " + imgPath
    print "    -c    add caption to image" 
    print "    -d    add description to image" 
    print "    -f    path to text font for caption & description. This will also trigger -c, default " + fontPath    

def main():    
    
    result = 0
    imgPath = '/tmp/image.jpg'
    fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    addCaption = 0
    addDescription = 0   
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:hdcf:', ['path=','help'])
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
            addCaption = 1
            fontPath = arg
            
            # check if fontPath exists
            if (os.path.isfile(fontPath)):
                addCaption = 1
                
        elif opt in ('-d'):
            addDescription = 1
        elif opt in ('-c'):
            addCaption = 1
    
    # check internet
    if (isInternetOn() == False):
        print "Internet is off"
        return 1
    
    # download image
    url = "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    imgLink = "http://bing.com" +  data["images"][0]["url"] 
    descriptionLink = data["images"][0]["copyrightlink"]
    captionText = data["images"][0]["copyright"]
    
    try:
        urllib2.urlopen(imgLink)
    except urllib2.HTTPError:
        result = 1
    except urllib2.URLError:
        result = 1
    
    if result == 0:
        urllib.urlretrieve(imgLink, imgPath)
    
    # result
    if (os.path.isfile(imgPath) == 0):
        result = 1            
    
    # add description to image        
    description = 0
    if (result == 0 and addDescription == 1):        
        result, description = GetImgDescription(descriptionLink, captionText)
    
    # add caption to image
    if (result == 0 and addCaption == 1):
        # default values
        inputImg = imgPath
        outputImg = "/tmp/bing-wall-output.jpg"  
        
        if (CaptionAdder(inputImg, outputImg, fontPath, captionText, description) == 0):
            # rm input, change output as input name
            os.remove(inputImg)
            shutil.move(outputImg, inputImg)                                        
    
    if (result == 0):
        print "Successfully saved " + imgPath
    else:
        print "Error code " + str(result)
        
    return result

if __name__ == "__main__":
    main()
