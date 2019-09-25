"""
    the columns' name mapping, from old name(backend name) to (new name)frontend name
    the index level:

    database_system_name:
        database_name:
            table_name(table in database or table of special operator like vertex):
                old_col:new_col
                old_col:new_col
                ......

"""

CONFIG_column_mapping = {

    "SQLGraph": {
        "EEDGraphSingular_v16": {
            "entity": {
                "__v": "id",
                "Entity_name": "Entity_name",
                "Chinese_name": "Chinese_name",
                "meta_type": "meta_type",
                "Entity_type": "Entity_type",
            },
            "edge": {
                "__s": "from",
                "__d": "to",
                "id": "id",
                "relation_id": "relation_id",
                "type": "type"
            },
            "event": {
                "__v": "id",
                "doc_id": "doc_id",
                "event_type": "event_type",
                "meta_type": "meta_type",
                "event_subtype": "event_subtype",
                "publish_time": "publish_time",
                "time_list": "time_list",
                "entity_list": "entity_list",
                "location_list": "location_list",
                "Entity_type": "Entity_type"
            },
            "document": {
                "__v": "id",
                "raw_id": "raw_id",
                "channel": "channel",
                "site_name": "site_name",
                "title": "title",
                "publish_time": "publish_time",
                "entity_list": "entity_list",
                "Entity_type": "Entity_type",
                "meta_type": "meta_type"
            },
            "all": {
                "__v": "id",
                "Entity_name": "Entity_name",
                "Chinese_name": "Chinese_name",
                "meta_type": "meta_type",
                "Entity_type": "Entity_type",
                "doc_id": "doc_id",
                "event_type": "event_type",
                "event_subtype": "event_subtype",
                "publish_time": "publish_time",
                "time_list": "time_list",
                "entity_list": "entity_list",
                "location_list": "location_list",
                "raw_id": "raw_id",
                "channel": "channel",
                "site_name": "site_name",
                "title": "title"
            }
        }
    },
}
