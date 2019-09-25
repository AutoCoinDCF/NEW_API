import api.configs.dynamic_config as dy_config

from api.log.QBLog import QBLog
from api.Mongo import DbOpsFactory


class OperatorApplication(object):
    def __init__(self, db_type='mongo', host="10.60.1.140", port=6080, usr="root", pwd="111111"):
        self.db = DbOpsFactory.get_dbops_instance(
            db_type=db_type, host=host, port=port, usr=usr, pwd=pwd)
        self.logger = QBLog({'LOG_LEVEL': dy_config.LOG_LEVEL}, self.__class__.__name__)

    def operator_test(self, eventIds: list) -> dict:
        """
        Find the detail event information list by entity id list.
        param eventIds: The event id list.
        return: Result data.
        """
        res = {"code": 0, "data": []}
        result = self.db.find_event_detail_by_id(eventIds)

        if len(result) != len(eventIds):
            res["code"] = -1
            self.logger.error(f'Incoming id error')
            return res

        for data in result:
            add = {}
            type_lower = data["event_type"].lower()
            subtype_lower = data["event_subtype"].lower()
            add["id"] = data["_id"]
            add["event_type"] = type_lower
            add["event_subtype"] = subtype_lower
            add["description"] = data["event_content"]["ch"]
            add["entity_list"] = data["entity_list"]
            add["time_list"] = data["time_list"]
            add["location_list"] = data["location_list"]
            add["publish_time"] = data["publish_time"]
            res["data"].append(add)
        return res
