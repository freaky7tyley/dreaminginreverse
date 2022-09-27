#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from pprint import pprint
from twill import browser
from twill.commands import *
from bs4 import BeautifulSoup

import os
from tqdm import tqdm

from icalendar import Calendar, Event
import  os
from datetime import datetime, timedelta

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleConnector:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']
    _googleService=None
    _calID=None
    _port=None
    _clientSecret=None

    def __init__(self,OAuthPort,OauthClientSecretFile):
        self.googleService=None
        self.calID=None
        self._port=OAuthPort
        self._clientSecret=OauthClientSecretFile

    def _addNewCalendarIfNotExists(self,service,calendarTitle):
        page_token = None

        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if calendar_list_entry['summary'] == calendarTitle:
                    return calendar_list_entry['id']
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        new_calendar = {
        'summary': calendarTitle,
        'timeZone': 'Europe/Berlin'
        }
        created_calendar = service.calendars().insert(body=new_calendar).execute()

        return created_calendar['id']

    def _EventExists(self,service,calId,summary,id):
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        tMax=datetime.utcnow().replace(month=datetime.now().month+3).isoformat()+ 'Z' 
        
        events_result = service.events().list(calendarId=calId, timeMin=now, timeMax=tMax, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        found = False
        if not events:
            print('Event does not exist yet.')
        else:
            for event in events:
                if summary == event['summary'] and id in event['description']:
                    found = True
                    print('Event has been found.')
                    break
            if found != True:
                print('Event does not exist yet.')
        return found

    def _insertEventToGoogleCalendar(self,service,calID,starttime,endtime,summary,location,description,id):
        try:
            if self._EventExists(service,calID,summary,id):
                return
        except:
            pass
        
        event = self._CreateCalEvent(starttime, endtime, summary, location, description, id)
        
        try:
            print('Inserting event')
            event = service.events().insert(calendarId=calID, body=event).execute()
            print ('Event created: %s' % (event.get('htmlLink')))

        except HttpError as error:
            print('An error occurred: %s' % error)

    def _CreateCalEvent(self,starttime, endtime, summary, location, description, id):
        return {
            'summary': summary,
            'location': location,
            'description': description+'\nKursnummer: '+id,
            'start': {
                'dateTime': starttime.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
            'end': {
                'dateTime': endtime.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
            }

    def _ConnectToGoogleAndCreateService(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._clientSecret, self.SCOPES)
                creds = flow.run_local_server(port=self._port)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)
        return service

    def AddGreiEventToCalendar(self,start,duration_hours,title,url,id):
        location="DAV Kletterzentrum Landshut, Ritter-von-Schoch Str.6, 84036 Landshut",
        end = start + timedelta(hours = duration_hours)

        if self._googleService == None:
            self._googleService = self._ConnectToGoogleAndCreateService()
            self._calID = self._addNewCalendarIfNotExists(self._googleService,myGreiKalender)

        self._insertEventToGoogleCalendar(self._googleService,self._calID,start,end,title,location,url,id)

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

url='https://157.webclimber.de/de/courseBooking'

iAm = 'Flo H.'
# hashtag umleitungsuriport oderso
myOAuthPort=8105
myOauthClientSecretFile="client_secret.json"

myGreiKalender="cocoburgh"

heySiri= GoogleConnector(myOAuthPort,myOauthClientSecretFile)
davScraper= WebclimberScraper(url)

soup = davScraper.getSoup()
courseTypes = davScraper.getCourseTypes(soup)

for courseType in courseTypes:
    text = courseType[0]
    amount = int(courseType[1])
    link = courseType[2]
    
    courseURL = url + link.replace('/de/courseBooking','')
    
    if amount < 1:
        continue 

    courses =  davScraper.getCourses(link)

    for course in courses:
        
        teacher= davScraper.getTeacher(course)
        print(teacher)
        if iAm == teacher:
            dates=davScraper.getDates(course)
            print("Kurs: ",course,dates)
            id=course[0]
            id_suffix=0
            
            for date in dates:
                
                crapdata=date.replace(' ','').split(',')
                parsed_date = None
                DurationHours=0
                
                for myDate in crapdata:
                    try:
                        parsed_date = datetime.strptime(myDate, '%d.%m.%Y')
                    except:
                        pass
                    if '-' in myDate:
                        times = myDate.split('-')
                        
                        parsed_date, DurationHours = davScraper.SetDateAndDurationHours(parsed_date, times)
                        
                        cId=id+'_'+str(id_suffix)
                        
                        print(cId,text,parsed_date,DurationHours,courseURL)
                    
                        heySiri.AddGreiEventToCalendar(parsed_date,DurationHours,text,courseURL,cId)
                        
                        id_suffix=id_suffix+1

    print('--------------------------------------------------------------')