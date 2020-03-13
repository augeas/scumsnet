# Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt

SPIDER_MODULES = ['scumsnet.scumsnet_crawl']

ITEM_PIPELINES = {
    'scumsnet.pipelines.tmw.TMWPipeline': 100,
    'scumsnet.pipelines.tmw_nlp.TMWEntityPipeline': 200,
    'scumsnet.pipelines.scumsnet_neo.NeoPipeline': 300}

AUTOTHROTTLE_ENABLED = True

