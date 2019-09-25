import api.es.searchResHandle as HANDLE
from api.es.es_base import ESClient


def findById(index: str, doc_type: str, id: str, index_info: bool = True, source: list = None):
    res = {}
    (res['code'], res['data']) = ESClient().get(index, doc_type, id, index_info, source)
    return res


def findByIdList(index: str, doc_type: str, idlist: list, index_info: bool = True, source: list = None):
    res = {}
    (res['code'], res['error'], res['data']) = ESClient().ids(index, doc_type, idlist, index_info, source)
    res = HANDLE.resFix(res)
    return res
