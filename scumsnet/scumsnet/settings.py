SPIDER_MODULES = ['scumsnet.scumsnet_crawl']

ITEM_PIPELINES = {
    'scumsnet.pipelines.tmw.TMWPipeline': 100,
    'scumsnet.pipelines.tmw_nlp.TMWEntityPipeline': 200}

