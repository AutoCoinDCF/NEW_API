CONFIG_column_useage = {
    "SQLGraph-EEDGraphSingular_v16-entity": {
        "vertex_column_map_index": ('SQLGraph', 'EEDGraphSingular_v16', 'entity'),
        "vertex_columns": [
            "__v",
            "entity_name",
            "chinese_name",
            "meta_type",
            "entity_type",
        ]
    },
    "SQLGraph-EEDGraphSingular_v16-event": {
        "vertex_column_map_index": ('SQLGraph', 'EEDGraphSingular_v16', 'event'),
        "vertex_columns": [
            "__v",
            "doc_id",
            "event_type",
            "meta_type",
            "event_subtype",
            "event_content",
            "publish_time",
            "time_list",
            "entity_list",
            "location_list",
            "entity_type",
        ]
    },
    "SQLGraph-EEDGraphSingular_v16-document": {
        "vertex_column_map_index": ('SQLGraph', 'EEDGraphSingular_v16', 'document'),
        "vertex_columns": [
            "__v",
            "raw_id",
            "channel",
            "i_sn String",
            "title String",
            "time String",
            "entity_list",
            "entity_type",
            "meta_type"
        ]
    },
    "SQLGraph-EEDGraphSingular_v16-edge": {
        "edge_column_map_index": ('SQLGraph', 'EEDGraphSingular_v16', 'edge'),
        "edge_columns": [
            "__s",
            "__d",
            "id",
            "relation_id",
            "type",
            "from_meta_type",
            "to_meta_type"
        ]
    },
    "SQLGraph-EEDGraphSingular_v16-all": {
        "vertex_column_map_index": ('SQLGraph', 'EEDGraphSingular_v16', 'all'),
        "vertex_columns": [
            "__v",
            "entity_name",
            "chinese_name",
            "meta_type",
            "entity_type",
            "doc_id",
            "event_type",
            "event_subtype",
            "event_content",
            "publish_time",
            "time_list",
            "entity_list",
            "location_list",
            "raw_id",
            "channel",
            "i_sn",
            "title",
            "time"
        ]
    }
}
