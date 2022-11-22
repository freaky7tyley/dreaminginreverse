from __future__ import print_function

from datetime import datetime
import httplib2
import os

from apiclient import discovery
from google.oauth2 import service_account

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']

def printEvents(service,calId):
    tMin = datetime.now().isoformat() + 'Z'  # 'Z' indicates UTC time
    tMax= datetime.max.isoformat() + 'Z' 
        

    events_result = service.events().list(calendarId=calId, timeMin=tMin, timeMax=tMax, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return None
    else:
        for event in events:
            print(event['summary'])


def addNewCalendarIfNotExists(service,calendarTitle):
    page_token = None

    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print(calendar_list_entry['summary'])
            if calendar_list_entry['summary'] == calendarTitle:
                print('Calendar exists: %s ' %calendar_list_entry['id'])
                return calendar_list_entry['id']
            page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    new_calendar = {
    'summary': calendarTitle,
    'timeZone': 'Europe/Berlin'
    }
    created_calendar = service.calendars().insert(body=new_calendar).execute()
    print('Calendar created: %s' %calendar_list_entry['id'])
    return created_calendar['id']


try:
    secret_file = os.path.join(os.getcwd(), 'client_secret.json')
    credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=SCOPES) 
    service = build('calendar', 'v3', credentials=credentials)
    id=addNewCalendarIfNotExists(service,'Kurskalender Flo Huber')
    printEvents(service,id)
except Exception as e:
    print(e) 