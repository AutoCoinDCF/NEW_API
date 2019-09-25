Graph = {
    "type": [
        "entity",
        "event",
        "document"
    ],
    "subtype": {
        "entity": [
            "human", "organization", "administrative"
        ],
        "event": [
            "Release-Parole"
        ],
        "document": [
            "web"
        ]
    },
    "attr": {
        "entity": "EntityAttr",
        "event": "EventAttr",
        "document": "DocumentAttr"
    },
    "AttrIDName": {
        "human": {
            ""
        }
    }
}

channel = {
    1: "新闻",
    2: "论坛",
    3: "博客",
    4: "境外新闻",
    5: "微博",
    8: "元搜索",
    11: "客户端",
    20: "推特",
    30: "短视频",
    40: "微信",
    41: "360",
    16: "特殊通道",
    18: "darpa"
}

set_table = {
    "insert_fields": ["name", "des", "nodeIds", "modify_time", "create_time", "modify_user", "create_user", "type"],
    "update_fields": ["id", "name", "des", "nodeIds", "modify_time", "modify_user", "type"]
}

project_table = {
    "insert_fields": ["name", "des", "image", "data", "modify_time", "create_time", "modify_user", "create_user",
                      "type"],
    "update_fields": ["id", "name", "des", "data", "nodeIds", "modify_time", "modify_user", "type"]
}
