""" relation types that should be kept when extend neighbors for each vertex types """

CONFIG_extend_relation_types = {
    "entity": {
        "human": {
            "member of",  # entity
            "employer",
            "educated at",
            "work at",
            "father",
            "mother",
            "spouse",
            "child",
            "sibling",
            "include_entity",  # document
            "include_event",
            "employee",
            "position held",
            "chairperson",
            "Twitter username",
            "Facebook ID",
            "publish",  # document
            "mention",
            "forward"
        },

        "organization": {
            "founded by",  # entity
            "chairperson",
            "chief executive officer",
            "business division",
            "parent organization",
            "subsidiary",
            "more position",
            "has part",
            "include_entity",  # document
            "include_event",
            "host",
            "employer",
            "employee"
        },

        "administrative": {
            "head of state",  # entity
            "head of government",
            "office held by head of government",
            "head of government",
            "legislative body",
            "executive body",
            "highest judicial authority",
            "located in the administrative territorial entity",
            "contains administrative territorial entity",
            "diplomatic relation",
            "twinned administrative body",
            "shares border with",
            "include_entity",  # document
            "include_event",
            "employee"
        },
        "weapon": {  # 暂无
            "country of origin",  # entity
            "country",
            "manufacturer",
            "developer",
            "designed by",
            "operator",
            "guidance system",
            "ammunition",
            "powerplant",
            "avionics",
            "include_entity",  # document
            "include_event",
            "employee"
        },
        "CyberUser": {
            "Twitter username",
            "Facebook ID",
            "publish",   # document
            "mention",
            "forward"
        },
        "other": {  # 暂无
            "founded by",  # entity
            "chairperson",
            "chief executive officer",
            "business division",
            "parent organization",
            "subsidiary",
            "more position",
            "has part",
            "include_entity",  # document
            "include_event"
        },
    },

    "event": {
        # todo: please finish these rules
        "divorce": {
            "person",
            "include_entity",
            "include_event",
        },
    },

    "document": {
        "document": {
            "include_entity",
            "include_event",
            "publish",
            "mention",
            "forward"
        }
    },
}

