import scrapy
import json
class OkSpider(scrapy.Spider):
    name = 'ok'
    start_urls = ['https://ok.ru/ria']
    def parse(self, response):
        yield from self.group_parse(response)
        links = response.css('div.media-text_cnt_tx.emoji-tx.textWrap a::attr(href)').getall()
        for index, link in enumerate(links):
            yield response.follow(link, self.profile_parse, meta={'index': index})
    def profile_parse(self, response):
        index = response.meta['index']
        yield {
            'url': response.url,
            'text': response.css('div.media-text_cnt_tx.emoji-tx.textWrap::text').get().replace('\"', '').replace('\n','').replace('\xa0', ''),
            'comments_count': int(response.css('a[data-l="t,.k"] span.widget_count::text').getall()[index].replace('\xa0', '')),
            'likes_count': int(response.css('.widget_cnt.controls-list_lk.js-klass.js-klass-action .widget_count::text').getall()[index].replace('\xa0', '')),
            'publication_date': response.css('div.ucard_add-info_i::text').get(),
            'item_type': 'GroupPost'
        }
    def group_parse(self, response):
        yield{
            'url': response.css('meta[property="og:url"]::attr(content)').get(),
            'group_name': response.css('h1.group-name_h::text').get().replace('\"', ''),
            'group_id': response.css('div.u-menu_li.u-menu_li__pro a::attr(data-group-id)').get(),
            'description': response.css('meta[property="og:description"]::attr(content)').get().replace('\n','').replace('\"', ''),
            'members_count': int(response.css('span#groupMembersCntEl::text').get().replace('\xa0', '')),
            'posts_count': int(response.css('span.navMenuCount::text').get().replace('\xa0', '')),
            'place': response.css('div.group-info_lst_i.__value::text').get(),
            'item_type': 'GroupProfile'
        }