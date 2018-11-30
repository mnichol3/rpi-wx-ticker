import urllib2
import json
import os
import glob
import time
import feedparser
import datetime
from PIL import Image, ImageFont, ImageDraw
import threading
import random


# --------- User Settings ---------
STATE = "YOUR_STATE"
CITY = "YOUR_CITY"
WUNDERGROUND_API_KEY = "YOUR_KEY_HERE"
MINUTES_BETWEEN_READS = 5
RSS_URL = "https://alerts.weather.gov/cap/wwaatmget.php?x=MDC003&y=0"
# ---------------------------------

PPM_COUNT = 0
ACTIVE_WARN = False

# Takes a string/int and adds a padding 0 if necessary. Returns a string
# For 2 digit ints
def pad_2dig(num):
        if (int(num) < 10):
                res = "0" + str(num)
        else:
                res = str(num)
        return res


# Takes a string/int and adds a padding 0's if necessary. Returns a string
# For 3 digit ints
def pad_3dig(num):
        if (int(num) < 100):
                if (int(num) < 10):
                        res = "00" + str(num)
                else:
                        res = "0" + str(num)
        else:
                res = str(num)
        return res


def rchop(my_string, ending):
        if (my_string.endswith(ending)):
                return my_string[:-len(ending)]
        return my_string


def get_data(keyword):
	api_url = "http://api.wunderground.com/api/" + WUNDERGROUND_API_KEY + "/" + keyword + "/q/" + STATE + "/" + CITY + ".json"
	try:
		f = urllib2.urlopen(api_url)
	except:
		return []
	json_data = f.read()
	f.close()
	return json.loads(json_data)


def get_conditions():
	cond_dict = {}
	cond_str = ""
	conditions = get_data("conditions")

	if (conditions == []): 
		print "Error! Wunderground API call failed"
		return -1
	else:
                time = datetime.datetime.now().time()
                hour = time.hour
                mins = time.minute
                
                if (hour < 10):
                        hour = "0" + str(hour)
                else:
                        hour = str(hour)

                if (mins < 10):
                        mins = "0" + str(mins)
                else:
                        mins = str(mins)
                        
		humidity_pct = conditions['current_observation']['relative_humidity']
		humidity = humidity_pct.replace("%","")

                wind_dir = str(conditions['current_observation']['wind_degrees'])
                wind_gst = str(int(float(conditions['current_observation']['wind_gust_mph'])))
		wind_spd = str(int(float(conditions['current_observation']['wind_mph'])))

		cond_dict['time_date'] = conditions['current_observation']['local_time_rfc822']
		cond_dict['temp_f'] = conditions['current_observation']['temp_f']
		cond_dict['dewpoint_f'] = conditions['current_observation']['dewpoint_f']
		cond_dict['wind_mph'] = pad_2dig(wind_spd)
                cond_dict['wind_gust_mph'] = pad_2dig(wind_gst)
		cond_dict['pressure_in'] = conditions['current_observation']['pressure_in']
		cond_dict['1_hr_precip'] = conditions['current_observation']['precip_1hr_in']
		cond_dict['daily_precip'] = conditions['current_observation']['precip_today_in']
		cond_dict['solar_rad'] = conditions['current_observation']['solarradiation']
		cond_dict['humidity'] = humidity
		cond_dict['UV_index'] = conditions['current_observation']['UV']
		cond_dict['wind_dir'] = pad_3dig(wind_dir)
		cond_dict['feels_like'] = conditions['current_observation']['feelslike_f']
		cond_dict['vis_sm'] = conditions['current_observation']['visibility_mi']
		cond_dict['weather'] = conditions['current_observation']['weather']
		cond_dict['obs_time'] = conditions['current_observation']['observation_time']
		cond_dict['pressure_trend'] = conditions['current_observation']['pressure_trend']
		
		date_time = cond_dict['time_date'][:-9]
		date = cond_dict['time_date'][:-15]
		cond_dict['time_date'] = date_time
                cond_dict['date'] = date

		cond_str = cond_str + date + "  " + hour + ":" + mins + "z   "
		cond_str = cond_str + "" + cond_dict['weather'] + "   "
		cond_str = cond_str + "Temp: " + str(int(float(cond_dict['temp_f']))) + "F" + "   "
		cond_str = cond_str + "Dwpt: " + str(int(float(cond_dict['dewpoint_f']))) + "F" + "   "
		cond_str = cond_str + "RH: " + str(cond_dict['humidity']) + "%" + "   "
		cond_str = cond_str + "Feels Like: " + str(int(float(cond_dict['feels_like']))) + "F" + "   "
		cond_str = cond_str + "Wind: " + cond_dict['wind_dir'] + " / " + cond_dict['wind_mph'] + " G " + cond_dict['wind_gust_mph'] + " mph" + "   "
		cond_str = cond_str + "A" + str(cond_dict['pressure_in']) + str(cond_dict['pressure_trend']) + "   "
		#cond_str = cond_str + "UV Index: " + str(cond_dict['UV_index']) + "   "
		#cond_str = cond_str + "1-hour Precip: " + str(cond_dict['1_hr_precip']) + " in   "
		cond_str = cond_str + "Daily Precip: " + str(cond_dict['daily_precip']) + " in   "
		#cond_str = cond_str + cond_dict['obs_time'] + "   "


                return cond_str


