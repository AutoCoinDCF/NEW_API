import sys
import csv
csv.field_size_limit(sys.maxsize)
from elasticsearch import Elasticsearch
from elasticsearch import helpers
es=Elasticsearch( hosts='http://10.60.1.145',port=9200,timeout=500)

filedir = "./csv/"
filename = "KnowledgeGraph_big_table_with_in_out_neighbor.csv"
actions=[]
index_name = "entity_info_new"
doc_type = "entity_info_new"


_index_mappings = {
         "mappings": {
            doc_type: {
               "properties": {
                 "date_of_birth": { "type":"text"},
                 "date_of_death": { "type":"text"}
               }
            }
        },
        "settings":{
            "number_of_shards":1   
         }         
  }
if es.indices.exists(index=index_name) is not True:
    res = es.indices.create(index=index_name, body=_index_mappings)


with open(filedir+filename, 'r', encoding="utf-8") as f:
     reader = csv.reader(f)
     fieldnames = next(reader)
     csv_reader = csv.DictReader(f,fieldnames = fieldnames)
     i = 0
     for row in csv_reader:
         if( i == 2000 ):
             helpers.bulk(client=es, actions=actions)
             actions.clear()
             i=0
         d = {}
         for k,v in row.items():
             d[k] = v
         _id = d['_id']
         d.pop('_id')
         action={'_op_type':'index',
                 '_index':index_name,
                 '_type':doc_type,
                 '_id': _id,
                 '_source': d}
         actions.append(action)
         i += 1    
        
     helpers.bulk(client=es, actions=actions)

