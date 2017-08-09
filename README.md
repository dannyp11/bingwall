# bingwall
unoffical Bing's Photo of the Day fetcher with nice caption adder and more 

[![Build Status](https://travis-ci.org/dannyp11/bingwall.svg?branch=devel)](https://travis-ci.org/dannyp11/bingwall)

## Introduction
As you may know there's currently a wallpaper setter called wallch which allows you to set Wikipedia's photo of the day as wallpaper. However, that tool doesn't (or at least at the time I write this readme) support Bing wallpaper. So bingwall is supposed to be filled in that gap. 


## About bingwall
As of June 2017 Microsoft doesn't provide official API to get its gorgeous image of the day (if you have it please let me know :+1:). Thus, this tool uses hacky way by reverse engineered call to Bing. Therefore, stability isn't guaranteed but the author's best effort. This tool is primarily developed on Unix like environment and, therefore, works best with linux. The tool is continously tested against the author's OS such as Ubuntu 14 & Fedora 25. The tool only download full hd 1920x1080 image


## Development roadmap
  1. add caption - done
  2. add description - done
  3. add weather (may need to register API key) - done
  4. nicer weather icon - done
  5. what else?


## Usage
```
$ python bingwall.py -h
Usage: python bingwall.py OPTION [VALUE]
    -p {path}         where to save the image, default /tmp/image.jpg
    -c                add caption to image
    -d                add description to image
    -f {fontPath}     path to text font for caption & description. This will also trigger -c, default /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
    -w {zipcode}      turn on weather feature, must also use -k option
    -k {api.key path} path to api key file for http://openweathermap.org/appid, must also use -w
    -x {top left x}   topleft x pixel of weather info (optional)
    -y {top left y}   topleft y pixel of weather info (optional)

```

## Sample output

![Alt text](https://raw.githubusercontent.com/dannyp11/bingwall/master/img/sample2.jpg?raw=true "With caption")
![Alt text](https://raw.githubusercontent.com/dannyp11/bingwall/master/img/sample1.jpg?raw=true "With caption & description")
![Alt text](https://raw.githubusercontent.com/dannyp11/bingwall/master/img/sample3.jpg?raw=true "With caption & description & weather info")
