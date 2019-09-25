from functools import partial

from api.configs.MiddleEndConfig import CONFIG
from api.BackendAPI.BackendAPI import SPACE_BACKEND_API

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

#nodeIds = ["Q20", "Q23", "Q30"]
#nodeIds = ["Q23", "Q370363", "Q1413"]
nodeIds = ["Q20", "Q30"]
limit = 20
result = SPACE_BACKEND_API.Graph_API.select_neighbor_by_id_aggregated(nodeIds=nodeIds, limit=2)

pass
