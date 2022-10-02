#!/usr/bin/env python 
#-*- coding: utf-8 -*-
import os

from twill.commands import *
from datetime import datetime
from dotenv import load_dotenv

from GoogleConnector import GoogleConnector
from WebclimberScraper import WebclimberScraper

# Load all environment variables from the .env file
load_dotenv()

url='https://157.webclimber.de/de/courseBooking'

iAm = os.environ.get('I_AM')
# hashtag umleitungsuriport oderso
myOAuthPort = int(os.environ.get('OAUTH_PORT'))
myOauthClientSecretFile = os.environ.get('OAUTH_CLIENT_SECRET_FILE')

myGreiKalender = int(os.environ.get(' '))

heySiri= GoogleConnector(myOAuthPort,myOauthClientSecretFile,myGreiKalender)
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