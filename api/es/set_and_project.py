import time
from elasticsearch import Elasticsearch

from api.es.es_base import ESClient
import api.es.config.config_statistics as INDEX


# from api.web.utils import func_line_time


class SetProject():

    def __init__(self, host: str = "10.60.1.145", port: str = "9200", timeout: int = 5000):
        """
        Create a instance to handle data
        :param host: es host
        :param port: es port
        :param timeout: es timeout
        """
        self.client = ESClient()
        self.Client = Elasticsearch(host=host, port=port, timeout=timeout)

    def insert_index_set_data(self, data: dict):
        res = {"code": 0, "error": "", "data": {}}
        for key in INDEX.set_table['insert_fields']:
            if key in data:
                res['data'][key] = data[key]
            else:
                res['code'] = -1
                res['error'] += " " + key
        if res['code'] == -1:
            return res

        res.pop("error")
        index = "set_data_2"
        doc_type = "set_data_2"
        res['data']['id'] = ESClient().insert(index, doc_type, res['data'])
        return res

    def update_index_set_data(self, data: dict):
        res = {"code": 0, "error": "", "data": {}}
        for key in INDEX.set_table['update_fields']:
            if key in data:
                res['data'][key] = data[key]
            else:
                res['code'] = -1
                res['error'] += " " + key
        if res['code'] == -1:
            return res

        id = res['data']['id']
        res['data'].pop('id')

        res.pop("error")
        index = "set_data_2"
        doc_type = "set_data_2"
        res['data'] = ESClient().update(index, doc_type, id, data)
        return res

    def insert_index_project_data(self, data: dict):
        res = {"code": 0, "error": "", "data": {}}
        for key in INDEX.project_table['insert_fields']:
            if key in data:
                res['data'][key] = data[key]
            else:
                res['code'] = -1
                res['error'] += " " + key
        if res['code'] == -1:
            return res

        res.pop("error")
        index = "project_data"
        doc_type = "project_data"
        res['data']['id'] = ESClient().insert(index, doc_type, res['data'])
        return res

    def update_index_project_data(self, data: dict):
        res = {"code": 0, "error": "", "data": {}}
        for key in INDEX.project_table['update_fields']:
            if key in data:
                res['data'][key] = data[key]
            else:
                res['code'] = -1
                res['error'] += " " + key
        if res['code'] == -1:
            return res

        id = res['data']['id']
        res['data'].pop('id')

        res.pop("error")
        index = "project_data"
        doc_type = "project_data"
        res['data'] = ESClient().update(index, doc_type, id, data)
        return res

    def findSetorProject(self, label: str, limit: bool, query: str = None, idlist: list = None,
                         page: int = None, size: int = 30):
        """
        @:param label: "set" or "project"
        @:param query: "id": search by id; "type": search by type
        """
        res = {}
        table_index = None
        doc_type = None
        if label == "set":
            table_index = "set_data_2"
            doc_type = "set_data_2"
        else:
            if label == "project":
                table_index = "project_data"
                doc_type = "project_data"
            else:
                res["code"] = -1
                return res
        searchRes = None
        time.sleep(0.2)
        if limit:
            searchRes = self.client.matchall(table_index, doc_type)
        elif not query:
            searchRes = self.client.matchall(table_index, doc_type, page, size)
        elif query != "id":
            searchRes = self.client.match(table_index, doc_type, "name", query, page, size)
        elif query == "id" and len(idlist) != 0:
            (code, error, searchRes) = self.client.ids(table_index, doc_type, idlist, False)
        if searchRes:
            searchRes = sorted(searchRes, key=lambda  x: x["create_time"], reverse=True)
        res["code"] = 0
        res["data"] = searchRes
        return res

    def deleteSetorProject(self, label: str, idlist=None, type=None):
        res = {"code": 0}
        index = None
        doc_type = None
        if label == "set":
            index = "set_data_2"
            doc_type = "set_data_2"
        if label == "project":
            index = "project_data"
            doc_type = "project_data"
        if idlist:
            for item in idlist:
                if self.Client.exists(index=index, doc_type=doc_type, id=item):
                    self.Client.delete(index=index, doc_type=doc_type, id=item)
        elif type:
            res = self.findSetorProject(label, query=type)["data"]
            ids = []
            for item in res:
                self.Client.delete(index=index, doc_type=doc_type, id=item["id"])
        return res


if __name__ == '__main__':
    data = {
        "id": "",
        "name": "LiYingyan",
        "des": "description of LiYingyan",
        "nodeIds": ["Q1", "Q2", "Q3"],
        "modify_time": "2019-3-14",
        "create_time": "2019-3-14",
        "modify_user": "Liyingyan",
        "create_user": "Liyingyan",
        "type": "human"
    }
    test = SetProject()
    res = test.insert_index_set_data(data)
    print(res)
