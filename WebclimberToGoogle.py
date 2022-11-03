#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from datetime import datetime
from pyvirtualdisplay import Display
from GoogleConnector import GoogleConnector
from webclimberCalParser import *
from logging.handlers import RotatingFileHandler
from Mehler import Mehler
import logging
import pytz

logFile = '/home/pi/webclimmer/log/webclimmer.log'
myOAuthPort=8105
myOauthClientSecretFile="/home/pi/webclimmer/dreaminginreverse/client_secret.json"
mySettingsFile='/home/pi/webclimmer/dreaminginreverse/creds.json'
mehlerSettingsFile='/home/pi/webclimmer/dreaminginreverse/mehlersettings.json'
token="/home/pi/webclimmer/dreaminginreverse/token.json"
GreiKalenderPrefix="Kurskalender "

log_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,backupCount=5, encoding=None, delay=0)
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s','%Y-%m-%d %H:%M:%S')
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

logger.info('Batman begins')
display = Display(visible=0, size=(800, 600))
davScraper= WebclimberInternalScraper(logger,mySettingsFile)
mehler = Mehler(logger,mehlerSettingsFile)

try:
    display.start()

    start=datetime.now()
    utc=pytz.UTC
    now = utc.localize(datetime.now()) 

    heySiri= GoogleConnector(logger,myOAuthPort,myOauthClientSecretFile,token)
    
    # heySiri.DropCalendars()
    logger.info("start webclimming")
    courseEvents=davScraper.ParseAll()
    logger.info("webclimming done")
    for course in courseEvents:
        if course.Start < now:
            logger.info("das event war schon")
            continue
        course.Description = course.Description+ '\nStand: ' + start.strftime("%d.%m.%Y %H:%M")
        heySiri.AddEventToCalendar(GreiKalenderPrefix + course.Teacher, course.Start, course.End, course.Summary, course.Location, course.Description, course.Reminders)

    logger.info("done:"+str(datetime.now()-start))    
except Exception:
        logger.fatal("Shit. There is really going on some big shit!", exc_info=True)
        mehler.send(['florian-huber@posteo.de'], 'Weblimmer - Fehler','War klar dass es nicht ewig geht. Log checken. ',logFile)

davScraper.dispose()

display.stop()
