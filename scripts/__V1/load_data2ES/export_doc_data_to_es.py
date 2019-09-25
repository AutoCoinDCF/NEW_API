import pymongo
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json
 
es = Elasticsearch(hosts='http://10.60.1.145', port=9200)
actions=[]
index_name = "human_document"
doc_type = "human_document"

mongoclient = pymongo.MongoClient("10.60.1.140", 6080)
admin = mongoclient.admin
admin.authenticate("root", "111111")

db = mongoclient["nlu"]
col = db["LabelData"]
filter = {}
res = col.find(filter)

_index_mappings = { 
    "settings":{
        "number_of_shards": 1 
    }             
}

if es.indices.exists(index=index_name) is not True:
    res = es.indices.create(index=index_name, body=_index_mappings)
    print(res)

i = 0
for data in res:
    # if( i == 1000 ):
    #     helpers.bulk(client=es, actions=actions)
    #     actions.clear()
    #     print("clear")
    #     i=0
    # a = json.loads(data)
    id = data['_id']
    data.pop('_id')
    data['tmp'] = str(data['human_nel'])
    data.pop("human_nel")
    # a.pop('_nlu_nel')
    print(i)
    # action={'_op_type':'index',#操作 index update create delete  
    #         '_index':index_name,#index
    #         '_type':doc_type,  #type
    #         '_id': id,
    #         '_source':a}
    # actions.append(action)
    # print(a['_nlu_nel'])
    res = es.index(index = index_name, doc_type = doc_type, id = id, body = data, ignore = 400)
    print(res)
    i += 1
# helpers.bulk(client=es, actions=actions)
