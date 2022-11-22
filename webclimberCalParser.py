#!/usr/bin/env python
#-*- coding: utf-8 -*-

from icalendar import Calendar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import urllib.request
import json
import time
from datetime import datetime

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
    Ultimatum=None

class WebclimberInternalScraper:
    __logger=None
    __driver=None
    __webclimberSubscribers=None
    __settingsFile=None


    def __init__(self,logger,settingsFile):
        self.__settingsFile=settingsFile
        self.__logger=logger    
        
    def ParseAll(self):
        self.__login()
        calEvents=[]
        for subscriber in self.__webclimberSubscribers:
            self.__logger.info(subscriber['calUrl'])
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
            event.Ultimatum=self.__fetchAnmeldefrist(event.Url)
            event.Description=self.__getDescription(event)
            courseEvents.append(event)

        return courseEvents


    def __getDescription(self,event):
        text= event.BookedPersons + '\n' + event.Url
        if event.Ultimatum is None:
            return text
        if event.Ultimatum < datetime.now():
            text += '\nAnmeldefrist abgelaufen.' 
        else:
            text += '\nAnmeldungen bis '+event.Ultimatum.strftime("%d.%m.%Y %H:%M")
        return text


    def __login(self):
        username, password = self.__readSettingsFile()
        loginUrl=self.__getLoginUrl(self.__webclimberSubscribers[0]['calUrl'])
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless=True
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox") # linux only
        chrome_options.headless = True
        try:
            # self.__driver = webdriver.Firefox(options=fireFoxOptions)
            self.__driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            self.__logger.error(e)

        self.__driver.get(loginUrl)
        self.__driver.implicitly_wait(10)

        self.__driver.find_element("id", "LoginForm_username").send_keys(username)
        self.__driver.find_element("id","LoginForm_password").send_keys(password)
        self.__driver.find_element("name","yt0").click()

        time.sleep(5)


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
        teil=""
        drt= self.__driver.find_elements(By.CLASS_NAME,"control-group")
        self.__driver.implicitly_wait(0.1)
        for ctrl in drt:
            try:
                ctrl.find_element(By.CLASS_NAME,"memberCounter")
                teil=ctrl.text
            except:
                pass
        return teil


    def __fetchAnmeldefrist(self,url):
        self.__driver.get(url)
        drt= self.__driver.find_elements(By.CLASS_NAME,"control-group")
        self.__driver.implicitly_wait(0.1)
        for ctrl in drt:
            try:
                sub=ctrl.find_element(By.CLASS_NAME,"control-label")
                if "Anmeldefrist" in sub.text:
                    datum=ctrl.find_element(By.CLASS_NAME,"controls")
                    return datetime.strptime(datum.text, '%d.%m.%Y %H:%M:%S')
            except Exception as e:
                self.__logger.error(e)
        return None


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
            calEvent.Teacher = event.get('organizer')

            calEvents.append(calEvent)
            self.__logger.info(calEvent.Summary)

        return calEvents

    def dispose(self):
        return
        self.__driver.close()