def get_forecast():
	forecast_dict = {}
	forecast_str = ""
	forecast = get_data("forecast")
	if (forecast == []):
		print "Error! Wunderground API call failed. Skipping a reading then continuing ..."
		return -1
	else:
	
		# "Today"
		forecast_dict['period_1'] = forecast['forecast']['txt_forecast']['forecastday'][0]['title'] + ": " + forecast['forecast']['txt_forecast']['forecastday'][0]['fcttext']
		# "Tonight"
		forecast_dict['period_2'] = forecast['forecast']['txt_forecast']['forecastday'][1]['title'] + ": " + forecast['forecast']['txt_forecast']['forecastday'][1]['fcttext']
		# "Tomorrow"
		forecast_dict['period_3'] = forecast['forecast']['txt_forecast']['forecastday'][2]['title'] + ": " + forecast['forecast']['txt_forecast']['forecastday'][2]['fcttext']
		# "Tomorrow Night"
		forecast_dict['period_4'] = forecast['forecast']['txt_forecast']['forecastday'][3]['title'] + ": " + forecast['forecast']['txt_forecast']['forecastday'][3]['fcttext']
		# "Day After Tomorrow"
		forecast_dict['period_5'] = forecast['forecast']['txt_forecast']['forecastday'][4]['title'] + ": " + forecast['forecast']['txt_forecast']['forecastday'][4]['fcttext']

		forecast_str = forecast_str + "Forecast: "
		forecast_str = forecast_str +  forecast_dict['period_1'] + " "
		forecast_str = forecast_str +  forecast_dict['period_2'] + " "
		forecast_str = forecast_str +  forecast_dict['period_3'] + " "
		forecast_str = forecast_str +  forecast_dict['period_4'] + " "
		forecast_str = forecast_str +  forecast_dict['period_5'] + " "

		return forecast_str


#---------------------------------------------------------
# Will get simplified active advisory/warning string
# or, if there are none active,
# "There are no active watches, warnings or advisories"
#---------------------------------------------------------
def get_warnings():
        global ACTIVE_WARN
        warn = ""
	# Anne Arundel County, MD url from https://alerts.weather.gov/
	d = feedparser.parse(RSS_URL)
	if (d.status == 200):
		if (len(d['entries']) == 1 and "No active" in d['entries'][0]['title']): 
			ACTIVE_WARN = False 	
			warn = d['entries'][0]['title']
		else:
			ACTIVE_WARN = True
			warn_len = len(d['entries'])
			for idx in range(warn_len):
				warn_str = d['entries'][idx]['title']
				warn_str = rchop(warn_str, " by NWS")
				warn_str_short = warn_str.replace(" issued", ":").replace(" at", "").replace("until", "-") 
				warn = warn + warn_str_short
				if (idx != warn_len - 1):
					warn = warn + " &&& "
		return warn
	else:
		warn = "Weather Warning RSS parse error: status " + str(d.status)
		return -1
	


items = []
displayItems = []


def colorRed():
        return (255, 0, 0)

def colorGreen():
        return (0, 255, 0)

def colorBlue():
        return (0, 0, 255)

def colorWhite():
        return (255, 255, 255)

def colorAqua():
        return (40, 187, 200)

def colorPink():
        return (204, 51, 167)

def colorTan():
        return (164, 127, 48)

def colorLBlue():
        return (73, 131, 228)

def colorLGreen():
        return (2, 220, 103)

def colorMagenta():
        return (196, 14, 178)

def colorYellow():
        return (255, 255, 0)




def populateItems():
        del items[:]
        del displayItems[:]

        # Delete the old image file
        os.system("find . -name \*.ppm -delete")

        items.append(get_conditions())
        items.append("***" + get_warnings() + "***")
        #items.append(get_forecast())
        
def createLinks():
        try:
                populateItems()
                writeImage(items)
        except ValueError:
                print("Error creating links")
 
def writeImage(wx_text):
        global PPM_COUNT
        global ACTIVE_WARN
        bitIndex = 0
        text_len = []
        text_list = wx_text[:]

        font = ImageFont.truetype("usr/share/fonts/truetype/freefont/FreeSans.ttf", 16)
        
        for x in text_list:
                x = unicode(x)
                text_len.append(font.getsize(x)[0])

        text = ''.join(text_list)

        if (ACTIVE_WARN):
                color_warn = colorMagenta()
        else:
                color_warn = colorRed()
        color_curr = colorRed()
        color_fore = colorGreen()

        width, ignore = font.getsize(text)
        im = Image.new("RGB", (width + 30, 16), "black")
        draw = ImageDraw.Draw(im)
        
        draw.text((0, 0), text_list[0], color_curr, font = font)
        draw.text((text_len[0], 0), text_list[1], color_warn, font = font)
        # Uncomment the statement below to show forecast
        #draw.text((text_len[0] + text_len[1], 0), text_list[2], color_fore, font = font)
        filename = str(PPM_COUNT) + ".ppm"
        displayItems.append(filename)
        im.save(filename)

def run():
        createLinks()
        threading.Timer(5 * 60, run).start()
        showOnLEDDisplay()
                

def showOnLEDDisplay():
        for disp in displayItems:
                os.system("sudo ./demo -t 300 --led-rows=16 --led-chain=3 --led-brightness=25 --led-pwm-lsb-nanoseconds=400 --led-slowdown-gpio=2 --led-pwm-bits=8 -D 1 " + '"' + disp + '"')

                
def main():
        run()

if __name__ == "__main__":
        main()

