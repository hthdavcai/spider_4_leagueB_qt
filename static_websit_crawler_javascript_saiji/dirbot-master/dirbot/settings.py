# Scrapy settings for dirbot project

SPIDER_MODULES = ['dirbot.spiders']
NEWSPIDER_MODULE = 'dirbot.spiders'
DEFAULT_ITEM_CLASS = 'dirbot.items.CrawlerHeadItemBasket'

ITEM_PIPELINES = {
    'dirbot.pipelines.MySQLStorePipeline': 100,
}

DUPEFILTER_CLASS = 'scrapyjs.SplashAwareDupeFilter'
DOWNLOADER_MIDDLEWARES = {
    'scrapyjs.SplashMiddleware': 1,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 2,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'dirbot.UA.RotateUserAgentMiddleware': 400
}
SPLASH_URL = 'http://192.168.2.10:58050'
