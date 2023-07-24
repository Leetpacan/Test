import scrapy
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from time import sleep
import io

class OkSpider(scrapy.Spider):
    name = 'ok'
    start_urls = ['https://ok.ru/yaponskay']

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        group_data = self.group_parse(response)
        self.driver.get(response.url)
        sleep(1)
        SCROLL_PAUSE_TIME = 1
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        sel = Selector(text=self.driver.page_source)
        profile_data = list(self.profile_parse(response.url, sel))
        self.driver.quit()

        data = {
            'group_data': group_data,
            'profile_data': profile_data
        }
        with io.open('ok.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def profile_parse(self, url, response):
        posts = response.css('div.media-text_cnt_tx.emoji-tx.textWrap')
        comment_selectors = response.css('a[data-l="t,.k"] span.widget_count::text').getall()
        like_selectors = response.css('.widget_cnt.controls-list_lk.js-klass.js-klass-action .widget_count::text').getall()
        publication_date = response.css('div.feed_date::text').getall()
        for i, post in enumerate(posts):
            yield {
                'url': post.css('a.media-text_a::attr(href)').get(),
                'text': post.css('::text').get().replace('\"', '').replace('\n', '').replace('\xa0', ''),
                'comments_count': int(comment_selectors[i].replace('\xa0', '')),
                'likes_count': int(like_selectors[i].replace('\xa0', '')),
                'publication_date': publication_date[i],
                'item_type': 'GroupPost'
            }

    def group_parse(self, response):
        return {
            'url': response.css('meta[property="og:url"]::attr(content)').get(),
            'group_name': response.css('h1.group-name_h::text').get().replace('\"', ''),
            'group_id': response.css('div.u-menu_li.u-menu_li__pro a::attr(data-group-id)').get(),
            'description': response.css('meta[property="og:description"]').get().replace('\n', '').replace('\"', ''),
            'members_count': int(response.css('span#groupMembersCntEl::text').get().replace('\xa0', '')),
            'posts_count': int(response.css('span.navMenuCount::text').get().replace('\xa0', '')),
            'place': response.css('div.group-info_lst_i.__value::text').get(),
            'item_type': 'GroupProfile'
        }
