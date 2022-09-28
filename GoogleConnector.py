#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from twill.commands import *
import os
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
    location="DAV Kletterzentrum Landshut, Ritter-von-Schoch Str.6, 84036 Landshut"

    _googleService=None
    _port=None
    _clientSecret=None

    def __init__(self,OAuthPort,OauthClientSecretFile):
        self.googleService=None
        self.calID=None
        self._port=OAuthPort
        self._clientSecret=OauthClientSecretFile

    def AddGreiEventToCalendar(self,teacher,start,duration_hours,title,slots,url,id):
        
        end = start + timedelta(hours = duration_hours)

        if self._googleService == None:
            self._googleService = self._ConnectToGoogleAndCreateService()
        
        calID = self._addNewCalendarIfNotExists(self._googleService,teacher)

        self._insertEventToGoogleCalendar(self._googleService,calID,start,end,title,slots,url,id)


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


    def _insertEventToGoogleCalendar(self,service,calID,starttime,endtime,summary,slots,url,id):
        try:
            if self._EventExists(service,calID,summary,id):
                return
        except:
            pass
        
        event = self._CreateCalEvent(starttime, endtime, summary, slots, url, id)
        
        try:
            print('Inserting event')
            event = service.events().insert(calendarId=calID, body=event).execute()
            print ('Event created: %s' % (event.get('htmlLink')))

        except HttpError as error:
            print('An error occurred: %s' % error)


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


    def _CreateCalEvent(self,starttime, endtime, summary, slots, url, id):
        return {
            'summary': summary,
            'location': self.location,
            'description': 'Freie Plätze: '+slots +'\n'+url+'\nKursnummer: '+id,
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



