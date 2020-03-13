
# Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt

from datetime import datetime
import json
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
        url = 'https://www.mumsnet.com/info/search'
        for term in self.terms:
            params = {'q': term}
            yield scrapy.FormRequest(url=url, method='GET', formdata=params,
                meta={'term': term}, callback=self.parse, dont_filter=True)


    def parse(self, response):
        cx_path = "//script[starts-with(.,'(function(){var cx')]/text()"
        cx_scr = scr = response.xpath(cx_path).extract_first()
        self.cx, = re.findall(r"(?<=cx=')[a-zA-Z0-9:]+", cx_scr)
        url = 'https://cse.google.com/cse.js'
        term = response.meta.get('term')
        params = {'cx': self.cx}
        yield scrapy.FormRequest(url=url, method='GET', formdata=params,
            meta={'term': term}, callback=self.parse_cse, dont_filter=True)
        
        
    def search_pars(self, term, page=1, date_sort=True):
        suffix = str(random.randint(2000, 4000))
        pars = {'rsz': 'filtered_cse', 'num': '10', 'hl': 'en',
            'source': 'gcsc', 'gss': '.com', 'start': str(10*page),
            'cselibv': self.cse_lib, 'cx': self.cx, 'q': term, 'safe': 'off',
            'cse_tok': self.cse, 'exp': 'csqr,cc',
            'callback': 'google.search.cse.api'+suffix}
        if date_sort:
            pars['sort'] = 'date'
        return pars
    
        
    def parse_cse(self, response):
        self.cse, = re.findall(u'(?<="cse_token": ")[a-zA-Z0-9:]+',
            response.text)
        self.cse_lib, = re.findall(u'(?<="cselibVersion": ")[a-zA-Z0-9:]+',
            response.text)
        term = response.meta.get('term')
        params = self.search_pars(term)
        yield scrapy.FormRequest(url='https://cse.google.com/cse/element/v1',
            method='GET', formdata=params,
            meta={'term': term, 'page': 1}, callback=self.parse_results,
            dont_filter=True)
        
        
    def parse_results(self, response):
        
        json_resp = json.loads('{'
            +'\n'.join(response.text.split('\n')[2:-1])
            +'}')
        
        results = json_resp.get('results', [])
        
        term = response.meta['term']
        page = response.meta.get('page', 1)
        
        if 'results' not in json_resp.keys():
            params = self.search_pars(term, page=page)
            yield scrapy.FormRequest(url='https://cse.google.com/cse/element/v1',
                method='GET', formdata=params,
                meta={'term': term, 'page': page}, callback=self.parse_results,
                dont_filter=True)            
        
        for res in results:
            yield scrapy.Request(url=res['url'], callback=self.parse_thread)

        if results:
            next_page = 1 + page
            params = self.search_pars(term, page=next_page)
            yield scrapy.FormRequest(url='https://cse.google.com/cse/element/v1',
                method='GET', formdata=params,
                meta={'term': term, 'page': next_page}, callback=self.parse_results)
                    
        
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
            
        
        
