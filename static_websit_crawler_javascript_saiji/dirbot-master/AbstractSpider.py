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
        if 3 != len(argvs):
            print 'Please Input SpiderConfig Name Form MySql'
        else:
            # get JSON From MySql For Test
            DataDemoUtil = DataDemoUtil()
            cfstr = argvs[1]
            sqljsonStr = DataDemoUtil.getJsonString(cfstr)

            # write Config File
            timestamp = time.time()
            timestamp = "%.3f" % timestamp + '.json'
            print timestamp
            f = file(timestamp, 'w')
            f.write(sqljsonStr)
            f.close()
            ABSPATH = os.path.abspath(sys.argv[0])
            ABSPATH = os.path.dirname(ABSPATH) + os.sep
            filepath = ABSPATH + timestamp
            filepath = str(filepath)
            # start Spider
            cmdline.execute((
                                "scrapy crawl spiders_exec_okooo_jclq -a category=" + timestamp + " -a filePath=" + filepath + " -a jsonPath=" +
                                sys.argv[2] + " -L ERROR").split())

            print "Spider Exit"
