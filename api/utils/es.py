from elasticsearch import Elasticsearch


class es():
    def __init__(self, host: str = '10.60.1.145', port: str = '9200', timeout: int = 5000):
        """
        Create a instance to handle data
        
        :param host: es host
        :param port: es port
        :param timeout: es timeout        
        """
        self.Client = Elasticsearch(host=host, port=port, timeout=timeout)

    def insert(self, index: str, doc_type: str, _id: str, data: dict):
        """
        Insert data into es
        
        :param index: The name of the index to scope the operation
        :param doc_type: The name of the document type
        :param _id: entity_id, data store with _id
        :param data: {"field1": value1, "filed2": value2 ……}
        """
        return self.Client.index(index=index, doc_type=doc_type, id=_id, body=data)

    def findbyId(self, index: str, doc_type: str, _id: str, filter=[]) -> dict:
        """
        Return the data with specified id
        
        :param index: The name of the index to scope the operation
        :param doc_type: The name of the document type
        :param _id: entity_id
        
        :return: {"code": 0/-1, "data"[]} success:0 failed: -1
        """
        res = {}
        res['data'] = []
        ids = []
        ids.append(_id)
        body = {
            "query": {
                "ids": {
                    "type": doc_type,
                    "values": ids
                }
            }
        }
        if (len(filter) != 0):
            body['_source'] = filter
        searchRes = self.Client.search(index=index, doc_type=doc_type, body=body)
        if (searchRes['hits']['total'] == 0):
            res['code'] = -1
        else:
            res['code'] = 0
            res['data'] = searchRes['hits']['hits'][0]['_source']
        return res

    def findbyIdList(self, index: str, doc_type: str, idlist: list, filter: list = []):
        res = {}
        res['data'] = []
        body = {
            "query": {
                "ids": {
                    "type": doc_type,
                    "values": idlist
                }
            }
        }
        if (len(filter) != 0):
            body['_source'] = filter
        searchRes = self.Client.search(index=index, doc_type=doc_type, body=body, from_=0, size=100000000)
        if (searchRes['hits']['total'] != len(idlist)):
            res['code'] = -1
        else:
            res['code'] = 0
            for item in searchRes['hits']['hits']:
                tmp = item['_source']
                tmp['id'] = item['_id']
                res['data'].append(tmp)
        return res
