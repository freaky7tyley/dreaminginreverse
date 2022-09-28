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
    _myCalendar=None
    def __init__(self,OAuthPort,OauthClientSecretFile,myCalendar):
        self.googleService=None
        self.calID=None
        self._port=OAuthPort
        self._clientSecret=OauthClientSecretFile
        self._myCalendar=myCalendar

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
            self._calID = self._addNewCalendarIfNotExists(self._googleService,self._myCalendar)

        self._insertEventToGoogleCalendar(self._googleService,self._calID,start,end,title,location,url,id)

