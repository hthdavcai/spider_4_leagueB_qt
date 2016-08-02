# -*- coding: utf-8 -*-
import demjson
import MySQLdb
from dirbot.jsonDataDemo import jsonDataDemo
import ConfigParser
import json
import datetime
cf = ConfigParser.ConfigParser()
cf.read("platinfo.cfg")

class DataDemoUtil:
    def __getDataDemo__(self): 
        dataDemo = jsonDataDemo()
        items =[]
        variables =[]
        json = self.__getSpidersExecCommand__(cf.get("spider", "spider_name"))
        text = demjson.decode(json)
        dataDemo.__setTableName__('tableName',text.get('tableName'))
        dataDemo.__setPrimaryKey__('primaryKey',text.get('primaryKey'))
        dataDemo.__setURL__('URL',text.get('URL'))
        dataDemo.__setTask__('task',text.get('task'))
        for item in text.get('items'):
            items.append(demjson.decode(demjson.encode(item)))      
            dataDemo.__setItems__('items',items)
        for variable in text.get('variables'):
            variables.append(demjson.decode(demjson.encode(variable)))
        dataDemo.__setVariables__('variables',variables)
        return dataDemo

    def getJsonString(self,spiders_exec_id): 
        db = MySQLdb.connect(cf.get("db", "db_host"),cf.get("db", "db_user"),cf.get("db", "db_pass"),cf.get("db", "db_name"),charset=cf.get("db", "db_charset") )
        cursor = db.cursor()
        sql = "SELECT "+cf.get("spider", "spiders_exec_command")+" FROM "+cf.get("spider", "spiders_exec_tab")+" WHERE "+cf.get("spider", "spiders_exec_id") +" = '%s'" % (spiders_exec_id)
        try:
            cursor.execute(sql)
            data = cursor.fetchone()
            return data[0]
        except:
            db.rollback()
        db.close() 
    
    def __getDataDemoFromString__(self,jsonStr): 
        self.crawlerTime = datetime.datetime.now()
        dataDemo = jsonDataDemo()
        items =[]
        variables =[]
        text = demjson.decode(jsonStr)
        dataDemo.__setTableName__('tableName',text.get('tableName'))
        dataDemo.__setPrimaryKey__('primaryKey',text.get('primaryKey'))
        # replace DataTime to Now
        startUrl = text.get('URL')
        startUrl = startUrl.replace("##year", str(self.crawlerTime.year))
        startUrl = startUrl.replace("##month", str(self.crawlerTime.month))
        startUrl = startUrl.replace("##day", str(self.crawlerTime.day))
        startUrl = startUrl.replace("##hour", str(self.crawlerTime.hour))
        startUrl = startUrl.replace("##minute", str(self.crawlerTime.minute))
        startUrl = startUrl.replace("##second", str(self.crawlerTime.second))
        
        dataDemo.__setURL__('URL',startUrl)
        
        dataDemo.__setTask__('task',text.get('task'))
        for item in text.get('items'):
            items.append(demjson.decode(demjson.encode(item)))
            dataDemo.__setItems__('items',items)
        for variable in text.get('variables'):
            variables.append(demjson.decode(demjson.encode(variable)))
        dataDemo.__setVariables__('variables',variables)
        
        chirdrenObjs = []
        for chirdren in text.get('chirdren'):
            chirdrenJson = json.dumps(chirdren)
            chirdrenObj = self.__getDataDemoFromString__(chirdrenJson)
            chirdrenObjs.append(chirdrenObj)
        dataDemo.__setChirdren__(chirdrenObjs)
        return dataDemo


    def __getSpidersExecCommand__(self,spiders_exec_id): 
        db = MySQLdb.connect(cf.get("db", "db_host"),cf.get("db", "db_user"),cf.get("db", "db_pass"),cf.get("db", "db_name"),charset=cf.get("db", "db_charset") )
        cursor = db.cursor()
        sql = "SELECT "+cf.get("spider", "spiders_exec_command")+" FROM "+cf.get("spider", "spiders_exec_tab")+" WHERE "+cf.get("spider", "spiders_exec_id") +" = '%s'" % (spiders_exec_id)
        try:
            cursor.execute(sql)
            data = cursor.fetchone()
            return data[0]
        except:
            db.rollback()
        db.close()    
     

