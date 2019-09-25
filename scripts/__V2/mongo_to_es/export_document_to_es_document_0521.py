import pymongo
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts='http://10.60.1.145', port=9200)
actions = []
index_name = "document_sg"
doc_type = "document_sg"

mongoclient = pymongo.MongoClient("10.60.1.140", 6080)
admin = mongoclient.admin
admin.authenticate("root", "111111")

db = mongoclient["QBData"]
#col = db["documents_darpa"]
# documents_humanrights表会有超过1000字段的文档，es默认不支持该数量，也不建议修改
#col = db["documents_humanrights"]
# documents_labeled表也有超过1000的
#col = db["documents_labeled"]
#col = db["documents_taiwan"]
col = db["documents_gtd"]
filter = {}
res = col.find(filter)

_index_mappings = {
    "mappings": {
        index_name: {
            "properties": {
                "title": {
                    "properties": {
                        "ch": {"type": "text"},
                        "en": {
                            "type": "text",
                            "analyzer": "my_analyzer",
                            "search_analyzer": "my_analyzer",
                            # "fields": {
                            #     "keyword": {
                            #         "type": "keyword"
                            #     }
                            # }
                        }
                    }
                },
                "content": {
                    "properties": {
                        "ch": {"type": "text"},
                        "en": {
                            "type": "text",
                            "analyzer": "my_analyzer",
                            "search_analyzer": "my_analyzer",
                            # "fields": {
                            #     "keyword": {
                            #         "type": "keyword"
                            #     }
                            # }
                        }
                    }
                },

            }
        }
    },
    "settings": {
        "number_of_shards": 1,
        "max_result_window": "2000000000",
        "analysis": {
            "analyzer": {
                "my_analyzer": {
                    "type": "custom",
                    "tokenizer": "letter",
                    "filter": ["lowercase", "asciifolding"]

                }
            }
        }
    }
}
l = []
i = 0
if es.indices.exists(index=index_name) is not True:
    res = es.indices.create(index=index_name, body=_index_mappings)
    #print(res)
print("开始传输～")
for data in res:
    id = data['_id']
    data.pop('_id')
    data.pop("raw_id")
    try:
        res = es.index(index=index_name, doc_type=doc_type, id=id, body=data)
    except Exception as error:
        i += 1
        print("-------------id--------------")
        print(error)
        l.append(id)
    #print(res)
print('----------------------l----------------------')
print(l)
print('----------------------i----------------------')
print(i)
print("传输完毕～")
