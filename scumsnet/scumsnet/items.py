
import scrapy


class Post(scrapy.Item):
    author = scrapy.Field()
    copy = scrapy.Field()
    timestamp = scrapy.Field()


class Thread(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    posts = scrapy.Field()
