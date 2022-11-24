#!/usr/bin/env python 
#-*- coding: utf-8 -*-

import sqlite3 as db
import os


class sqliteConnector:
    dataBase='my-test.db'
    con=None

    def __init__(self,DataBaseName):
        self.dataBase=DataBaseName

    def DbExits(self):
        return os.path.isfile(self.dataBase)

    def Connect(self):
        self.con = db.connect(self.dataBase)

    def Execute(self,sqlStatement):
            with self.con:
                return self.con.execute(""+sqlStatement+"")

    def ExecuteWithParameters(self,sql,*data):
            with self.con:
                return self.con.execute(sql, data)

    def Close(self):
        self.con.close()

class WebclimberDataBaseConnector(sqliteConnector):
    
    UserTableName="User"

    def __init__(self,DataBaseName):
        sqliteConnector.__init__(self,DataBaseName)
        if not self.DbExits():
            self.Connect()
            self.Execute("CREATE TABLE "+self.UserTableName+" (name TEXT NOT NULL PRIMARY KEY,calendarUrl TEXT NOT NULL ,eMailAddress TEXT NOT NULL );")
            self.Close()
    
    def AddUser(self,Name,calUrl,eMail):
        data = [(Name,calUrl,eMail)]
        self.Connect()
        try:
            self.ExecuteWithParameters("INSERT INTO "+self.UserTableName+" (name,calendarUrl,eMailAddress) VALUES(?, ?, ?);",Name,calUrl,eMail)
        except Exception as e:
            print("AddUser failed.",Name,calUrl,eMail,e)

        self.Close()
    
    def ReadUsersEmail(self,Name):
        self.Connect()
        data=self.ExecuteWithParameters("SELECT eMailAddress FROM "+self.UserTableName+" WHERE name = '"+Name+"';").fetchone()
        self.Close()
        return data[0]
    
    def ReadUsersCalUrl(self,Name):
        self.Connect()
        data=self.ExecuteWithParameters("SELECT calendarUrl FROM "+self.UserTableName+" WHERE name = '"+Name+"';").fetchone()
        self.Close()
        return data[0]
    
    def LoadAllUsers(self):
        self.Connect()
        data=self.ExecuteWithParameters("SELECT * FROM "+self.UserTableName+";").fetchall()
        self.Close()
        return data


climmer=WebclimberDataBaseConnector("Webclimber.Db")
climmer.AddUser("Hans","einerulq30948203685032850385ß245","hans@hans.de")
climmer.AddUser("Huber","einerulq30948203685032850385ß245","hans@hans.de")

users = climmer.LoadAllUsers()
for u in users:
    print (u)

print(climmer.ReadUsersEmail("Hans"),climmer.ReadUsersCalUrl("Hans"))