import collections
import json
import os

from elasticsearch import Elasticsearch

import api.es.generateDSL as DSL
import api.es.searchResHandle as HANDLE


class ESClient():

    def __init__(self):
        """
        Create a instance to handle data      
        """
        path = '/config/es.config'
        config_path = os.path.join(os.path.dirname(__file__) + path)
        self._config = {}
        with open(config_path, 'r') as f:
            self._config = collections.OrderedDict(json.load(f))
        self.esConnect()

    def esConnect(self):
        self.Client = Elasticsearch(hosts=self._config['param']['es']['client']['hosts'],
                                    timeout=self._config['param']['es']['client']['timeout'])

    def ids(self, index: str, doc_type: str, idlist: list, index_info: bool = True, source: list = None):
        body = DSL.ids(doc_type, idlist, source)
        res = self.Client.search(index=index, doc_type=doc_type, body=body)['hits']
        HANDLE.addIdMany(res)
        HANDLE.addTypeMany(res)
        (code, error) = HANDLE.check(idlist, res)
        if not index_info:
            res = HANDLE.getSourceMany(res)
        if source and len(source) == 1:
            res = HANDLE.getIds(source[0], res)
        return (code, error, res)

    def exits(self, index: str, doc_type: str, id: str):
        return self.Client.exists(index=index, doc_type=doc_type, id=id)

    def get(self, index: str, doc_type: str, id: str, index_info: bool = True, source: list = None):
        code = -1
        res = {}
        if self.exits(index, doc_type, id):
            code = 0
            res = self.Client.get(index=index, doc_type=doc_type, id=id)
            HANDLE.addIdOne(res)
            if not index_info:
                res = HANDLE.getSourceOne(res)
        if source:
            res = HANDLE.filter(res, source)
        return (code, res)

    def term(self, index: str, field: str, query: str, size: int = 10, source: list = None):
        body = DSL.term(field, query, size, source)
        res = self.Client.search(index=index, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def matchterm(self, index: str, field: str, query: str, size: int = 10, source: list = None):
        body = DSL.match_term(field, query, size, source)
        res = self.Client.search(index=index, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def matchPhrase(self, index: str, field: str, query: str, slop: int = 10, size: int = 10, source: list = None):
        body = DSL.matchPhrase(field, query, slop, size, source)
        res = self.Client.search(index=index, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def fuzzy(self, index: str, field: str, query: str, size: int = 10, source: list = None):
        body = DSL.fuzzy(field, query, size, source=source)
        res = self.Client.search(index=index, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def prefix(self, index: str, field: str, query: str, size: int = 10, source: list = None):
        body = DSL.prefix(field, query, size=size, source=source)
        res = self.Client.search(index=index, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if source and len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def wildcard(self, index: str, field: str, query: str, size: int = 800, source: list = None):
        """wildcard query"""
        body = DSL.wildcard(field, query, size=size, source=source)
        res = self.Client.search(index=index, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if source and len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def insert(self, index: str, doc_type: str, data: str):
        return self.Client.index(index=index, doc_type=doc_type, body=data)['_id']

    def update(self, index: str, doc_type: str, id: str, data: str):
        body = {'doc': data}
        self.Client.update(index=index, doc_type=doc_type, id=id, body=body)
        (code, res) = self.get(index, doc_type, id, False)
        return res

    def matchall(self, index: str, doc_type: str, page: str = None, size: str = None, source: list = None):
        body = DSL.matchall(page, size, source)
        res = self.Client.search(index=index, doc_type=doc_type, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if source and len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def match(self, index: str, doc_type: str, field: str, query: str, page: str = None, size: str = None,
              source: list = None):
        body = DSL.match(field, query, page, size, source)
        res = self.Client.search(index=index, doc_type=doc_type, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if source and len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res

    def nested(self, index: str, field: str, query: str, size: int = 10, source: list = None):
        pass

    def should(self, index: str, doc_type: str, field: str, query: list or str, page: int = None, size: int = 10,
               source: list = None):
        body = DSL.should(field, query, page, size, source)
        res = self.Client.search(index=index, doc_type=doc_type, body=body)['hits']
        HANDLE.addIdMany(res)
        res = HANDLE.getSourceMany(res)
        if source and len(source) == 1 and "id" in source:
            res = HANDLE.getIds("id", res)
        return res
