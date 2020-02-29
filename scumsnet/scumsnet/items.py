
import scrapy


class Annotation(scrapy.Item):
    text = scrapy.Field()
    pos = scrapy.Field()
    tag = scrapy.Field()
    label = scrapy.Field()


class Post(scrapy.Item):
    author = scrapy.Field()
    copy = scrapy.Field()
    timestamp = scrapy.Field()
    annotations = scrapy.Field()


class Thread(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    posts = scrapy.Field()
