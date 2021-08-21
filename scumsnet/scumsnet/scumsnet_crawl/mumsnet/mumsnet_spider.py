
# Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt

from datetime import datetime
from itertools import chain
import random
import re


from dateutil import parser
import scrapy

from scumsnet.items import Post, Thread


user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'Windows 	Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/73.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/73.0']


class MumsnetSpider(scrapy.Spider):
    name = 'mumsnet'
    
    custom_settings = {'USER_AGENT': random.choice(user_agents)}

    
    def __init__(self, **kwargs):
        self.terms = ['trans', 'transgender', 'transsexual']
        super().__init__()
        
        
    def start_requests(self):        
        url = ('https://www.mumsnet.com/service/searchlambda/'
            +'talk-search-results?q={}&sort=newest')

        for term in self.terms:
            yield scrapy.Request(url=url.format(term), callback=self.parse)
            
            
    def parse(self, response):
        threads = response.css('section.search-results').css(
            'div.search-service__search-item').xpath('a/@href').extract()  
        
        titles = [t.split('/')[-1].split('?')[0] for t in threads]   
        
        yield from (scrapy.Request(url=url, meta={'thread': title},
            callback=self.parse_thread) for url, title in zip(threads, titles))
        
        pages = response.css('ul.pagination').xpath('li/a/@href').extract()
        
        page_numbers = list(chain.from_iterable(
            map(lambda p: re.findall('(?<=page=)[0-9]+$', p), pages))) 
        
        previous_pages = response.meta.get('previous', [])
        
        yield from (scrapy.Request(url=url, meta={'previous': previous_pages},
            callback = self.parse) for url, page in zip(pages, page_numbers)
            if page not in previous_pages)
        
         
    def parse_thread(self, response):
        thread = response.meta.get('thread',
            response.css('h1.thread_name').xpath('text()').extract_first())

        posts = response.css('div#posts>div.post')
        nicks = posts.css('span.nick').xpath('text()').extract()
        dates = list(map(datetime.isoformat, map(parser.parse,
            posts.css('span.post_time').xpath('text()').extract())))
        content = ['\n'.join(post.xpath(
            'descendant-or-self::*/text()').extract()).strip()
            for post in posts.css('div.talk-post')]   
                
        next_page = response.css('a#message-pages-bottom-next').xpath(
            '@href').extract_first()
        
        thread_page = response.meta.get('thread_page', 0)
        thread_url = response.meta.get('thread_url', response.url)

        post_items = [Post(
            **{'author': author, 'copy': copy, 'timestamp': timestamp})
            for author, copy, timestamp in zip(nicks, content, dates)]
        
        if thread_page:
            offset = 1
        else:
            offset = 0
        
        if post_items:
            yield Thread(title=thread, url=thread_url, posts=post_items[offset:])
        
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_url, callback=self.parse_thread,
                meta={'thread_page': thread_page+1, 'thread': thread,
                'thread_url': thread_url})
            
        
