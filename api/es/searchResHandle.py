def getSourceOne(data: dict):
    return data['_source']


def getSourceMany(data: list):
    for i in range(len(data['hits'])):
        data['hits'][i] = getSourceOne(data['hits'][i])
    return data['hits']


def addIdOne(data: dict):
    data['_source']['id'] = data['_id']


def addIdMany(data: list):
    for item in data['hits']:
        item['_source']['id'] = item['_id']


def addTypeMany(data: list):
    for item in data['hits']:
        item['_source']['type'] = item['_type']


def filter(data: dict, fields: list):
    res = {}
    for item in data:
        if item in fields:
            res[item] = data[item]
    return res


def isError(result: int, query: int):
    if (result != query):
        return True
    return False


def getIds(field: str, data: list):
    res = {"values": []}
    for index in range(len(data)):
        res['values'].append(data[index][field])
    return res


def check(idlist: list, data: list):
    res = []
    reslist = getIds("_id", data['hits'])
    if isError(data['total'], len(idlist)):
        for id in idlist:
            if id not in reslist['values']:
                res.append(id)
        return (-1, res)
    return (0, None)


def resFix(data):
    if "error" in data and data['code'] == 0:
        data.pop("error")
    return data
