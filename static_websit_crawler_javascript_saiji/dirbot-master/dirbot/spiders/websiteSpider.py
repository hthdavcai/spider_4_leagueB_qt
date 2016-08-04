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
import redis

RENDER_HTML_URL = "http://192.168.2.10:58050/render.html"

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
        self.subleague_index = 0

        if len(self.dataDemo.__getPathVariables__()) == 0:
            self.__pathVariables = 1
        else:
            self.__pathVariables = self.dataDemo.__getPathVariables__()[0]['min']

        self.start_urls = [
            self.dataDemo.__getURL__()
        ]
        self.crawlerTime = datetime.datetime.now()
        print 'init'

    def start_requests(self):
        script = """
            function main(splash)
                splash:go(\"""" + str(self.start_urls[0]) + """\")
                splash:wait(5)
                splash:runjs("$('td.cupmatch_rw2').eq(""" + str(self.subleague_index) + """).click()")
                splash:wait(5)
                return splash:html()
            end
        """
        yield scrapy.Request(self.start_urls[0], self.parse,
                             meta={'splash': {'args': {'lua_source': script}, 'endpoint': 'execute'}})

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
            # variables = currentDataDemo.__getVariables__()
            variables = copy.deepcopy(currentDataDemo.__getVariables__())
            actualVars = copy.deepcopy(variables)

            round_count = sel.xpath("count(//td[@class='lsm2'])").extract()[0]
            round_count = int(round_count.split('.')[0])
            subleague_count = sel.xpath("count(//td[contains(@class,'cupmatch_rw2')])").extract()[0]
            subleague_count = int(subleague_count.split('.')[0])

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
                        valuexpathone = valuexpath[0].strip('\r\n').strip('\r\n').strip(' ')
                        item[str(jsonitem.get('name'))] = str(valuexpathone).strip()
                        itemCount += 1
                    except Exception, e:
                        item[str(jsonitem.get('name'))] = ""
                yield item
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

                if round_count > 1:
                    for round_index in range(round_count):
                        script = """
                            function main(splash)
                                splash:go(\"""" + str(self.start_urls[0]) + """\")
                                splash:wait(5)
                                splash:runjs("$('td.cupmatch_rw2').eq(""" + str(self.subleague_index) + """).click()")
                                splash:wait(5)
                                splash:runjs("$('td.lsm2').eq(""" + str(round_index) + """).click()")
                                splash:wait(5)
                                return splash:html()
                            end
                        """

                        yield scrapy.Request(self.start_urls[0], self.parse_round,
                                             meta={'splash': {'args': {'lua_source': script}, 'endpoint': 'execute'}})

                    if subleague_count > 1:
                        for subleague_index in range(subleague_count):
                            script = """
                                function main(splash)
                                    splash:go(\"""" + str(self.start_urls[0]) + """\")
                                    splash:wait(5)
                                    splash:runjs("$('td.cupmatch_rw2').eq(""" + str(subleague_index) + """).click()")
                                    splash:wait(5)
                                    return splash:html()
                                end
                            """
                            self.subleague_index = subleague_index
                            yield scrapy.Request(self.start_urls[0], self.parse_subleague,
                                                 meta={
                                                     'splash': {'args': {'lua_source': script}, 'endpoint': 'execute'}})

                elif subleague_count > 1:
                    for subleague_index in range(subleague_count):
                        script = """
                            function main(splash)
                                splash:go(\"""" + str(self.start_urls[0]) + """\")
                                splash:wait(5)
                                splash:runjs("$('td.cupmatch_rw2').eq(""" + str(subleague_index) + """).click()")
                                splash:wait(5)
                                return splash:html()
                            end
                        """
                        self.subleague_index = subleague_index
                        yield scrapy.Request(self.start_urls[0], self.parse_subleague,
                                             meta={'splash': {'args': {'lua_source': script}, 'endpoint': 'execute'}})

        except Exception, e:
            # print e
            logging.error(e)

    def parse_round(self, response):
        if 'config' in response.meta:
            configStr = response.meta['config']
            print "parse_chirdren"
            currentDataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, configStr)
        else:
            currentDataDemo = self.dataDemo
        try:
            sel = Selector(response)
            # variables = currentDataDemo.__getVariables__()
            variables = copy.deepcopy(currentDataDemo.__getVariables__())
            actualVars = copy.deepcopy(variables)

            while 1 == 1:
                item = {}
                itemCount = 0
                items = currentDataDemo.__getItems__()
                for jsonitem in items:
                    try:
                        xpath = str(jsonitem.get('xpath'))
                        for var in variables:
                            xpath = xpath.replace(var.get('flag'), str(var.get('min')))
                        valuexpath = sel.xpath(xpath).extract()
                        valuexpathone = valuexpath[0].strip('\r\n').strip('\r\n').strip(' ')
                        item[str(jsonitem.get('name'))] = valuexpathone
                        itemCount += 1
                    except Exception, e:
                        item[str(jsonitem.get('name'))] = ""
                yield item
                # count
                finish = 0
                for c in range(0, len(variables)):
                    if variables[c]['min'] == actualVars[c]['max']:
                        finish += 1
                if finish == len(variables):
                    break
                variables = self.addVars(variables, actualVars)
            print 'Spider While Crawler OK'
        except Exception, e:
            logging.error(e)

    def parse_subleague(self, response):
        if 'config' in response.meta:
            configStr = response.meta['config']
            print "parse_chirdren"
            currentDataDemo = DataDemoUtil.__getDataDemoFromString__(self.DataDemoUtil, configStr)
        else:
            currentDataDemo = self.dataDemo
        subleague_index = self.subleague_index

        try:
            sel = Selector(response)
            # variables = currentDataDemo.__getVariables__()
            variables = copy.deepcopy(currentDataDemo.__getVariables__())
            actualVars = copy.deepcopy(variables)

            round_count = sel.xpath("count(//td[@class='lsm2'])").extract()[0]
            round_count = int(round_count.split('.')[0])

            while 1 == 1:
                item = {}
                itemCount = 0
                items = currentDataDemo.__getItems__()
                for jsonitem in items:
                    try:
                        xpath = str(jsonitem.get('xpath'))
                        for var in variables:
                            xpath = xpath.replace(var.get('flag'), str(var.get('min')))
                        valuexpath = sel.xpath(xpath).extract()
                        valuexpathone = valuexpath[0].strip('\r\n').strip('\r\n').strip(' ')
                        item[str(jsonitem.get('name'))] = valuexpathone
                        itemCount += 1
                    except Exception, e:
                        item[str(jsonitem.get('name'))] = ""
                yield item
                # count
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

                if round_count > 1:
                    for round_index in range(round_count):
                        script = """
                            function main(splash)
                                splash:go(\"""" + str(self.start_urls[0]) + """\")
                                splash:wait(5)
                                splash:runjs("$('td.cupmatch_rw2').eq(""" + str(subleague_index) + """).click()")
                                splash:wait(5)
                                splash:runjs("$('td.lsm2').eq(""" + str(round_index) + """).click()")
                                splash:wait(5)
                                return splash:html()
                            end
                        """

                        yield scrapy.Request(self.start_urls[0], self.parse_round,
                                             meta={'splash': {'args': {'lua_source': script}, 'endpoint': 'execute'}})

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
