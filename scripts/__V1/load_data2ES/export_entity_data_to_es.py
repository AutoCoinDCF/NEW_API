import pymongo
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json

# nohup python export_entity_data_to_es.py >import.log 2>&1 &

es = Elasticsearch(hosts='http://10.60.1.145', port=9200)
actions = []
index_name = "wiki_data"
doc_type = "wike_data"

mongoclient = pymongo.MongoClient("10.60.1.140", 6080)
admin = mongoclient.admin
admin.authenticate("root", "111111")

db = mongoclient["wikidata"]
col = db["Sys_Property"]
filter = {}
res = col.find(filter)

_index_mappings = {

    "mappings": {
        index_name: {
            "properties": {
                "date_of_birth": {"type": "text"},
                "date_of_death": {"type": "text"},
                "chinese_name": {
                    "type": "text",
                    "analyzer": "pinyin",
                    "search_analyzer": "pinyin",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "entity_name": {
                    "type": "text",
                    "analyzer": "my_analyzer",
                    "search_analyzer": "my_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }
    },
    "settings": {
        "number_of_shards": 1,
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
    print(res)

purpose_field = [
    'Entity_id', 'Entity_name', 'Chinese_name', 'Entity_type', 'birth name',
    'name in native language', 'nickname', 'date of birth', 'date of death',
    'date of disappearance', 'place of birth', 'country of citizenship',
    'ethic group', 'religion', 'occupation', 'military rank', 'military branch',
    'member of political party', 'award received', 'e-mail', 'official blog',
    'official website', 'summary', 'description', 'native label', 'short name',
    'headquarters location', 'type', 'inception', 'member count', 'employees',
    'political ideology', 'official website', 'telephone number', 'description',
    'official name', 'name in native language', 'replaces', 'replaces by', 'nickname',
    'short name', 'inception', 'capital', 'continent', 'country', 'area', 'located in or next to body of water',
    'population', 'GDP', 'gini coefficient', 'located in time zone', 'coordinate location',
    'local dialing code', 'postal code', 'top-level Internet domain', 'official website',
    'office blog', 'image', 'coat of arms image', 'vessel class', 'location of final assembly',
    'total produced', 'inception', 'first flight', 'service entry', 'service retirement',
    'use', 'cost', 'muzzle velocity', 'length', 'width', 'height', 'mass', 'bore', 'diameter',
    'wingspan', 'takeoff and landing capability', 'conflict', 'significant event',
    'participant of', 'armament', 'coordinate location', 'call sign',
    'pennant number', 'official website'
]


def field_filter():
    purpose_field_filter = []
    for x in purpose_field:
        if x not in purpose_field_filter:
            purpose_field_filter.append(x)
    return purpose_field_filter


def filter_end(data):
    print(data)
    if not data['Entity_id'].startswith('Q'):
        return
    filter_end = {}
    purpose_field_filter = field_filter()
    for field_row in data:
        if field_row in purpose_field_filter:
            # filter_end.update({field_row: data.get(field_row)})
            filter_end.update({field_row.replace(' ', '_').lower(): data.get(field_row)})
            filter_end["img"] = "http://10.60.1.143/pic_lib/entity/{id}.png".format(id=data["Entity_id"])
    return filter_end


# def data_process(res):
#     '''
#     Insert mongo records one by one into the es database
#     Insertion efficiency: 10,000 pieces in 8 minutes
#     '''
#     # i = 0
#     for data in res:
#         data = filter_end(data)
#         if data:
#             id = data['Entity_id']
#             data.pop('Entity_id')
#             res = es.index(index = index_name, doc_type = doc_type, id = id, body = data, ignore = 400)
#             print(res)
#             # i += 1
#             # if i == 1000:
#             #     break
#
# data_process(res)

def go(res):
    '''
    Insert mongo records one by one into the es database
    Insertion efficiency: 40,000 pieces per minute
    '''
    actions = []

    def data_process(res):
        i = 0
        for data in res:
            data = filter_end(data)

            if (i == 1000):
                helpers.bulk(client=es, actions=actions)
                actions.clear()
                i = 0

            if data:
                id = data['entity_id']
                data.pop('entity_id')
                action = {'_op_type': 'index',  # 操作 index update create delete
                          '_index': index_name,  # index
                          '_type': doc_type,  # type
                          '_id': id,
                          '_source': data}
                print(i, action)
                actions.append(action)
            i += 1

    data_process(res)
    helpers.bulk(client=es, actions=actions)
go(res)
