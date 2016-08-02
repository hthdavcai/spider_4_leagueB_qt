# -*- coding: utf-8 -*-
from dirbot.jsonDataDemo import jsonDataDemo
from dirbot.DataDemoUtil import DataDemoUtil
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
import ConfigParser
import json
import logging
import urlparse
import copy
import scrapy
import os
import datetime
import demjson
from scrapy.http.headers import Headers
import redis

RENDER_HTML_URL = "http://192.168.57.128:8050/render.html"

cf = ConfigParser.ConfigParser()
cf.read("platinfo.cfg")


class websiteSpider(CrawlSpider):
    def __init__(self, category=None, filePath=None, jsonPath=None):
        f = file(category)
        jsonstr = f.read()
        f.close()
        if os.path.isfile(filePath):
            os.remove(filePath)

        self.league_dic = None
        if jsonPath is not None:
            f_obj = open(jsonPath)
            redis_str = f_obj.read()
            redis_dic = eval(redis_str)
            self.league_dic = redis_dic
            f_obj.close()
            os.remove(jsonPath)

        self.redis_server = redis.Redis(host='localhost', port=6379, db=4, charset='utf8', decode_responses=True)

        self.jsonstr = '%s' % jsonstr
        self.DataDemoUtil = DataDemoUtil()
        self.dataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, jsonstr, redis_dic)

        if len(self.dataDemo.__getPathVariables__()) == 0:
            self.__pathVariables = 1
        else:
            self.__pathVariables = self.dataDemo.__getPathVariables__()[0]['min']

        self.start_urls = [
            self.dataDemo.__getURL__()
        ]
        self.crawlerTime = datetime.datetime.now()
        print 'init'

    # def start_requests(self):
    #     for url in self.start_urls:
    #         body = json.dumps({"url": url, "wait": 3})
    #         headers = Headers({'Content-Type': 'application/json'})
    #         yield scrapy.Request(RENDER_HTML_URL, self.parse, method="POST",
    #                              body=body, headers=headers)

    jsonstr = ''
    name = cf.get("spider", "spider_name")

    # is woring  really * is delete this
    # allowed_domains = ["*"]

    def parse(self, response):
        if 'previous_body' in response.meta and response.body == response.meta['previous_body']:
            return
        if response.meta.has_key('config'):
            configStr = response.meta['config']
            currentDataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, configStr)
        else:
            currentDataDemo = self.dataDemo

        try:
            sel = Selector(response)
            # print response.body
            variables = currentDataDemo.__getVariables__()
            actualVars = copy.deepcopy(variables)
            while 1 == 1:
                item = {}
                itemCount = 0
                items = currentDataDemo.__getItems__()
                for jsonitem in items:
                    try:
                        xpath = str(jsonitem.get('xpath'))
                        #                        print variables
                        for var in variables:
                            xpath = xpath.replace(var.get('flag'), str(var.get('min')))
                        valuexpath = sel.xpath(xpath).extract()
                        if jsonitem.get('name') == 'matchTime':
                            valuexpathone = self.modify_time(valuexpath[0], item)
                        else:
                            valuexpathone = valuexpath[0].strip('\r\n').strip('\r\n').strip(' ')
                        item[str(jsonitem.get('name'))] = str(valuexpathone).strip()
                        # print jsonitem.get('name')
                        # print item[str(jsonitem.get('name'))],
                        itemCount += 1
                        # print "itemCount" ,
                        # print itemCount,
                    except Exception, e:
                        item[str(jsonitem.get('name'))] = ""
                chirdrenJsonObjects = currentDataDemo.__getChirdren__()
                for chirdrenjsonDataDemo in chirdrenJsonObjects:
                    jsonDataDemo().encode(chirdrenjsonDataDemo)
                    jsonConfigString = json.dumps(chirdrenjsonDataDemo, cls=jsonDataDemo)

                    for itemkey in item.keys():
                        jsonConfigString = jsonConfigString.replace(str("#" + itemkey + "#"), str(item[itemkey]))

                    jsonConfigObject = json.loads(jsonConfigString)
                    chirdrenKey = jsonConfigObject['URL'].replace(str('#super.'), str(''))
                    chirdrenLink = item[chirdrenKey]
                    if chirdrenLink != '':
                        chirdrenURL = urlparse.urljoin(response.url, chirdrenLink)
                        chirdrenURL = chirdrenURL.replace("##year", str(self.crawlerTime.year))
                        chirdrenURL = chirdrenURL.replace("##month", str(self.crawlerTime.month))
                        chirdrenURL = chirdrenURL.replace("##day", str(self.crawlerTime.day))
                        chirdrenURL = chirdrenURL.replace("##hour", str(self.crawlerTime.hour))
                        chirdrenURL = chirdrenURL.replace("##minute", str(self.crawlerTime.minute))
                        chirdrenURL = chirdrenURL.replace("##second", str(self.crawlerTime.second))
                        jsonConfigObject['URL'] = chirdrenURL
                        jsonConfigString = json.dumps(jsonConfigObject)
                        body = json.dumps({"url": chirdrenURL, "wait": 1})
                        headers = Headers({'Content-Type': 'application/json'})
                        yield scrapy.Request(RENDER_HTML_URL, self.parse_chirdren, meta={'config': jsonConfigString},
                                             method="POST",
                                             body=body, headers=headers)
                        # yield scrapy.Request(chirdrenURL,meta={'config': jsonConfigString}, callback=self.parse_chirdren)
                yield item
                print "item == {}".format(item)
                finish = 0
                for c in range(0, len(variables)):
                    if variables[c]['min'] == actualVars[c]['max']:
                        finish += 1
                if finish == len(variables):
                    break
                variables = self.addVars(variables, actualVars)
            print 'Spider While Crawler OK'

            spider_fin = False
            if len(variables) == 0:
                spider_fin = True
            '''如果第一个网页已经爬取完毕，则继续爬取第二个网页'''
            for c in range(0, len(variables)):
                if variables[c]['min'] == variables[c]['max']:
                    print 'spider a html OK!!!'
                spider_fin = True
            if spider_fin is True:
                if len(currentDataDemo.__getPathVariables__()) != 0:
                    if self.__pathVariables == currentDataDemo.__getPathVariables__()[0]['max'] + 1:
                        pass
                    else:
                        startUrl = self.change_url_4_spider(self.__pathVariables)
                        startUrl = startUrl.replace(u"##year", datetime.datetime.now().strftime('%Y'))
                        startUrl = startUrl.replace(u"##month", datetime.datetime.now().strftime('%m'))
                        startUrl = startUrl.replace(u"##day", datetime.datetime.now().strftime('%d'))
                        self.__pathVariables += 1
                        yield scrapy.Request(startUrl, meta={'config': self.jsonstr, 'previous_body': response.body},
                                             callback=self.parse)

        except Exception, e:
            # print e
            logging.error(e)

    def parse_chirdren(self, response):
        configStr = response.meta['config']
        print "parse_chirdren"
        currentDataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, configStr)
        try:
            sel = Selector(response)
            variables = currentDataDemo.__getVariables__()
            actualVars = copy.deepcopy(variables)
            while 1 == 1:
                item = {}
                item['###spiderConfigString###'] = configStr
                itemCount = 0
                items = currentDataDemo.__getItems__()
                for jsonitem in items:
                    try:
                        xpath = str(jsonitem.get('xpath'))
                        for var in variables:
                            xpath = xpath.replace(var.get('flag'), str(var.get('min')))
                        valuexpath = sel.xpath(xpath).extract()
                        valuexpathone = valuexpath[0].strip('\r\n').strip('\r\n').strip(' ')
                        # print valuexpathone,
                        item[str(jsonitem.get('name'))] = valuexpathone
                        # print jsonitem.get('name')
                        # print item[str(jsonitem.get('name'))],
                        itemCount += 1
                        # print "itemCount" ,
                        # print itemCount,
                    except Exception, e:
                        # print e
                        item[str(jsonitem.get('name'))] = ""
                        # print ''
                chirdrenJsonObjects = currentDataDemo.__getChirdren__()
                for chirdrenjsonDataDemo in chirdrenJsonObjects:
                    jsonDataDemo().encode(chirdrenjsonDataDemo)
                    jsonConfigString = json.dumps(chirdrenjsonDataDemo, cls=jsonDataDemo)

                    for itemkey in item.keys():
                        jsonConfigString = jsonConfigString.replace(str("#" + itemkey + "#"), str(item[itemkey]))

                    jsonConfigObject = json.loads(jsonConfigString)
                    chirdrenKey = jsonConfigObject['URL'].replace(str('#super.'), str(''))
                    chirdrenLink = item[chirdrenKey]
                    if chirdrenLink != '':
                        chirdrenURL = urlparse.urljoin(response.url, chirdrenLink)
                        chirdrenURL = chirdrenURL.replace("##year", str(self.crawlerTime.year))
                        chirdrenURL = chirdrenURL.replace("##month", str(self.crawlerTime.month))
                        chirdrenURL = chirdrenURL.replace("##day", str(self.crawlerTime.day))
                        chirdrenURL = chirdrenURL.replace("##hour", str(self.crawlerTime.hour))
                        chirdrenURL = chirdrenURL.replace("##minute", str(self.crawlerTime.minute))
                        chirdrenURL = chirdrenURL.replace("##second", str(self.crawlerTime.second))
                        jsonConfigObject['URL'] = chirdrenURL
                        jsonConfigString = json.dumps(jsonConfigObject)
                        body = json.dumps({"url": chirdrenURL, "wait": 0.5})
                        headers = Headers({'Content-Type': 'application/json'})
                        yield scrapy.Request(RENDER_HTML_URL, self.parse_chirdren, meta={'config': jsonConfigString},
                                             method="POST",
                                             body=body, headers=headers)
                        # yield scrapy.Request(chirdrenURL,meta={'config': jsonConfigString}, callback=self.parse_chirdren)
                yield item
                # count
                finish = 0;
                for c in range(0, len(variables)):
                    if variables[c]['min'] == actualVars[c]['max']:
                        finish += 1
                if finish == len(variables):
                    break
                variables = self.addVars(variables, actualVars)
            print 'Spider While Crawler OK'
        except Exception, e:
            # print e
            logging.error(e)

    # return to pipelines For First Crawler
    def getDataDemo(self):
        return self.dataDemo

    #  vars ++ 
    def addVars(self, vars, acutalVars):
        vc = len(acutalVars) - 1
        if vc == 0:
            val = vars[vc]['min'] + 1
            if val <= acutalVars[vc]['max']:
                vars[vc]['min'] = val
                return vars
        for vc in range(vc, 0, -1):
            val = vars[vc]['min'] + 1
            if val <= acutalVars[vc]['max']:
                vars[vc]['min'] = val
                return vars
            else:
                vars[vc]['min'] = acutalVars[vc]['min']
                if vc - 1 >= 0:
                    vars[vc - 1]['min'] += 1
                return vars
        return vars

    def get_json_str(self):
        return self.jsonstr

    def change_url_4_spider(self, index):
        json_str = self.get_json_str()
        text = demjson.decode(json_str)
        next_url = text.get('URL')
        next_url = next_url.replace(':page', str(index + 1))
        if self.league_dic is not None:
            next_url = next_url.replace("LeagueType", self.league_dic['leagueType'])
            next_url = next_url.replace("LeagueSeason", self.league_dic['season'])
            next_url = next_url.replace("LeagueId", self.league_dic['leagueId'])
        return next_url

    def modify_time(self, match_time, item):
        try:
            match_time = "{}-{}".format(item['season'].split('-')[-1], match_time)
        except KeyError, e:
            match_time = "2016-{}".format(match_time)
        time_obj = datetime.datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S')
        time_obj = time_obj + datetime.timedelta(hours=8)
        return time_obj.strftime('%m-%d %H:%M:%S')
