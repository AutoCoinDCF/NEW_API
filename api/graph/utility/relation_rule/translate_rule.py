"""Translate relation into Chinese."""

translate_dict = {
    "spouse": "夫妻",
    "mother": "母亲",
    "father": "父亲",
    "child": "子女",
    "sibling": "兄弟姐妹",
    "partner": "情侣",
    "occupation": "职业",
    "member of political party": "所属政党",
    "country of citizenship": "国籍",
    "member of": "所属组织",
    "employer": "雇主",
    "business division": "业务部门",
    "subsidiary": "子组织",
    "parent organization": "母组织",
    "chief executive officer": "首席执行官",
    "founded by": "创办者",
    "chief operating officer": "首席运营官",
    "country": "所属国家",
    "capital": "首府",
    "contains administrative territorial entity": "包含",
    "located in the administrative territorial entity": "位于",
    "diplomatic relation": "外交关系",
    "shares border with": "接壤",
    "head of government": "政府首长",
    "head of state": "国家元首",
    "Twitter username": "twitter账号",
    "Facebook ID": "facebook 账号",
    "include_event": "包含",
    "include_entity": "包含",
    "publish": "发布",
    "mention": "提及",
    "forward": "转发"
}


def translate(relation_type: str) -> str:
    """Translate function.

    :param relation_type:
    :return:
    """
    if relation_type in translate_dict:
        return translate_dict[relation_type]
    else:
        return "未知"
