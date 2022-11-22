#!/usr/bin/env python 
#-*- coding: utf-8 -*-
#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from datetime import datetime

from GoogleConnector import GoogleConnector

from logging.handlers import RotatingFileHandler
from Mehler import Mehler
import logging
import pytz
import urllib.request
from icalendar import Calendar

logFile = '/home/pi/webclimmer/log/webclimmer.log'
logFile = 'webclimmer.log'
myOAuthPort=8105
myOauthClientSecretFile="/client_secret.json"
mySettingsFile='creds.json'
mehlerSettingsFile='mehlersettings.json'
token="token.json"
GreiKalenderPrefix="Kurskalender "

log_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,backupCount=5, encoding=None, delay=0)
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s','%Y-%m-%d %H:%M:%S')
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

logger.info('Batman rises')

class CalUrlChecker:
    __logger=None

    def __init__(self,logger):
        self.__logger=logger    

    def CalnameEquals(self,calUrl,name):
        self.__logger.info(calUrl)
        try:
            resp = urllib.request.urlopen(calUrl)
            data = resp.read()
            cal  = Calendar.from_ical(data)
            d=str(cal['X-WR-CALNAME'])
            return d==name
        except Exception:
            logger.error("Cal Name check error.", exc_info=True)
            return False


urlcheck=CalUrlChecker(logger)

#ok
print (urlcheck.CalnameEquals("https://157.webclimber.de/de/course/ical/95?period=6&reminder=0&key=6d5e4cc0407ab426723a749fb9d1862d",'Kurse [Freeclimber]'))

#nok
print (urlcheck.CalnameEquals("https://157.webclimber.de/de/course/ical/95?period=6&reminder=0&key=6d5e4cc0407ab426723a749fb9d1862d",'Kurse [Freeclidmber]'))
print (urlcheck.CalnameEquals("https://157.afsdfswebclimber.de/de/course/ical/95?period=6&reminder=0&key=6d5e4cc0407ab426723a749fb9d1862d",'Kurse [Freeclidmber]'))





heySiri= GoogleConnector(logger,myOAuthPort,myOauthClientSecretFile,token)
id=heySiri.CreateCalendarID("CalendarNameGoesHere")
heySiri.PrintACl(id)

heySiri.SetOwner(id,"srogge87@gmail.com")
heySiri.PrintACl(id)


id=heySiri.CreateCalendarID("Kurskalender Simon Rogge")
heySiri.PrintACl(id)
#