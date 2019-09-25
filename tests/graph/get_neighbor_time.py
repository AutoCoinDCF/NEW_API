from api.configs.MiddleEndConfig import CONFIG
from api.BackendAPI.BackendAPI import SPACE_BACKEND_API
from tests.utils.code_timer import code_timer

CONFIG.choose_config(WebAPI_choice='test', GraphAPI_choice='test')
SPACE_BACKEND_API.set_after_CONFIG()

with code_timer("get neighbor time:", show_start=True):
    nodeIds = ['Q30']
    response = SPACE_BACKEND_API.Graph_API.select_neighbor_by_id(nodeIds)

print(response['data'][0]["nodes"][:10])
