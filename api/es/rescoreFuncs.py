import math


def rescore_chinese_entities(entity_list):
    non_other_list = []
    other_list = []

    for entity in entity_list:
        if "type" in entity:
            entity_type = entity["type"]
        else:
            entity_type = entity["entity_type"]

        if "chinese_name" not in entity:
            entity["chinese_name"] = entity["name"]

        if entity_type != "other":
            non_other_list.append({
                "id": entity["id"],
                "chinese_name": entity["chinese_name"],
                "entity_name": entity["entity_name"],
                "entity_type": entity["entity_type"]
            })
        else:
            other_list.append({
                "id": entity["id"],
                "chinese_name": entity["chinese_name"],
                "entity_name": entity["entity_name"],
                "entity_type": entity["entity_type"]
            })

    new_list = []
    for entity in non_other_list:
        hit_count = 0
        for other in other_list:
            if entity["chinese_name"]:
                if entity["chinese_name"] in other["chinese_name"]:
                    hit_count += 1
            else:
                if entity["entity_name"] in other["entity_name"]:
                    hit_count += 1
        id = int(entity["id"][1:])
        # id_score = (20 - len(entity["id"])) * 1.5
        id_score = (24 - math.log(id)) * 1.5
        entity["weight"] = hit_count + id_score
        if entity["id"][0] == 'A':
            entity["weight"] -= 100000
        new_list.append(entity)

    new_list = sorted(new_list, key=lambda e: e["weight"], reverse=True)
    if len(new_list) > 20:
        return new_list
    else:
        return new_list + other_list
