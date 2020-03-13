
# Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt

from itertools import chain
import logging
import os

from neo4j import GraphDatabase   
import scrapy

from .neo_tools import *


class NeoPipeline(object):
    
    def open_spider(self, spider):
        try:
            self.neo_db = GraphDatabase.driver('bolt://scumsnet_neo:7687')
        except:
            self.neo_db = GraphDatabase.driver(
                'bolt://{}:7687'.format(
                os.environ.get('NEO_HOST', 'localhost')))

                    
    def process_item(self, item, spider):
        for post in item.get('posts', []):
            post['post_id'] = '_'.join(map(post.get, ('author', 'timestamp')))
            
        post_data = [{
            'user': post['author'],
            'text': cypherval(post['copy']),
            'timestamp': post['timestamp'],
            'post_id': post['post_id']} for post in  item.get('posts', [])]
                                                              
        thread_merge = '''
            MERGE (t:thread {{title: "{title}", url: "{url}"}})'''.format(
                title=cypherval(item['title']), url=item['url'])
            
        post_unwind = '''
            WITH t
            UNWIND $data AS data
            MERGE (u:user {name: data.user})
            MERGE (p:post {text: data.text, posted: datetime(data.timestamp),
            post_id: data.post_id})
            MERGE (u)-[:POSTED]->(p)-[:POSTED_IN]->(t)'''
        
        neo_tx(self.neo_db, '\n'.join((thread_merge, post_unwind)),
            data=post_data)        
        
        entity_data = [[
            {'post_id': post['post_id'], 'text': cypherval(ent['text']),
            'label': ent['label']} for ent in post.get('entities', [])]
            for post in  item.get('posts', [])]
            
        entity_unwind = '''
            UNWIND $data AS data
            UNWIND data AS ents
            MATCH (p:post {post_id: ents.post_id})
            MERGE (e:entity {text: ents.text, label: ents.label})
            MERGE (p)-[:MENTIONS]->(e)'''
            
        neo_tx(self.neo_db, entity_unwind, data=entity_data)
        
        annot_data = [[
            {'post_id': post['post_id'], 'text': cypherval(annot['text']),
            'pos': annot['pos'], 'tag': annot['tag'], 'label': annot['label']}
            for annot in post.get('annotations', [])]
            for post in item.get('posts', [])]
            
        annot_unwind = '''
            UNWIND $data AS data
            UNWIND data AS annots
            MATCH (p:post {post_id: annots.post_id})
            MERGE (a:annotation {text: annots.text, pos: annots.pos,
            tag: annots.tag, label: annots.label})
            MERGE (p)-[:FLAGGED]->(a)'''
        
        
        neo_tx(self.neo_db, annot_unwind, data=annot_data)


        return item
