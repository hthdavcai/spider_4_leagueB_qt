import os
import time
import redis
import MySQLdb
import sys
import ConfigParser
from scrapy.utils.serialize import ScrapyJSONEncoder

if __name__ == '__main__':
    # cf = ConfigParser.ConfigParser()
    # cf.read("redis.cfg")

    redis_host = 'localhost'
    redis_port = 6379
    password = '-1'
    spider_name = 'spider1'

    if password == '-1':
        redis_server = redis.Redis(host=redis_host, port=redis_port, db=4)
    else:
        redis_server = redis.Redis(host=redis_host, port=redis_port, password=password, db=4)

    conn = MySQLdb.connect(host='101.201.211.208', user='spider', passwd='spiderCBjuj19BN&^*', db='db_lottery',
                           charset='utf8', port=3306)

    cursor = conn.cursor()
    cursor.execute("select leagueId,season,leagueType from md_qt_league")
    league_lst = cursor.fetchall()
    item = {}
    for league in league_lst:
        item['leagueId'] = str(league[0])
        item['season'] = str(league[1])
        item['leagueType'] = str(league[2])
        x = ScrapyJSONEncoder().encode(item)
        redis_server.rpush('spiderDataJson', x)
    conn.close()

    f_obj = open('league.txt')
    data_lst = f_obj.readlines()
    league_id_lst = []
    for data in data_lst:
        league_id_lst.append(data.strip())

    while True:
        try:
            os.system('del *.json')
        except SystemExit, e:
            pass
        cfstr = redis_server.rpop('spiderDataJson')
        if cfstr is None:
            sys.exit(1)
        else:
            timestamp = time.time()
            timestamp = "cfstr_" + "%.3f" % timestamp + '.json'
            print timestamp
            f = file(timestamp, 'w')
            f.write(cfstr)
            f.close()
            cf_dic = eval(cfstr)
            try:
                if 'League' in cfstr and cf_dic['leagueId'] in league_id_lst:
                    os.system('python AbstractSpider.py spiders_exec_qt_league_fixtures {}'.format(timestamp))
                # elif 'CupMatch' in cfstr:
                #     os.system('python AbstractSpider.py spiders_exec_qt_cupmatch_fixtures {}'.format(timestamp))
                #     pass
                # elif 'SubLeague' in cfstr:
                #     os.system('python AbstractSpider.py spiders_exec_qt_subleague_fixtures {}'.format(timestamp))
                #     pass
            except SystemExit, e:
                print e
            except Exception, e:
                print e

    print '{} exit!'.format(spider_name)
