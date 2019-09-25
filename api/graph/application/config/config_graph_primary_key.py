CONFIG_graph_primary_key = {
    "SQLGraph": {
        "vertex_primary_key": "__v",
        "edge_primary_key": "relation_id",
        "edge_src_key": "__s",
        "edge_dst_key": "__d",
    },

    "ES": {
        "vertex_primary_key": "_id",
    },

    "Frontend": {
        "vertex_primary_key": "id",
        "edge_primary_key": "id",
        "edge_src_key": "from",
        "edge_dst_key": "to",
    }
}
