#!/usr/bin/env python 
#-*- coding: utf-8 -*-

#import json
#import sys
#import urllib,requests
from pprint import pprint
import logging, datetime
import time
import pathlib
import re
from twill import browser
from twill.commands import *
from bs4 import BeautifulSoup
import array 
import os
from tqdm import tqdm

from icalendar import Calendar, Event
import pytz, os
from datetime import datetime, timedelta

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
iAm = 'Flo H.'#'Johannes L.'
myMail='florian.huber@kwpsoftware.de'

url ='https://157.webclimber.de/de/courseBooking'
teachers = []

def EventExists(service,summary,id):
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    tMax=datetime.utcnow().replace(month=datetime.now().month+3).isoformat()+ 'Z' 
    
    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=tMax, singleEvents=True, orderBy='startTime').execute()
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



def insertEventToGoogleCalendar(calID,starttime,endtime,summary,location,description,id):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        if EventExists(service,summary,id):
            return
        # Call the Calendar API
        print('Inserting event')


        event = {
        'summary': summary,
        'location': location,
        'description': description+'\nKursnummer: '+id,
        'start': {
            'dateTime': starttime.isoformat(),#'2022-05-10T09:00:00-07:00',
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': endtime.isoformat(),#str(endtime),#'2022-05-10T17:00:00-07:00',
            'timeZone': 'Europe/Berlin',
        },
        # 'attendees': [
        #     {'email': 'lpage@example.com'},
        #     {'email': 'sbrin@example.com'},
        # ],
        # 'reminders': {
        #     'useDefault': False,
        #     'overrides': [
        #     {'method': 'email', 'minutes': 24 * 60},
        #     {'method': 'popup', 'minutes': 10},
        #     ],
        #},
        }

        event = service.events().insert(calendarId=calID, body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print('An error occurred: %s' % error)


def build_event_duration(summary, description, start, duration, location, url):
        #freq_of_recurrence, until):

    '''
    Return an event that can be added to a calendar

    summary: summary of the event
    description: description of the event
    location: self explanatory
    start, end, stamp: These are datetime.datetime objects
    freq_of_recurrence: frequency of recurrence, string which can take the
    values daily, weekly, monthly, etc.
    until: A datetime.datetime object which signifies when the recurrence will
    end
    '''

    event = Event()
    event.add('summary', summary)
    event.add('description', description)
    event.add('dtstart', start)
    event.add('duration', timedelta(hours=duration))
    event.add('dtstamp', datetime.now())
    event.add('location', location)
    event.add('url', url)
    #event.add('rrule', { 'FREQ': freq_of_recurrence, 'UNTIL': until})

    return event

    
def AddToGoogleCalendar(calID,start,duration_hours,title,url,id):
    location="DAV Kletterzentrum Landshut, Ritter-von-Schoch Str.6, 84036 Landshut",
    end = start + timedelta(hours = duration_hours)
    insertEventToGoogleCalendar(calID,start,end,title,location,url,id)


def getSoup(url):
    browser.go(url)
    html=browser.dump
    soup = BeautifulSoup(html,features="lxml")
    return soup

def getOddEven(soup):
    return soup.find_all(class_="odd") + soup.find_all(class_="even")

def getTable(soup,tableattribute):
    data = []
    table = soup.find('table', attrs={'class':tableattribute})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        #print(row)
        cols = row.find_all('td') 
        #for ele in cols:
         #   print((ele.get_text(separator="\n")))
        cols = [ele.get_text(separator="\n").strip() for ele in cols]
        #cols = [ele.text.strip() for ele in cols]
        try:
            cols.append(row.find("a", href=True)["href"].rpartition("?")[0])
        except:
            pass
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    return data

def getCourseTypes(soup):
    courseTypes = getTable(soup,"items table table-striped table-hover")
    #courseTypes = getOddEven(soup)
    #print(len(courseTypes), "courseTypes")
    return courseTypes

def getCourses(courseTypyUrl):
    soup = getSoup(courseTypyUrl)
    courses = getTable(soup,'items table table-striped table-hover table-condensed')
    #print(len(courses), "coursecoursesTypes")
    return courses

def getTeacher(course):
    teacher = course[len(course)-3]
    return teacher

def addTeacher(course):
    teacher = course[len(course)-3]
    if teacher not in teachers:
        teachers.append(teacher)

def getDates(course):
    dates = course[1].split('\n')
    return dates

soup = getSoup(url)
courseTypes = getCourseTypes(soup)

# for courseType in courseTypes:
#     text = courseType[0]
#     amount = int(courseType[1])
#     link = courseType[2]

#     if amount < 1:
#         continue 

#     courses = getCourses(link)
#     for course in courses:
#         #print(course)
#         addTeacher(course)
#     #print('--------------------------------------------------------------')

# print('teachers',teachers)

for courseType in courseTypes:
    text = courseType[0]
    amount = int(courseType[1])
    link = courseType[2]
    courseURL = url + link.replace('/de/courseBooking','')
    if amount < 1:
        continue 

    #print(text,link)

    courses = getCourses(link)

    for course in courses:
        #print(course)
        print(getTeacher(course))
        if iAm == getTeacher(course):
            print("Kurs: ",course,getDates(course))
            id=course[0]
            id_suffix=0
            for date in getDates(course):
                crapdata=date.replace(' ','').split(',')
                #print(crapdata)
                parsed_date = None
                DurationHours=0
                for myDate in crapdata:
                    try:
                        parsed_date = datetime.strptime(myDate, '%d.%m.%Y')
                    except:
                        pass
                    if '-' in myDate:
                        times = myDate.split('-')
                        hour_start=int(times[0].split(':')[0])
                        minute_start=int(times[0].split(':')[1])
                        hour_stop=int(times[1].split(':')[0])
                        minute_stop=int(times[1].split(':')[1])
                        parsed_date = parsed_date.replace(hour=hour_start, minute=minute_start)
                        DurationHours = (int(hour_stop)-int(hour_start)) + (int(minute_stop)-int(minute_start))/60
                        cId=id+'_'+str(id_suffix)
                        print(cId,text,parsed_date,DurationHours,courseURL)
                        AddToGoogleCalendar(myMail,parsed_date,DurationHours,text,courseURL,id)
                        id_suffix=id_suffix+1
    print('--------------------------------------------------------------')