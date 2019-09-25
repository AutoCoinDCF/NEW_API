import pymongo
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts='http://10.60.1.145', port=9200)
actions = []
index_name = "event_0617"
doc_type = "event_0617"

mongoclient = pymongo.MongoClient("10.60.1.140", 6080)
admin = mongoclient.admin
admin.authenticate("root", "111111")

db = mongoclient["QBData"]
col = db["events"]
filter = {}
res = col.find(filter)
# 正确版本
#_index_mappings = {
#    "settings": {
#        "number_of_shards": 1
#    }
#}

_index_mappings = {
    "settings": {
        "number_of_shards": 1,
        "max_result_window": "2000000000"
    }
}


# 下次记得加检索最大值
#    "settings": {
#        "number_of_shards": 1,
#        "max_result_window": "2000000000",
#        "analysis": {
#            "analyzer": {
#                "my_analyzer": {
#                    "type": "custom",
#                    "tokenizer": "letter",
#                    "filter": ["lowercase", "asciifolding"]
#
#                }
#            }
#        }
#    }


print("start!")
if es.indices.exists(index=index_name) is not True:
    res = es.indices.create(index=index_name, body=_index_mappings)
    #print(res)

for data in res:
    #print(data)
    id = data['_id']
    data.pop('_id')
    res = es.index(index=index_name, doc_type=doc_type, id=id, body=data, ignore=400)
    #print(res)
print("end!")
