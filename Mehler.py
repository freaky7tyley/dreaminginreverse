#!/usr/bin/env python
#-*- coding: utf-8 -*-

import ssl
import smtplib
from zlib import Z_BEST_COMPRESSION
import pytz
import json
import os

from zipfile import ZIP_DEFLATED, ZipFile
from typing import List
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from email import utils
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

class Mehler:
    __HOST=None
    __USE_SSL=None
    __USERNAME=None
    __PASSWORD=None
    __SENDER=None
    __PORT=None

    def __init__(self,logger,settingsFile) -> None:
        self.__logger=logger
        try:
            self.__readSettingsFile(settingsFile)
        except Exception:
            self.__logger.error("Mehlerfehler! reading Settings failed. ", exc_info=True)


    def __readSettingsFile(self,settingsFile):
        f = open(settingsFile)
        data = json.load(f)

        self.__HOST     = data['host']
        self.__USE_SSL  = data['useSsl']
        self.__USERNAME = data['username']
        self.__PASSWORD = data['password']
        self.__SENDER   = data['emailAddress']
        self.__PORT = int(data['port'])
        
        f.close()
            

    def send(self, receivers:List[str], subject, text, attachement=None):
        print("send ead")
        message = MIMEMultipart()# MIMEText(text, 'plain', 'utf-8')

        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = f'radio-spy <{self.__SENDER}>'
        message['To'] = ", ".join(receivers)
        message['Date'] = utils.format_datetime(datetime.now(pytz.timezone('Europe/Berlin')))
        message['Message-ID'] = utils.make_msgid()
        message.attach(MIMEText(text, 'plain', 'utf-8'))
        archiveName=None

        if attachement is not None:
            archiveName=attachement+'.zip'
            zf=ZipFile(archiveName, mode='w', compression=ZIP_DEFLATED)
            zf.write(attachement, arcname=basename(attachement))
            zf.close()

            with open(archiveName, "rb") as file:
                part = MIMEApplication(file.read(),Name=basename(archiveName))

            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(archiveName)
            message.attach(part)

        try:
            if self.__USE_SSL:
                context = ssl.create_default_context()

                with smtplib.SMTP_SSL(self.__HOST, self.__PORT, context=context) as server:
                    server.login(self.__USERNAME, self.__PASSWORD)
                    server.sendmail(self.__SENDER, receivers, message.as_string())
            else:
                with smtplib.SMTP(self.__HOST, self.__PORT) as server:
                    server.login(self.__USERNAME, self.__PASSWORD)
                    server.sendmail(self.__SENDER, receivers, message.as_string())
                    
        except Exception:
            self.__logger.error("Mehlerfehler!", exc_info=True)

        if archiveName is not None:
            os.remove(archiveName)
