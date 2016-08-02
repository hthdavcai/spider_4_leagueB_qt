# -*- coding: UTF-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi              #导入twisted的包
import MySQLdb.cursors
from dirbot.DataDemoUtil import DataDemoUtil

#DataDemoUtil = DataDemoUtil() 
#dataDemo = DataDemoUtil.__getDataDemo__()  
import ConfigParser
cf = ConfigParser.ConfigParser()
cf.read("platinfo.cfg")

class MySQLStorePipeline(object):
    DataDemoUtil = DataDemoUtil()
    def __init__(self):                            #初始化连接mysql的数据库相关信息
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
          host = cf.get("db", "db_host"),                                 
          db = cf.get("db", "db_name"),
          user = cf.get("db", "db_user"),
          passwd = cf.get("db", "db_pass"),
          cursorclass = MySQLdb.cursors.DictCursor,
          charset = cf.get("db", "db_charset"),
          use_unicode = False
      )

    # pipeline dafault function                    #这个函数是pipeline默认调用的函数
    def process_item(self, item, spider):
        if item.has_key('###spiderConfigString###'):
            currentDataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil,item['###spiderConfigString###'])
        else:
            currentDataDemo = spider.getDataDemo()
        # go out to database OK
        self.dataDemo = currentDataDemo
        self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    # insert the data to databases                 #把数据插入到数据库中
    def _conditional_insert(self, tx, item):
        try:  
            classNameShort=str(self.dataDemo.__getTableName__())
            primaryKey =  str(self.dataDemo.__getPrimaryKey__())
            item_primaryKey = primaryKey.split(",")#
            item_primaryKey_o = []
            item_select_o = []
            colname_insert_o = []
            placeholder_insert_o = []
            item_insert_o = []
            itemNameValue = {}
            primyKeyHaveNull = 0
            for jsonitem in self.dataDemo.__getItems__():
                placeholder_insert_o.append('%s')
                colname_insert_o.append(str(jsonitem.get('name')))
                if '\'' in item[str(jsonitem.get('name'))]:
                    item[str(jsonitem.get('name'))] = item[str(jsonitem.get('name'))].replace('\'', '\\\'')
                item_insert_o.append("'"+item[str(jsonitem.get('name'))]+"'")
                # key value
                itemNameValue[str(jsonitem.get('name'))] = item[str(jsonitem.get('name'))]
            #add
            listNameWithOutPK = list(set(colname_insert_o) - set(item_primaryKey))
            for nameNoPKCount in range(len(listNameWithOutPK)):
                nameValue = listNameWithOutPK[nameNoPKCount]
                listNameWithOutPK[nameNoPKCount] = "`"+nameValue+"`" +'=' +"'"+itemNameValue[nameValue]+"'"
            listNoPKString = ",".join(listNameWithOutPK)
            colname_insert_o_y = []
            for item_insert_n_y in colname_insert_o:
                colname_insert_o_y.append('`'+item_insert_n_y+'`')
            colname_insert_n =  ",".join(colname_insert_o_y)
            colvalue_insert_v = ",".join(item_insert_o)#
            len_item_primaryKey = len(item_primaryKey)          
            for index  in range(len_item_primaryKey):
                itemPrimyKeyName = item_primaryKey[index]
                itemPrimyKeyValue = itemNameValue[itemPrimyKeyName]
                #print itemPrimyKeyValue
                if itemPrimyKeyValue == '':
                    primyKeyHaveNull = primyKeyHaveNull + 1
                if index < len_item_primaryKey - 1:
                    item_primaryKey_o.append(str(item_primaryKey[index])+'='+'%s and') 
                    item_select_o.append(item[str(item_primaryKey[index])])
                else:
                    item_primaryKey_o.append(str(item_primaryKey[index])+'='+"'%s'")
                    item_select_o.append(item[str(item_primaryKey[index])])   
            item_primaryKey_n = str(tuple(item_primaryKey_o)).replace("'","").replace(",","")
            if item_primaryKey_n and str(item_select_o).find('\'\'',0,len(str(item_select_o)))==-1:
                insert_sql = "insert into "+classNameShort+" ("+str(colname_insert_n)+") values(" + colvalue_insert_v+")"#placeholder_insert_n
                #on duplicate key update 
                insertORupdateSql = ''
                if len(listNameWithOutPK) == 0:
                    insertORupdateSql = insert_sql
                else:
                    insertORupdateSql = insert_sql +' on duplicate key update ' +  listNoPKString
                #print insertORupdateSql
                if primyKeyHaveNull == 0:
#                    print insertORupdateSql
                    tx.execute(insertORupdateSql) #item_insert_o
                else:
                    print 'primyKey Have Null , dont install or update'
        except Exception,e:
                print e
                #logging.error(e)   
