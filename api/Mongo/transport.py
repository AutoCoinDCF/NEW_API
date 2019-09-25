from ast import literal_eval
import api.Mongo.config_data_purpose_field as INDEX


def str_to_container(str_or_obj: str or object):
    """
    transform string in database to container,
    for example: "['Q23','Q30']" --> ['Q23','Q30']
    """
    try:
        return literal_eval(str_or_obj)
    except (ValueError, SyntaxError):
        return str_or_obj


def es_search_res_handle(typelabel: str, data: dict):
    return rename(filter_and_change(typelabel, data))


def rename(data: dict):
    res = []
    for item in data:
        tmp = {}
        for key in item:
            tmp['_'.join(key.split(" "))] = item[key]
        res.append(tmp)
    return res


def filter_and_change(typelabel: str, data: dict):
    # 对当前的字段的值为"'[...]'"了类型的字段进行筛选并转换格式
    res = []
    for item in data:
        tmp = {}
        for key in item:
            if key not in list(INDEX.all[typelabel].values()):
                continue
            if key in ['type']:
                continue
            if item[key] != "":
                if isinstance(item[key], str) and '[' in item[key] and ']' in item[key]:
                    item[key] = str_to_container(item[key])
                    if not len(item[key]):
                        continue
                tmp[key] = item[key]
        res.append(tmp)
    return res
