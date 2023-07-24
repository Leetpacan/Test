import scrapy
import os
from scrapy import signals
from scrapy.signalmanager import dispatcher
from newspaper import Article
import xml.etree.ElementTree as ET
import json
datatosave = []
class RssSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(RssSpider, self).__init__(*args, **kwargs)
        self.need_render = False
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
    name = "rss_spider"
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'news.json'
    }
    start_urls = [
        'https://rssexport.rbc.ru/rbcnews/news/30/full.rss',
    ]

    def parse(self, response):
        root = ET.fromstring(response.text)
        if os.path.isfile("source_state.json"):
            with open("source_state.json") as f:
                data = json.load(f)
                self.need_render = data["need_render"]
        else:
            self.need_render = bool(response.text)
        for item in root.findall('.//item'):
            news_url = item.find('link').text
            article = Article(news_url)
            article.download()
            article.parse()
            #self.need_render = bool(article.text)
            #print(self.need_render)
            yield {
                'url': news_url,
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
            }
    def spider_closed(self, spider):
        with open('source_state.json', 'w') as f:
            json.dump({"need_render": self.need_render}, f)