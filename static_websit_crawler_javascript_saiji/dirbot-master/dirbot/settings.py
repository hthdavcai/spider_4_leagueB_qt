# Scrapy settings for dirbot project

SPIDER_MODULES = ['dirbot.spiders']
NEWSPIDER_MODULE = 'dirbot.spiders'
DEFAULT_ITEM_CLASS = 'dirbot.items.CrawlerHeadItemBasket'

ITEM_PIPELINES = {
    'dirbot.pipelines.MySQLStorePipeline': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'dirbot.UA.RotateUserAgentMiddleware': 400
}
SPLASH_URL = 'http://192.168.57.128:8050'
