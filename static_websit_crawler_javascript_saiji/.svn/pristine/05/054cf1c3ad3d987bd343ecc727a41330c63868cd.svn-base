# -*- coding: utf-8 -*-
import ConfigParser
from dirbot.DataDemoUtil import DataDemoUtil
import time
import sys
import os
from scrapy import cmdline
reload(sys)
sys.setdefaultencoding('utf-8')
cf = ConfigParser.ConfigParser()
cf.read("platinfo.cfg")

class AbstractSpider:
    
    if __name__ == '__main__':
        argvs = []
        for arg in sys.argv:   
            argvs.append(arg)
        if 2 != len(argvs):
            print 'Please Input SpiderConfig Name Form MySql'
        else:
            #get JSON From MySql For Test
            DataDemoUtil = DataDemoUtil()
            #cfstr =  cf.get("spider", "spider_name")
            cfstr = argvs[1]
            sqljsonStr = DataDemoUtil.getJsonString(cfstr) 
            
            #local Json
    #        jsonfile = f = file("c:\\okoooNewDIGUI.txt")
    #        jsonProtocolLocal = f.read()
    #        sqljsonStr = jsonProtocolLocal
    
            #write Config File
            timestamp = time.time()
            timestamp = "%.3f" % timestamp +'.json'
            print timestamp
            f = file(timestamp, 'w')
            f.write(sqljsonStr)
            f.close()
            ABSPATH=os.path.abspath(sys.argv[0])
            ABSPATH=os.path.dirname(ABSPATH)+"\\"  # for windows
#            ABSPATH=os.path.dirname(ABSPATH)+"/"  # for linux
            filepath = ABSPATH +  timestamp
            filepath = str(filepath)
            #start Spider
            cmdline.execute(("scrapy crawl spiders_exec_okooo_jclq -a category="+timestamp+" -a filePath="+filepath+" -L ERROR").split())
            print "Spider Exit"
#            if os.path.isfile(filepath):
#                os.remove(filepath)