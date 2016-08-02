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
        items = []
        variables = []
        json = self.__getSpidersExecCommand__(cf.get("spider", "spider_name"))
        text = demjson.decode(json)
        dataDemo.__setTableName__(text.get('tableName'))
        dataDemo.__setPrimaryKey__(text.get('primaryKey'))
        dataDemo.__setURL__(text.get('URL'))
        dataDemo.__setTask__(text.get('task'))
        for item in text.get('items'):
            items.append(demjson.decode(demjson.encode(item)))
            dataDemo.__setItems__(items)
        for variable in text.get('variables'):
            variables.append(demjson.decode(demjson.encode(variable)))
        dataDemo.__setVariables__(variables)
        return dataDemo

    def getJsonString(self, spiders_exec_id):
        db = MySQLdb.connect(cf.get("db", "db_host"), cf.get("db", "db_user"), cf.get("db", "db_pass"),
                             cf.get("db", "db_name"), charset=cf.get("db", "db_charset"))
        cursor = db.cursor()
        sql = "SELECT " + cf.get("spider", "spiders_exec_command") + " FROM " + cf.get("spider",
                                                                                       "spiders_exec_tab") + " WHERE " + cf.get(
            "spider", "spiders_exec_id") + " = '%s'" % (spiders_exec_id)
        try:
            cursor.execute(sql)
            data = cursor.fetchone()
            return data[0]
        except:
            db.rollback()
        db.close()

    def __getDataDemoFromString__(self, jsonStr, league_dic=None):
        self.crawlerTime = datetime.datetime.now()
        dataDemo = jsonDataDemo()
        items = []
        variables = []
        path_variables = []
        chirdrenObjs = []
        text = demjson.decode(jsonStr)
        dataDemo.__setTableName__(text.get('tableName'))
        dataDemo.__setPrimaryKey__(text.get('primaryKey'))
        # replace DataTime to Now
        startUrl = text.get('URL')
        startUrl = startUrl.replace("##year", str(self.crawlerTime.year))
        startUrl = startUrl.replace("##month", str(self.crawlerTime.month))
        startUrl = startUrl.replace("##day", str(self.crawlerTime.day))
        startUrl = startUrl.replace("##hour", str(self.crawlerTime.hour))
        startUrl = startUrl.replace("##minute", str(self.crawlerTime.minute))
        startUrl = startUrl.replace("##second", str(self.crawlerTime.second))
        if league_dic is not None:
            startUrl = startUrl.replace("LeagueType", league_dic['leagueType'])
            startUrl = startUrl.replace("LeagueSeason", league_dic['season'])
            startUrl = startUrl.replace("LeagueId", league_dic['leagueId'])
        try:
            startUrl = startUrl.replace(text['pathVariables'][0]['flag'], str(text['pathVariables'][0]['min']))
        except Exception, e:
            pass

        if 'items' in text:
            for item in text.get('items'):
                items.append(demjson.decode(demjson.encode(item)))
                dataDemo.__setItems__(items)
        else:
            text['items'] = []

        if 'variables' in text:
            for variable in text.get('variables'):
                variables.append(demjson.decode(demjson.encode(variable)))
        else:
            text['variables'] = []

        if 'chirdren' in text:
            for chirdren in text.get('chirdren'):
                chirdrenJson = json.dumps(chirdren)
                chirdrenObj = self.__getDataDemoFromString__(chirdrenJson)
                chirdrenObjs.append(chirdrenObj)
        else:
            text['chirdren'] = []

        if 'pathVariables' in text:
            for pathVariable in text.get('pathVariables'):
                path_variables.append(demjson.decode(demjson.encode(pathVariable)))
        else:
            text['pathVariables'] = []

        dataDemo.__setVariables__(variables)
        dataDemo.__setPathVariables__(path_variables)
        dataDemo.__setChirdren__(chirdrenObjs)
        dataDemo.__setURL__(startUrl)
        dataDemo.__setTask__(text.get('task'))
        return dataDemo

    def __getSpidersExecCommand__(self, spiders_exec_id):
        db = MySQLdb.connect(cf.get("db", "db_host"), cf.get("db", "db_user"), cf.get("db", "db_pass"),
                             cf.get("db", "db_name"), charset=cf.get("db", "db_charset"))
        cursor = db.cursor()
        sql = "SELECT " + cf.get("spider", "spiders_exec_command") + " FROM " + cf.get("spider",
                                                                                       "spiders_exec_tab") + " WHERE " + cf.get(
            "spider", "spiders_exec_id") + " = '%s'" % (spiders_exec_id)
        try:
            cursor.execute(sql)
            data = cursor.fetchone()
            return data[0]
        except:
            db.rollback()
        db.close()
