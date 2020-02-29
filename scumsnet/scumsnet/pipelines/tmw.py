
from .tmw_rules import rules, rule_tags
from scumsnet.items import Annotation


class TMWPipeline(object):
    
    def annotate(self, post):
        for rule in rules:
            for match in rule.rule.finditer(post):
                yield Annotation(**{
                    'text': match.group(),
                    'pos': match.span()[0],
                    'tag': rule.tag,
                    'label': rule.label})    

    
    def process_item(self, item, spider):
        for post in item['posts']:
            post['annotations'] = list(self.annotate(post['copy']))
            
        return item
