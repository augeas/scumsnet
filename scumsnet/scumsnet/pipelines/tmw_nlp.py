
import spacy

from scumsnet.items import Annotation, Entity

nlp = spacy.load("en_core_web_sm") 


class TMWEntityPipeline(object):
    
    def entity_filter(self, ent):
        return ent.label_ not in ('PRODUCT', 'DATE', 'TIME', 'PERCENT', 'MONEY',
            'QUANTITY', 'ORDINAL', 'CARDINAL')

    
    def process_item(self, item, spider):
        for post in item['posts']:
            doc = nlp(post['copy'])
            post['entities'] = [Entity(**{'text': e.text, 'label': e.label_})
                for e in filter(self.entity_filter, doc.ents)]
            
        return item
