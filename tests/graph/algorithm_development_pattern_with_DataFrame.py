#%%
import pandas as pd
from pandas import DataFrame, Series
from collections import defaultdict

from api.configs.MiddleEndConfig import CONFIG
from api.BackendAPI.BackendAPI import SPACE_BACKEND_API
from api.graph.utility.MiddleDataFrameFolder import MiddleDataFrameGraph
from api.graph.application.config.config_column_useage import CONFIG_column_useage
from api.graph.application.config.config_graph_primary_key import CONFIG_graph_primary_key

CONFIG.choose_config(*["dev"]*4)
INQUIRY = SPACE_BACKEND_API.Graph_API.graph_inquiry_helper

#%%
# API输入
nodeIds = [
    # human
    "Q23",  # 乔治华盛顿
    "Q15031",  # 习近平
]


#%%
# API执行流
result = INQUIRY.select_related(nodeIds=nodeIds, type_label="entity")
graph = MiddleDataFrameGraph(
    code=result["code"],
    message=result["message"],
    vertex_data=result["data"][0]["nodes"],
    edge_data=result["data"][0]["links"],)
graph.graph_select_and_rename_columns(
    **CONFIG_column_useage[f"SQLGraph-{'EventGraph2'}-vertex_summary"],
    **CONFIG_column_useage[f"SQLGraph-{'EventGraph2'}-edge"])
graph.keep_certain_types_links(nodeIds=nodeIds)
graph.add_name()
#%%
# 算法原型
######################################################
# 参数
nodesDataFrame: DataFrame = graph.data["nodes"]
linksDataFrame: DataFrame = graph.data["links"]
nodeIds = nodeIds
root: str = "from"
##############
# 算法
neighbor_column = "to" if root=="from" else "from"
group_dict = defaultdict(dict)
linksDataFrame = linksDataFrame.loc[linksDataFrame[root].isin(nodeIds), :]
for name, group in linksDataFrame.groupby([root, "type"]):
    vtx_id, relation_type = name[0], name[1]
    selected_node_ids: DataFrame = group.loc[:, [neighbor_column]]
    selected_node_ids.rename(columns={neighbor_column: "id"}, inplace=True)
    selected_nodes: DataFrame = selected_node_ids.join(other=nodesDataFrame.set_index('id'), on="id")
    selected_nodes = selected_nodes.loc[:, ["id", "name"]]
    group_dict[vtx_id][relation_type] = selected_nodes.to_dict(orient="records")
    ...
...
######################################################
#%%
graph.separator_to_underline()
graph.table_to_IdList(table_name="nodes")
