from PIL import Image
from PIL import ImageDraw
from datetime import datetime
import schedule
import time
import json
import math
import requests
import pytz
import random
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics #real 
#from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics #test 

###############################################################
###############################################################
###############################################################
#Configuration for the matrix

options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'
matrix = RGBMatrix(options = options)


###############################################################
###############################################################
###############################################################
#NON MAIN DRAWING FUNCTIONS


def get_nyt():
    #get article information from nyt top articles api 
    nyt_appid = ''

    response = requests.get('https://api.nytimes.com/svc/topstories/v2/home.json?api-key='+nyt_appid)
    nyt_data = json.loads(response.text)

    articles = nyt_data['results']  

    return articles

def get_weather():
    #get weather from openweather api 
    appid = ''
    location = '4926563' #South Bend, IN
    response = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+location+'&mode=json&cnt=10&appid='+appid)
    data = json.loads(response.text)
    main = data['main']
    curr = main['temp']
    low = main['temp_min']
    high = main['temp_max']

    current = ctof(curr) 
    low = ctof(low) 
    high = ctof(high) 

    temps = current,low,high

    return current,low,high

def ctof(num):
    temp = ((num-273.15)*(1.8)+32)
    temp = int(round(temp))
    return temp 




###############################################################
###############################################################
###############################################################
#FONT DEFINITIONS

time_font = graphics.Font()
time_font.LoadFont("../rpi-rgb-led-matrix/fonts/6x12.bdf")

font = graphics.Font()
font.LoadFont("../rpi-rgb-led-matrix/fonts/4x6.bdf")

textColor = graphics.Color(255, 255, 255)


###############################################################
###############################################################
###############################################################

def job():
    matrix.Clear()
    offscreen_canvas = matrix.CreateFrameCanvas()

    image = Image.open('icons/' + 'nyt' + '.png')
    image.thumbnail((10, 10))


    current,low,high = get_weather()
    articles = get_nyt()

    img_x = 2
    img_y = 32

    ###############################################################
    #TIME

    now = datetime.now(pytz.timezone('US/Eastern'))
    current_time = now.strftime("%I:%M %p")

    time_x = 8 
    time_y = 7

    #graphics.DrawText(matrix, time_font, time_x, time_y, textColor, current_time)

    ###############################################################
    #WEATHER

    weather_x = 1
    weather_y = 14

    weather_line = str(' C:') + str(current) + str(' ') + str('L:') +  str(low) + str(' ') + str('H:') + str(high)
    #graphics.DrawText(matrix, font, weather_x, weather_y, textColor, weather_line)


    ###############################################################
    #TOP HEADLINES

    #drawimage('icons/' + 'nyt' + '.png')

    j = 0 

    while j < 10: 
        title = articles[j]['title']
        y_pos = 48 
        x_pos = 1 
        i = 0     

        offscreen_canvas.Clear()
        offscreen_canvas.SetImage(image.convert('RGB'),img_x,img_y)
        graphics.DrawText(offscreen_canvas, font, x_pos, y_pos, textColor, title)
        current_time = now.strftime("%I:%M %p")
        graphics.DrawText(offscreen_canvas, time_font, time_x, time_y, textColor, current_time)
        graphics.DrawText(offscreen_canvas, font, weather_x, weather_y, textColor, weather_line)
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

        time.sleep(2.0)

        while i < (len(title)*4 + 64):
            offscreen_canvas.Clear()
            offscreen_canvas.SetImage(image.convert('RGB'),img_x,img_y)
            graphics.DrawText(offscreen_canvas, font, x_pos, y_pos, textColor, title)
            current_time = now.strftime("%I:%M %p")
            graphics.DrawText(offscreen_canvas, time_font, time_x, time_y, textColor, current_time)
            graphics.DrawText(offscreen_canvas, font, weather_x, weather_y, textColor, weather_line)

            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            x_pos -= 1 
            i += 1  
            time.sleep(0.025)
        time.sleep(0.5)
        j += 1


    ###############################################################


job()
schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
