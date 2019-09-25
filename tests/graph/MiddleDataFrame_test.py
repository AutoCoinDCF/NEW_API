from pandas import DataFrame
from functools import partial

from api.configs.MiddleEndConfig import CONFIG
from api.BackendAPI.BackendAPI import SPACE_BACKEND_API
from tests.utils.code_timer import code_timer
from api.graph.utility.MiddleDataFrameFolder import MiddleDataFrameGraph as MDFG

CONFIG.choose_config(*["dev"]*4)
SPACE_BACKEND_API.set_after_CONFIG()
GU = SPACE_BACKEND_API.Graph_API.graph_inquiry_helper
ES = SPACE_BACKEND_API.EsSearch_API

# 便于查询es的两个偏函数
get_entity_acc = partial(
    ES.accFindbyIdList,
    index=CONFIG.ESSearchConfig.entity_index,
    doc_type=CONFIG.ESSearchConfig.entity_doc_type)
get_entity_rough = partial(
    ES.roughFindbyIdList,
    index=CONFIG.ESSearchConfig.entity_index,
    doc_type=CONFIG.ESSearchConfig.entity_doc_type)

nodeIds = ["Q20", "Q23", "Q30"]
with code_timer("search big table:"):
    entity_detail = get_entity_acc(idlist=nodeIds)

df_graph = MDFG(code=entity_detail["code"], vertex_data=entity_detail["data"], vertex_primary_key="_id")

many, few = df_graph.split_by_neighbor_number(limit=20, keep_property=False)  # type: DataFrame
few_stack = DataFrame(few.stack())
df = few_stack.reset_index().rename(columns={"level_1": "relation_type", 0:"neighbor_ids"})
df = df.loc[df["neighbor_ids"].astype(bool)]

pass
