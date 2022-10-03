#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from datetime import datetime
import pytz
from icalendar import Calendar, Event, vCalAddress, vText
import urllib.request
from twill import browser
from twill.commands import *
from bs4 import BeautifulSoup
import re
import requests

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json

# terminal safaridriver --enable

class WebclimberCalEvent:
    Id=None
    Start=None
    End=None
    Summary=None
    Location="DAV Kletterzentrum Landshut, Ritter-von-Schoch Str.6, 84036 Landshut"
    Description=None
    Url=None
    Teacher=None
    Reminders=[]

class CourseEvent(WebclimberCalEvent): 
    BookedPersons=None

class WebclimberInternalScraper:
    __driver=None
    __webclimberSubscribers=None 
    __settingsFile=None

    def __init__(self,settingsFile):
        self.__settingsFile=settingsFile


    def ParseAll(self):
        self.__login()
        calEvents=[]
        for subscriber in self.__webclimberSubscribers:
            subscriberEvents=self.__getCalendarEvents(subscriber['calUrl'])
            for event in subscriberEvents:
                event.Reminders=subscriber['reminderMinutesBevore']
            calEvents.extend(subscriberEvents)

        courseEvents=self.__updateEventsWithBookedPersons(calEvents)
        self.__driver.close()

        return courseEvents


    def __updateEventsWithBookedPersons(self, calEvents):
        courseEvents=[]

        for event in calEvents:
            event.__class__=CourseEvent
            event.BookedPersons=self.__fetchTeilnehmer(event.Url)
            event.Description=self.__getDescription(event)
            courseEvents.append(event)
        
        return courseEvents


    def __getDescription(self,event):
        return event.BookedPersons + '\n' + event.Url


    def __login(self):
        username, password = self.__readSettingsFile()

        loginUrl=self.__getLoginUrl(self.__webclimberSubscribers[0]['calUrl'])

        self.__driver = webdriver.Safari()
        self.__driver.get(loginUrl)
        self.__driver.implicitly_wait(10)

        self.__driver.find_element("id", "LoginForm_username").send_keys(username)
        self.__driver.find_element("id","LoginForm_password").send_keys(password)
        self.__driver.find_element("name","yt0").click()

        sleep(5)    
        

    def __readSettingsFile(self):
        f = open(self.__settingsFile)
        data = json.load(f)
        username=data['username']
        password=data['password']
        self.__webclimberSubscribers=data['webclimberSubscribers']
        f.close()

        return username,password
    

    def __getLoginUrl(self,webclimberCalUrl):
        return webclimberCalUrl[0:(webclimberCalUrl.find('course'))]+'login'
    

    def __fetchTeilnehmer(self,url):

        self.__driver.get(url)
        
        # table = self.__driver.find_element(By.ID,"yw0")
        # teil=table.text
        teil=""
        drt= self.__driver.find_elements(By.CLASS_NAME,"control-group")
        self.__driver.implicitly_wait(0.1)
        for ctrl in drt:
            try:
                ctrl.find_element(By.CLASS_NAME,"memberCounter")
                teil=ctrl.text
            except:
                pass
        # next(f for f in drt if f..startswith("p"))
        return teil       
        # teilnehmer = re.search("Teilnehmer:([\s\S]*?)Teilnehmer", teil).group()
        # return teilnehmer


    def __getCalendarEvents(self,url):
        resp = urllib.request.urlopen(url)
        data = resp.read()

        calEvents=[]

        cal  = Calendar.from_ical(data)
        
        for event in cal.walk('vevent'):
            calEvent=WebclimberCalEvent()
            calEvent.Start = event.get('dtstart').dt
            calEvent.End = event.get('dtend').dt

            summaryData=event.get('summary').strip().rpartition(' ')
            calEvent.Summary = summaryData[0]
            calEvent.Id = summaryData[2]

            calEvent.Url = event.get('url')
            calEvent.Description = ""
            calEvent.Teacher = event.get('organizer')#event.get('description')
            
            calEvents.append(calEvent)

        return calEvents



# dummy=WebclimberInternalScraper('creds.json')
# dummy.ParseAll()

# for i in range(59, 200):
#     id=str(i)
#     calurl='https://157.webclimber.de/de/course/ical/'+id+'?period=6&reminder=0'#&key=72cf0077ac2b67a0befc14c2278cf592'
#     try:
#         calEvents= dummy.GetEvents(calurl)
#         print(id +': '+calEvents[0].Teacher)
#     except:
#         print(id +'gibts ned')
    