from elasticsearch import Elasticsearch

es = Elasticsearch(hosts='http://10.60.1.145', port=9200)
actions = []
index_name = "set_data_2"
doc_type = "set_data_2"

_index_mappings = {
    "mappings": {
        index_name: {
            "properties": {
                "nodeIds": {
                    "type": "object"
                }
            }
        }
    },
    "settings": {
        "number_of_shards": 1,
        "max_result_window": "2000000000"
    }
}

if es.indices.exists(index=index_name) is not True:
    res = es.indices.create(index=index_name, body=_index_mappings)
    print(res)
