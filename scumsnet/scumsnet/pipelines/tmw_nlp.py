
import spacy

from scumsnet.items import Annotation, Entity

nlp = spacy.load("en_core_web_sm") 


class TMWEntityPipeline(object):
    
    def entity_filter(self, ent):
        return ent.label_ not in ('PRODUCT', 'DATE', 'TIME', 'PERCENT', 'MONEY',
            'QUANTITY', 'ORDINAL', 'CARDINAL')


    def transgender_noun(self, tok):
        return tok.pos_ == 'NOUN' and tok.lemma_.startswith('transgend')

    
    def process_item(self, item, spider):
        for post in item['posts']:
            doc = nlp(post['copy'])
            post['entities'] = [Entity(**{'text': e.text, 'label': e.label_})
                for e in filter(self.entity_filter, doc.ents)]
            
            annotation_tokens = list(filter(self.transgender_noun, doc))
            if annotation_tokens:
                annotations = [Annotation(**{'text': tok.text, 'pos': tok.idx,
                    'tag': 'offensive', 'label': 'transgender as a noun'})
                    for tok in annotation_tokens]
                post['annotations'] += post.get('annotations', 
                    []) + annotations
            
        return item
