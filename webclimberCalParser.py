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

class WebclimberInternalScraper:
    _driver=None
    loginUrl=None

    def __init__(self,loginUrl):
        self.loginUrl=loginUrl
    
    def Login(self):
        f = open('creds.json')
        data = json.load(f)
        username=data['username']
        password=data['password']
        f.close()

        self.driver = webdriver.Safari()
        self.driver.get(self.loginUrl)
        self.driver.implicitly_wait(60)
        self.driver.find_element("id", "LoginForm_username").send_keys(username)
        self.driver.find_element("id","LoginForm_password").send_keys(password)
        self.driver.find_element("name","yt0").click()
        sleep(5)

    def FetchTeilnehmer(self,url):
        self.driver.get(url)
        table = self.driver.find_element(By.ID,"yw0")
        teil=table.text
        teilnehmer = re.search("Teilnehmer:([\s\S]*?)Teilnehmer", teil).group()
        return teilnehmer


def calTest():
    scraper=WebclimberInternalScraper('https://157.webclimber.de/de/login')
    scraper.Login()
    resp = urllib.request.urlopen('https://157.webclimber.de/de/course/ical/59?period=6&reminder=0&key=72cf0077ac2b67a0befc14c2278cf592')
    data = resp.read()

    cal  = Calendar.from_ical(data)

    for event in cal.walk('vevent'):

        start = event.get('dtstart').dt
        end = event.get('dtend').dt
        summary = event.get('summary')
        url = event.get('url')
        description = event.get('description')
        trainer = event.get('organizer')
        teilnemer=scraper.FetchTeilnehmer(url)

        print (start)
        print (end)
        print (url)
        print (summary)
        print (description)
        print (trainer)
        print (teilnemer)
        print ('---------------------------------')


    return

calTest()