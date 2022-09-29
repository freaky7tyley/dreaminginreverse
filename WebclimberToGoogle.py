#!/usr/bin/env python 
#-*- coding: utf-8 -*-

from calendar import calendar
from twill.commands import *
from datetime import datetime

from GoogleConnector import GoogleConnector
from WebclimberScraper import WebclimberScraper

url='https://157.webclimber.de/de/courseBooking'

iAm = None#'Simon R.'#Flo H.'
# hashtag umleitungsuriport oderso
myOAuthPort=8105
myOauthClientSecretFile="client_secret.json"

myGreiKalender=None#"cocoburgh"

if iAm is not None and myGreiKalender is None:
    raise Exception('myGreiKalender ist nicht angegeben') 

heySiri= GoogleConnector(myOAuthPort,myOauthClientSecretFile)
davScraper= WebclimberScraper(url)
# heySiri.DropCalendars()

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
        availableSlots=davScraper.getAvailableSlots(course)
        try:
            availableSlots=int(availableSlots)
        except:
            continue

        if iAm is None or iAm == teacher:
            dates=davScraper.getDates(course)
            # print("Kurs: ",course,dates)
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
                        print('############################')
                        print('Teacher:\t',teacher)
                        print('ID:\t\t',cId)
                        print('text:\t\t',text)
                        print('date:\t\t',parsed_date)
                        print('dur:\t\t',DurationHours)
                        print('slots:\t\t',availableSlots)
                        print('url:\t\t',courseURL)

                
                        if iAm is None:
                            calendarName='Kurskalender '+teacher
                        else:
                            calendarName=myGreiKalender

                        heySiri.AddGreiEventToCalendar(calendarName,parsed_date,DurationHours,text,availableSlots,courseURL,cId)
                        
                        id_suffix=id_suffix+1

    print('--------------------------------------------------------------')