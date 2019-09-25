"""Rule functions."""

from api.graph.utility.relation_rule.translate_rule import translate

rule_dict = {
    "父亲": "父子",
    "母亲": "母子",
    "母组织": "母组织",
    "位于": "位于",
}

ignore_list = set([
    "子女", "包含", "子组织"
])


def merge_rule(head, tail, relations, ignore):
    """Check if there is a relation between head and tail.

    :param head:
    :param tail:
    :param relations:
    :return:
    """
    result = set([])
    for r in relations:
        relation = translate(r["type"])
        if relation in rule_dict:
            if r["from"] == head and r["to"] == tail:
                result.add(rule_dict[relation])
            if r["from"] == tail and r["to"] == head:
                result.add(rule_dict[relation])
        elif relation in ignore_list and ignore:
            continue
        else:
            result.add(relation)
    return result
