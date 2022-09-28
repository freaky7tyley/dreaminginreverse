#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from twill import browser
from twill.commands import *
from bs4 import BeautifulSoup

class WebclimberScraper:
    _url=None

    def __init__(self,url):
        self._url=url

    def getSoup(self):
        return self._getSoup(self._url)    
    
    def _getSoup(self,url):
        browser.go(url)
        html=browser.dump
        soup = BeautifulSoup(html,features="lxml")
        
        return soup

    def _getTable(self,soup,tableattribute):
        data = []
        table = soup.find('table', attrs={'class':tableattribute})
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td') 
            cols = [ele.get_text(separator="\n").strip() for ele in cols]
            
            try:
                cols.append(row.find("a", href=True)["href"].rpartition("?")[0])
            except:
                pass
            
            data.append([ele for ele in cols if ele]) # Get rid of empty values
        return data

    def getCourseTypes(self,soup):
        courseTypes = self._getTable(soup,"items table table-striped table-hover")
        return courseTypes

    def getCourses(self,courseTypyUrl):
        soup = self._getSoup(courseTypyUrl)
        courses = self._getTable(soup,'items table table-striped table-hover table-condensed')
        return courses

    def getTeacher(self,course):
        teacher = course[len(course)-3]
        return teacher

    def getAvailableSlots(self,course):
        slots = course[len(course)-2]
        return slots

    def getDates(self,course):
        dates = course[1].split('\n')
        return dates

    def SetDateAndDurationHours(self,parsed_date, times):
        hour_start=int(times[0].split(':')[0])
        minute_start=int(times[0].split(':')[1])
        hour_stop=int(times[1].split(':')[0])
        minute_stop=int(times[1].split(':')[1])
                        
        parsed_date = parsed_date.replace(hour=hour_start, minute=minute_start)
        DurationHours = (int(hour_stop)-int(hour_start)) + (int(minute_stop)-int(minute_start))/60

        return parsed_date,DurationHours
