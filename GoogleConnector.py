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

    __googleService=None
    __port=None
    __clientSecret=None

    def __init__(self,OAuthPort,OauthClientSecretFile):
        self.googleService=None
        self.__port=OAuthPort
        self.__clientSecret=OauthClientSecretFile


    def AddEventToCalendar(self,calendarTitle,startTime, endTime, summary, location, description, reminders):
        if self.__googleService == None:
            self.__googleService = self.__connectToGoogleAndCreateService()
        
        calID = self.__addNewCalendarIfNotExists(self.__googleService,calendarTitle)

        self.__insertOrUpdateEvent(self.__googleService,calID,startTime, endTime, summary, location, description, reminders)


    def DropCalendars(self):
        service = self.__connectToGoogleAndCreateService()
        page_token = None

        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                try:
                    service.calendarList().delete(calendarId=calendar_list_entry['id']).execute()
                except:
                    pass
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break


    def __addNewCalendarIfNotExists(self,service,calendarTitle):
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


    def __insertOrUpdateEvent(self,service,calID,startTime, endTime, summary, location, description, reminders):
        eventId=None

        try: 
            eventId = self.__getEventIdIfExists(service,calID,summary,startTime,endTime)
        except Exception as e:
            print (e)
            pass

        event = self.__createCalEvent(startTime, endTime, summary, location, description, reminders)
        
        if eventId is None:
            try:
                print('Inserting event')
                event = service.events().insert(calendarId=calID, body=event).execute()
                print ('Event created: %s' % (event.get('htmlLink')))

            except HttpError as error:
                print('An error occurred: %s' % error)
        else:
            try:
                print('Updateing event')
                event = service.events().update(calendarId=calID,  eventId=eventId, body=event).execute()
                print ('Event created: %s' % (event.get('htmlLink')))

            except HttpError as error:
                print('An error occurred: %s' % error)

    def __getEventIdIfExists(self,service,calId,summary,startTime,endTime):
        tMin = datetime.now().isoformat() + 'Z'  # 'Z' indicates UTC time
        tMax= datetime.max.isoformat() + 'Z' 
       
        try:
            events_result = service.events().list(calendarId=calId, timeMin=tMin, timeMax=tMax, singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])
        except Exception as e:
            print(e)
            raise e

        if not events:
            return None

        else:
            for event in events:
                eventStart =datetime.fromisoformat(event['start']['dateTime'])
                if summary == event['summary'] and startTime == eventStart:
                    found = True
                    print('Event has been found.')
                    return event['id']

        return None

       
    def __createCalEvent(self, startTime, endTime, summary, location, description, reminders):
        eventReminders=None
        if len(reminders)>0:
            eventReminders={
            "reminders": {
                "useDefault": False,
                "overrides": []
                }}

            for reminder in reminders:
                override={
                    "method": 'popup',
                    "minutes": reminder 
                }
                eventReminders['reminders']['overrides'].append(override)

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': startTime.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
            'end': {
                'dateTime': endTime.isoformat(),
                'timeZone': 'Europe/Berlin',
            },    
            }
        if eventReminders is not None:
            event.update(eventReminders)
        return event


    def __connectToGoogleAndCreateService(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.__clientSecret, self.SCOPES)
                creds = flow.run_local_server(port=self.__port)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)
        return service



# #test
# class test:
#     def createCalEvent(seld,startTime, endTime, summary, location, description,reminders):
#         eventReminders=None
#         if len(reminders)>0:
#             eventReminders={
#             "reminders": {
#                 "useDefault": False,
#                 "overrides": []
#                 }}

#             for reminder in reminders:
#                 override={
#                     "method": 'popup',
#                     "minutes": reminder 
#                 }
#                 eventReminders['reminders']['overrides'].append(override)

#         event = {
#             'summary': summary,
#             'location': location,
#             'description': description,
#             'start': {
#                 'dateTime': startTime.isoformat(),
#                 'timeZone': 'Europe/Berlin',
#             },
#             'end': {
#                 'dateTime': endTime.isoformat(),
#                 'timeZone': 'Europe/Berlin',
#             },  
#             # "reminders": {
#             # "useDefault": False,
#             # # "overrides": [
#             # # {
#             # #     "method": string,
#             # #     "minutes": integer
#             # # }
#             # # ]
#             # },
#             "source": {
#                 "url": "www.aral.de",
#                 "title": "test"
#             },
#             }
#         if eventReminders is not None:
#             event.update(eventReminders)
#         return event

# t=test()
# reminders=[1,2,3]
# t.createCalEvent(datetime.now(), datetime.now(), "summary", "location", "description",reminders)