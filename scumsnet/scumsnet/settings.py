SPIDER_MODULES = ['scumsnet.scumsnet_crawl']

ITEM_PIPELINES = {
    'scumsnet.pipelines.tmw.TMWPipeline': 100}
