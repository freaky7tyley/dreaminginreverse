#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from calendar import calendar

from datetime import datetime

from GoogleConnector import GoogleConnector
from webclimberCalParser import *

# hashtag umleitungsuriport oderso
myOAuthPort=8105
myOauthClientSecretFile="client_secret.json"

GreiKalenderPrefix="Kurskalender "

heySiri= GoogleConnector(myOAuthPort,myOauthClientSecretFile)
davScraper= WebclimberInternalScraper('creds.json')
# heySiri.DropCalendars()

courseEvents=davScraper.ParseAll()

for course in courseEvents:
    heySiri.AddEventToCalendar(GreiKalenderPrefix + course.Teacher, course.Start, course.End, course.Summary, course.Location, course.Description)