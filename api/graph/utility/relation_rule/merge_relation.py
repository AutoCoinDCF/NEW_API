"""Merge all relations between a given entity pair.
Author: Long Bai
E-mail: bailong18b@ict.ac.cn
"""

from api.graph.utility.relation_rule.rule import merge_rule


def merge(head, tail, relations, ignore=True):
    """Merge relation list given an entity pair.

    :param head:
    :param tail:
    :param relations:
    :return:
    """
    # get id
    rid = None
    for r in relations:
        if isinstance(rid, int) and rid != None:
            rid = str(rid)
        if isinstance(r["id"], int):
            r["id"] = str(r["id"])
        if rid is None or rid > r["id"]:
            rid = r["id"]
    # merge relations
    relation_type = merge_rule(head, tail, relations, ignore)
    relation_type = "、".join(relation_type)
    return {"id": rid, "type": relation_type, "from": head, "to": tail, "direct": False}


def reduction(relations):
    """Reduce the relation list by entity pairs.

    :param relations:
    :return:
    """
    # collect entities
    entities = set([])
    for r in relations:
        entities.add(r["from"])
        entities.add(r["to"])
    entities = list(entities)
    # enumerate entities
    relation_list = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            head, tail = entities[i], entities[j]
            tmp_relation_list = []
            for r in relations:
                if r["from"] == head and r["to"] == tail or \
                        r["from"] == tail and r["to"] == head:
                    tmp_relation_list.append(r)
            if tmp_relation_list:
                relation_instance = merge(head, tail, tmp_relation_list)
                relation_list.append(relation_instance)
    return relation_list


def protogenesis(relations):
    relations_list = []
    for link in relations:
        relation_instance = merge(link["from"], link["to"], [link], ignore=False)
        relations_list.append(relation_instance)
    return relations_list
