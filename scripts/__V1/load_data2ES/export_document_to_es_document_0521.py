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
col = db["documents"]
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

if es.indices.exists(index=index_name) is not True:
    res = es.indices.create(index=index_name, body=_index_mappings)

print("传输开始！")

for data in res:
    id = data['_id']
    data.pop('_id')
    res = es.index(index=index_name, doc_type=doc_type, id=id, body=data, ignore=400)
    print(res)

print("传输完毕！")

