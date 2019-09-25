#%%
import pandas as pd
from pandas import DataFrame, Series
from api.configs.MiddleEndConfig import CONFIG
from api.BackendAPI.BackendAPI import SPACE_BACKEND_API
from api.graph.utility.MiddleDataFrameFolder import MiddleDataFrameGraph
from api.graph.application.config.config_column_useage import CONFIG_column_useage
from api.graph.application.config.config_graph_primary_key import CONFIG_graph_primary_key

#%%
# 需要扩展的边的类型
extend_relation_types = {
    "entity": {
        "human": {
            "member of",
            "employer",
            "educated at",
            "work at",
            "father",
            "mother",
            "spouse",
            "child",
            "sibling",
        },

        "organization": {
            "founded by",
            "chairperson",
            "chief executive officer",
            "business division",
            "parent organization",
            "subsidiary",
            "more position",
        },

        "administrative": {
            "head of state",
            "head of government",
            "office held by head of government",
            "head of government",
            "legislative body",
            "executive body",
            "highest judicial authority",
            "located in the administrative territorial entity",
            "contains administrative territorial entity",
            "diplomatic relation",
            "twinned administrative body",
            "shares border with",
        },

        "weapon": {  # 暂无
            "country of origin",
            "country",
            "manufacturer",
            "developer",
            "designed by",
            "operator",
            "guidance system",
            "ammunition",
            "powerplant",
            "avionics",
        }
    },

    "event": {
        ...
    },

    "document": {
        "document": {
            "include_entity",
            "include_event",
        }
    },
}

CONFIG.choose_config(*["dev"]*4)
INQUIRY = SPACE_BACKEND_API.Graph_API.graph_inquiry_helper

#%%
nodeIds = [
    # human
    "Q23",  # 乔治华盛顿
    "Q15031",  # 习近平
    # organization
    "Q17427",  # 中国共产党
    "Q7049542",  # 无党派主义
    "Q41726",  # 共济会
    # administrative
    "Q30",  # 美国
    "Q148",  # 中国
]
type_label = "entity"

#%%
result = INQUIRY.select_related(nodeIds=nodeIds, type_label=type_label)
graph = MiddleDataFrameGraph(
    code=result["code"],
    message=result["message"],
    vertex_data=result["data"][0]["nodes"],
    edge_data=result["data"][0]["links"],)

graph.graph_select_and_rename_columns(
    **CONFIG_column_useage[f"SQLGraph-{'EventGraph2'}-vertex_summary"],
    **CONFIG_column_useage[f"SQLGraph-{'EventGraph2'}-edge"])

#%%
nodes, links = graph.data["nodes"], graph.data["links"]
typed_nodes = nodes.loc[:, :]

def vertex_type(row):
    if row["meta_type"] == 'entity':
        return row["entity_type"]
    elif row["meta_type"] == 'event':
        return row["event_subtype"]
    elif row["meta_type"] == 'document':
        return 'document'
    else:
        raise TypeError(f"meta_type {row['meta_type']} is not 'entity', 'event' or 'document'")

typed_nodes["vertex_type"] = nodes.apply(func=vertex_type, axis= "columns")

#%%
input_nodes = typed_nodes.loc[typed_nodes["id"].isin(nodeIds), :]

filtered_links = DataFrame()
for name, group in input_nodes.groupby(["meta_type", "vertex_type"]):
    meta_type, vtx_type = name
    for root in ("from", "to"):
        append_links = links.loc[links[root].isin(group["id"]) & links["type"].isin(extend_relation_types[meta_type][vtx_type]), :]
        filtered_links = filtered_links.append(append_links, ignore_index=True)
filtered_links.drop_duplicates(subset=["id"], inplace=True)

#%%
filtered_nodes = nodes.loc[nodes["id"].isin(pd.concat([filtered_links["from"], filtered_links["to"]])), :]
#%%
graph.separator_to_underline()
#graph.table_to_IdList(table_name="nodes")



