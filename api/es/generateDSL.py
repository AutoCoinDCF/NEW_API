def ids(doc_type: str, idlist: list, source: list = None):
    body = {
        "query": {
            "ids": {
                "type": doc_type,
                "values": idlist
            }
        },
        "size": len(idlist)
    }
    if (source):
        body['_source'] = source
    return body


def term(filed: str, query: str, size: int = 10, source: str = None):
    body = {
        "query": {
            "term": {
                filed: query
            }
        },
        "size": size
    }
    if (source):
        body['_source'] = source
    return body


def match_term(filed: str, query: str, size: int = 10, source: str = None):
    body = {
        "query": {
            "term": {
                filed: query
            }
        },
        "size": size
    }
    if (source):
        body['_source'] = source
    return body


def matchPhrase(field: str, query: str, slop: int = 0, size: int = 10, source: str = None):
    body = {
        "query": {
            "match_phrase": {
                field: {
                    "query": query,
                    "slop": slop
                }
            }
        },
        "size": size
    }
    if (source):
        body['_source'] = source
    return body


def fuzzy(field: str, query: str, fuzziness: int = 2, prefix_len: int = 0, max_expansions: int = 100, size: int = 10,
          source: list = None):
    body = {"query": {
        "fuzzy": {
            field: {
                "value": query,
                "boost": 1.0,
                "fuzziness": fuzziness,
                "prefix_length": prefix_len,
                "max_expansions": max_expansions
            }
        }
    },
        "size": size
    }
    if (source):
        body['_source'] = source
    return body


def prefix(field: str, query: str, size: int, source: list):
    body = {
        "query": {
            "prefix": {
                field: query
            }
        },
        "size": size
    }
    if (source):
        body['_source'] = source
    return body


def wildcard(field: str, query: str, size: int, source: list):
    """
    wildcard query base API
    :param field:
    :param query:
    :param size:
    :param source:
    :return:
    """
    body = {
        "query": {
            "wildcard": {
                field: query
            }
        },
        "size": size
    }
    if (source):
        body['_source'] = source
    return body


def matchall(page: str = None, size: str = None, source: list = None):
    res = {
        "query": {
            "match_all": {}
        }
    }
    if size:
        res['size'] = size
    if page and size:
        res['from'] = (page - 1) * size
    if source:
        res['_source'] = source
    return res


def match(field: str, query: str, page: str = None, size: str = None, source: list = None):
    res = {
        "query": {
            "match": {
                field: query
            }
        }
    }
    if size:
        res['size'] = size
    if page:
        res['from'] = (page - 1) * size
    if source:
        res['_source'] = source
    return res


def nested(type: str, field: str, query: str, page: int = None, size: int = None, source: list = None):
    res = {
        "query": {

        }
    }
    return res


def should(field: str, query: list, page: int = None, size: int = None, source: list = None):
    res = {
        "query": {
            "bool": {
                "should": []
            }
        }
    }
    for item in query:
        res['query']['bool']['should'].append({"match": {field: item}})
    if size:
        res['size'] = size
    if page:
        res['from'] = (page - 1) * size
    if source:
        res['_source'] = source
    return res
