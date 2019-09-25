import traceback
import uuid, os, re, collections, json, operator, time
from functools import reduce
from pprint import pprint

import api.Mongo.transport as TOOL
import api.Mongo.config_mapping as MAPPING
import api.configs.entity_img as entity_img
import api.es.config.config_statistics as STA
import api.configs.dynamic_config as dy_config

from api.log.QBLog import QBLog
from api.Mongo import DbOpsFactory
from api.Mongo.utility import Mon_tool
# from api.web.utils import func_line_time
from api.graph.utility.utility import Match_list
from api.graph.utility.utility import NestedHelper
from api.Mongo import config_data_purpose_field as CF
from api.Mongo.schema import entity_schema, event_schema, document_schema
from api.graph.application.graph_application import GraphApplication


class MongoApplication(object):
    def __init__(self, host="10.60.1.140", port=6080, usr="root", pwd="111111"):
        self.db = DbOpsFactory.get_dbops_instance(
            'mongo', host, port, usr, pwd)
        self.m_tool = Mon_tool()
        path = '/mongo.config'
        config_path = os.path.join(os.path.dirname(__file__) + path)
        self._config = {}
        with open(config_path, 'r') as f:
            self._config = collections.OrderedDict(json.load(f))
        self.logger = QBLog({'LOG_LEVEL': dy_config.LOG_LEVEL}, self.__class__.__name__)
        self.graph = GraphApplication()
        self.math =  Match_list()
        self.entity_img = entity_img

    def Attr_sql(self, typelabel, entityIds, eventIds, docIds, all=False):

        if typelabel == "entity" and all:
            return {"idlist": entityIds, "count": len(entityIds)}
        elif typelabel == "entity":
            return self.db.find_subtype_by_entity(entityIds)

        if typelabel == "event" and all:
            return {"idlist": eventIds, "count": len(eventIds)}
        elif typelabel == "event":
            return self.db.find_subtype_by_event(eventIds)

        if typelabel == "document" and all:
            return {"idlist": docIds, "count": len(docIds)}
        elif typelabel == "document":
            return self.db.find_subtype_by_document(docIds)

    def ObjectsType(self, entityIds, eventIds, docIds):
        _len = len(entityIds + eventIds + docIds)
        fieldName_frist = {'firstLevelId': "ObjectsType", 'firstLevelName': "对象类型", "subStatisticsAttr": []}
        frist = []
        for _second in STA.Graph['type']:
            res = {}
            res["secondLevelId"] = "_".join("_".join(_second.split('-')).split(" "))
            res["secondLevelName"] = MAPPING.chinese['type'][_second] if _second in MAPPING.chinese['type'] else res[
                "secondLevelId"]
            res["specificStaticsAttr"] = []
            tmp_all = {}
            _all = self.Attr_sql(_second, entityIds, eventIds, docIds, True)
            if _all:
                tmp_all["thirdLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
                tmp_all["thirdLevelName"] = "全部"
                tmp_all["count"] = _all["count"]
                tmp_all["idlist"] = _all["idlist"]
                tmp_all["per"] = int(tmp_all['count'] / _len * 100) if _len else 0
                res["specificStaticsAttr"].append(tmp_all)
            for _select in self.Attr_sql(_second, entityIds, eventIds, docIds):
                tmp = {}
                if isinstance(_select["_id"], int):
                    tmp["thirdLevelId"] = str(_select["_id"])
                    if tmp["thirdLevelId"] in ["1"]:
                        _select["_id"] = "news"
                    elif tmp["thirdLevelId"] in ["16", "18"]:
                        _select["_id"] = "proprietary"
                    elif tmp["thirdLevelId"] in ["2", "3", "4", "5", "8", "11", "30", "40", "41", "20"]:
                        _select["_id"] = "social_contact"
                else:
                    tmp["thirdLevelId"] = "_".join("_".join(_select["_id"].split('-')).split(" "))
                tmp["thirdLevelName"] = MAPPING.chinese['type'][_select["_id"].lower()] if _select["_id"].lower() in \
                                                                                           MAPPING.chinese['type'] else \
                    tmp["thirdLevelId"]
                tmp["count"] = _select["count"]
                tmp["idlist"] = _select["idlist"]
                tmp["per"] = int(tmp['count'] / _len * 100)
                res["specificStaticsAttr"].append(tmp)
                res["specificStaticsAttr"] = sorted(res["specificStaticsAttr"],
                                                    key=lambda x: x["count"],
                                                    reverse=True)
            # 合并document和event的二级分类
            _d = {}
            if _second in ["document", "event"] and "specificStaticsAttr" in res:
                for _each in res["specificStaticsAttr"]:
                    if _each["thirdLevelName"] in _d:
                        _each["count"] += _d[_each["thirdLevelName"]]["count"]
                        _each["per"] = int(_each["count"] / _len * 100)
                        _each["idlist"] += _d[_each["thirdLevelName"]]["idlist"]
                        _d[_each["thirdLevelName"]] = _each
                    else:
                        _d[_each["thirdLevelName"]] = _each
                res["specificStaticsAttr"] = list(_d.values())
            res["typecount"] = len(res["specificStaticsAttr"]) - 1
            frist.append(res)
        fieldName_frist["subStatisticsAttr"].extend(frist)
        return fieldName_frist

    def num_AttrStatistics(self, entityIds, eventIds, docIds):
        Entity_id = entity_schema.get('Entity_id')
        _len = len(entityIds + eventIds + docIds)
        sub_types = [" ".join(k.split("_")) for k in self._config['graphStatistics']['numbers']]
        res_entity = self.db.find_subentity_by_entity_sub_type(entityIds, sub_types)
        res_entity = [k for k in res_entity if len(k) != 2]
        if Entity_id in sub_types:
            sub_types.remove(entity_schema.get(Entity_id))
        data = {}
        for _rec in res_entity:
            for _sub in _rec:
                if _sub in sub_types:
                    if _sub not in data:
                        data[_sub] = {}
                    for _ssub in _rec[_sub]:
                        if _ssub in data[_sub]:
                            data[_sub][_ssub].append(_rec[Entity_id])
                        else:
                            data[_sub][_ssub] = []
                            data[_sub][_ssub].append(_rec[Entity_id])
        frist = []
        for d in data:
            result_second = {}
            result_second["secondLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
            result_second["secondLevelName"] = MAPPING.chinese["entity"][d] if d in MAPPING.chinese["entity"] else d
            result_second["specificStaticsAttr"] = []
            res = []
            new_dict = {}
            for v in data[d]:
                vv = int(float(re.sub("\D", "", v)))
                new_dict[vv] = data[d][v]

            def num_group(A, B, C, _A, _B, _C):
                sta_dict = [
                    ("<{}".format(0), []),
                    ("{}-{}".format(0, _A), []),
                    ("{}-{}".format(_A, _B), []),
                    ("{}-{}".format(_B, _C), []),
                    (">{}".format(_C), [])
                ]
                for vv in new_dict:
                    value = [x for x in new_dict[vv]]
                    if vv < 0:
                        sta_dict[0][1].extend(value)
                    elif vv >= 0 and vv < A:
                        sta_dict[1][1].extend(value)
                    elif vv >= A and vv < B:
                        sta_dict[2][1].extend(value)
                    elif vv >= B and vv < C:
                        sta_dict[3][1].extend(value)
                    elif vv >= C:
                        sta_dict[4][1].extend(value)
                return sta_dict

            if d == "area":
                sta_dict = num_group(5000000, 10000000, 15000000, "500万", "1000万", "1500万")
            if d == "population":
                sta_dict = num_group(50000000, 100000000, 200000000, "5000万", "1亿", "2亿")
            # 该字段在mongo中没有查到，所以无法分类,参考sql: db.getCollection("Sys_Property").find({"area": {$exists: true}})
            if d == "GDP":
                sta_dict = num_group(5000000, 10000000, 15000000, "500万", "1000万", "1500万")
            if d == "employees":
                sta_dict = num_group(1000, 5000, 10000, "1000", "5000", "10000")

            # 写入
            for v in sta_dict:
                if v[1]:
                    # 其中人口如果不去重，同一个国家会有多个人口值(每年的数据)
                    idlist = list(set(v[1]))

                    stmp = {}
                    stmp["thirdLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
                    stmp['thirdLevelName'] = v[0]
                    stmp['count'] = len(idlist)
                    stmp['per'] = int(stmp['count'] / _len * 100)
                    stmp['idlist'] = idlist
                    res.append(stmp)
                    # 按count排序，待后期是否需要
                    # res = sorted(res, key=lambda x: x["count"], reverse=True)
            result_second["specificStaticsAttr"].extend(res)
            result_second["typecount"] = len(result_second["specificStaticsAttr"])
            frist.append(result_second)
        return frist

    def AttrStatistics(self, typelabel, entityIds: list = [], eventIds: list = [],
                       docIds: list = [], doc_e_e_d=False):
        _res_result = []
        def select_entity_by_doc_eve(result: list):
            entity_ids = list(set(reduce(operator.add, list(result.values())))) if result else []
            entity_info = self.db.find_entity_info_by_entity_list(entity_ids)
            for _each in list(entity_info.values()):
                for _sec in _each:
                    _sec["idlist"] = []
                    for _event_id in result:
                        if _sec[entity_schema.get("Entity_id")] in result[_event_id]:
                            _sec["idlist"].append(_event_id)
            return entity_info

        if typelabel == "entity":
            Entity_id = entity_schema.get('Entity_id')
            sub_types = [" ".join(k.split("_")) for k in self._config['graphStatistics'][typelabel]]
            _res_result = self.db.find_subentity_by_entity_sub_type(entityIds, sub_types)
            _res_result = [k for k in _res_result if len(k) != 2]
            sub_types = list(set(sub_types))
            if  Entity_id in sub_types:
                sub_types.remove(entity_schema.get(Entity_id))
            data = {}
            for _rec in _res_result:
                for _sub in _rec:
                    if _sub in sub_types:
                        if _sub not in data:
                            data[_sub] = {}
                        _rec[_sub] = list(set(_rec[_sub]))
                        for _ssub in _rec[_sub]:
                            if _ssub in list(data[_sub].keys()):
                                data[_sub][_ssub].append(_rec[Entity_id])
                            else:
                                data[_sub][_ssub] = []
                                data[_sub][_ssub].append(_rec[Entity_id])
            return data

        if typelabel == "document" and len(docIds) != 0 and not doc_e_e_d:
            _id = document_schema.get("_id")
            sub_types = self._config['graphStatistics'][typelabel]
            _res_result = self.db.find_subdoc_by_doc_sub_type(docIds, sub_types)
            data = {}
            for _rec in _res_result:
                for _sub in _rec:
                    if _sub in sub_types:
                        if _sub not in data:
                            data[_sub] = {}
                        if _rec[_sub].lower() in data[_sub]:
                            data[_sub][_rec[_sub].lower()].append(_rec[_id])
                        else:
                            data[_sub][_rec[_sub].lower()] = []
                            data[_sub][_rec[_sub].lower()].append(_rec[_id])
            return data

        if typelabel == "event":
            if len(eventIds) == 0:
                return []
            else:
                _res_result = self.db.find_entity_list_by_event_id(eventIds)
                return select_entity_by_doc_eve(_res_result)

        if typelabel == "document" and doc_e_e_d:
            if len(docIds) == 0:
                return []
            else:
                _res_result = self.db.find_entity_list_by_doc_id(docIds)
                return select_entity_by_doc_eve(_res_result)

    def TypeAttr(self, entityIds, eventIds, docIds):
        result_all = []
        _len = len(entityIds + eventIds + docIds)
        for _type in STA.Graph['type']:
            result = {}
            result["firstLevelId"] = STA.Graph['attr'][_type]
            result["firstLevelName"] = MAPPING.chinese["AttrName"][result["firstLevelId"]]
            result["subStatisticsAttr"] = []
            if _type in ["entity", "document"]:
                ASTS = self.AttrStatistics(typelabel=_type, entityIds=entityIds, docIds=docIds)
                if ASTS:
                    for sub_type in ASTS:
                        result_second = {}
                        s_type = "_".join(sub_type.split(" "))
                        result_second["secondLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
                        result_second["secondLevelName"] = MAPPING.chinese[_type][s_type] if s_type in MAPPING.chinese[
                            _type] else s_type
                        result_second["specificStaticsAttr"] = []
                        for subsub_type in ASTS[sub_type]:
                            result_third = {}
                            result_third["thirdLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
                            result_third["thirdLevelName"] = MAPPING.chinese['type'][
                                subsub_type.lower()] if subsub_type.lower() in  MAPPING.chinese[
                                                            'type'] else subsub_type
                            if result_third["thirdLevelName"] == "":
                                result_third["thirdLevelName"] = "未知来源"
                            result_third["idlist"] = ASTS[sub_type][subsub_type]
                            result_third["count"] = len(result_third["idlist"])
                            result_third["per"] = int(result_third['count'] / _len * 100)
                            result_second["specificStaticsAttr"].append((result_third))
                            result_second["specificStaticsAttr"] = sorted(result_second["specificStaticsAttr"],
                                                                          key=lambda x: x["count"],
                                                                          reverse=True)
                        result_second["typecount"] = len(result_second["specificStaticsAttr"])
                        result["subStatisticsAttr"].append(result_second)
                if _type == "entity":
                    NUM = self.num_AttrStatistics(entityIds, eventIds, docIds)
                    if NUM:
                        result["subStatisticsAttr"].extend(NUM)
                result_all.append(result)
            if _type in ["event", "document"]:
                Entity_name, Chinese_name = entity_schema.get("Entity_name"), entity_schema.get("Chinese_name")

                def select_entity_list(ids):
                    # 统计需求写死，待之后需求变化写入配置文件
                    for sub_type in ["human", "organization", "administrative"]:
                        if sub_type in ids:
                            tmp = {}
                            tmp["secondLevelId"] = sub_type
                            tmp["secondLevelName"] = MAPPING.chinese["entity"][sub_type]

                            tmp["specificStaticsAttr"] = []
                            for _third in ids[sub_type]:
                                stmp = {}
                                stmp["thirdLevelId"] = "_".join(_third[Entity_name].split(" "))
                                stmp["thirdLevelName"] = _third[Chinese_name] if _third[Chinese_name] != '' else \
                                    stmp["thirdLevelId"]
                                stmp["idlist"] = _third["idlist"]
                                stmp["count"] = len(stmp["idlist"])
                                stmp["per"] = int(stmp["count"] / _len * 100)
                                tmp["specificStaticsAttr"].append(stmp)
                            tmp["typecount"] = len(tmp["specificStaticsAttr"])
                            tmp["specificStaticsAttr"] = sorted(tmp["specificStaticsAttr"], key=lambda x: x["count"],
                                                                reverse=True)
                            result["subStatisticsAttr"].append(tmp)
                    result_all.append(result)

                if _type == "event":
                    _entity_ids = self.AttrStatistics(typelabel=_type, eventIds=eventIds)
                    select_entity_list(ids=_entity_ids)
                elif _type == "document":
                    doc_entity_ids = self.AttrStatistics(typelabel=_type, docIds=docIds, doc_e_e_d=True)
                    select_entity_list(ids=doc_entity_ids)
        return result_all[:3]

    def graphAttr(self, entityIds: list, eventIds: list, docIds: list, type: str):
        """
        :param idlist: query idlist
        :param type: "geo" / "net" / "document"
        :return:
        """
        res = {"code": 0, "data": []}
        res['data'].append(self.ObjectsType(entityIds, eventIds, docIds))
        res['data'].extend(self.TypeAttr(entityIds, eventIds, docIds))

        def result_filter(firstLevelId: list, secondLevelId: list):
            l = []
            f = []
            for idx in res["data"]:
                if idx["firstLevelId"] in firstLevelId:
                    l.append(res["data"].index(idx))
                if idx["firstLevelId"] == "ObjectsType":
                    for _type in idx["subStatisticsAttr"]:
                        if _type["secondLevelId"] in secondLevelId:
                            f.append(idx["subStatisticsAttr"].index(_type))
                    for _e in f[::-1]:
                        idx["subStatisticsAttr"].pop(_e)
            for _frist in l[::-1]:
                res["data"].pop(_frist)

        if type == "geo":
            result_filter(["DocumentAttr"], ["DocumentType"])
        elif type == "document":
            result_filter(["EntityAttr", "EventAttr"], ["EntityType", "EventType"])
        return res

    def aggregation_dispose(self, node_list: list, type_list: list):
        links = []
        node_all = []
        for _ids in node_list:
            node_all.extend(_ids)

        _2_group = self.m_tool._2_group(list(set(node_all)))

        def data_combination(group: list, num: list, subtype: list):
            result = []
            if len(num) != 0:
                for _each in num:
                    _d = {}
                    _d["id"] = "_".join(str(uuid.uuid1()).split("-"))
                    _d["from"] = group[0]
                    _d["to"] = group[1]
                    _d["num"] = _each
                    _d["type"] = subtype[num.index(_each)]
                    _d["undirected_type"] = _d["type"]
                    _d["direct"] = "true"
                    result.append(_d)
            return result

        for _group in _2_group:
            num = []
            subtype = []
            for _ids in node_list:
                if _group[0] in _ids and _group[1] in _ids and type_list[node_list.index(_ids)] not in subtype:
                    num.append(1)
                    subtype.append(type_list[node_list.index(_ids)])
                elif _group[0] in _ids and _group[1] in _ids and type_list[node_list.index(_ids)] in subtype:
                    num[subtype.index(type_list[node_list.index(_ids)])] += 1
            links.extend(data_combination(_group, num, subtype))
        return links

    # @func_line_time
    def aggregation(self, allNodeIds: list, selectNodeIds: list):
        '''
        :param allNodeIds: 前端画布中所有的节点
        :param selectNodeIds: 需要合并的节点，仅支持合并event和document类型
        : 只能聚合doc和entity
        '''
        res = {"code": 0, "data": {"nodes": []}}

        def select_base(type):
            node_list, type_list, links = [], [], []
            for id in selectNodeIds:
                if type == "event":
                    _res_s = self.db.find_entity_doc_id_by_event(id)
                elif type == "document":
                    _res_s = self.db.find_entity_id_by_document(id)
                # 加None判断的原因：id前8位切片在event表和document表都存在，导致doc_id会去event表中查询，有时返回[]。 有时返回None
                str_res = [record for record in _res_s if record is not None]
                if len(str_res) == 0:
                    continue
                node_ids = [_each["id"] for _each in str_res[0][event_schema.get("entity_list")]]
                if type == "event":
                    if str_res[0][event_schema.get("doc_id")] not in selectNodeIds:
                        node_ids.append(str_res[0][event_schema.get("doc_id")])
                if type == "document":
                    _res_related_event = self.db.find_event_by_document(id)
                    # 同上解释
                    str_related_event = [record[document_schema.get("_id")] for record in _res_related_event if
                                         record is not None]
                    for event_id in str_related_event:
                        if event_id not in selectNodeIds:
                            node_ids.append(event_id)
                node_list.append([_id for _id in node_ids if _id in allNodeIds])
                type_list.append(str_res[0][event_schema.get("meta_type")])
            return self.aggregation_dispose(node_list, type_list)

        # 合并event节点
        event_links = select_base("event")

        # 合并document节点
        document_links = select_base("document")

        res["data"]["links"] = event_links + document_links
        return res

    def event_2_time(self, eventIds: list, docIds: list):
        res = {}
        eve_searchResult, doc_searchResult = [], []
        publish_time = document_schema.get("publish_time")

        if eventIds:
            eve_searchResult = self.db.find_time_and_id_by_event_id(eventIds)
        if docIds:
            doc_searchResult = self.db.find_time_and_id_by_document_id(docIds)

        searchResult = eve_searchResult + doc_searchResult

        # values 为过滤组合以int类型类型时间为键，事件id为值的字典
        values = {}
        for _time in searchResult:
            # 部分id的publish_time为''或者-1
            if isinstance(_time[publish_time], str) and _time[publish_time] != '':
                _time[publish_time] = int(_time[publish_time])
            elif _time[publish_time] == "":
                continue
            elif _time[publish_time] == -1:
                continue
            if _time[publish_time] in values:
                values[_time[publish_time]].append(_time[event_schema.get("_id")])
            else:
                values[_time[publish_time]] = []
                values[_time[publish_time]].append(_time[event_schema.get("_id")])

        values_times_str = {}
        res["data"] = {}
        res["data"]["time"] = {}

        # data_time 通过下方for循环, 过滤出str类型时间的列表
        data_time = []
        for _time in [x for x in values]:
            timeArray = time.localtime(_time)
            otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
            data_time.append(otherStyleTime)
            if otherStyleTime in values_times_str:
                values_times_str[otherStyleTime] += values[_time]
            else:
                values_times_str[otherStyleTime] = values[_time]
        res["data"]["time"] = list(set(data_time))
        res["data"]["time"].sort()
        res["data"]["count"] = [data_time.count(x) for x in res["data"]["time"]]
        result = self.math.filling_time_count(res["data"]["time"])

        # 遍历返回的结果中的time字段，在values_times_str字典中找到对应的id，追加到对应的ids的列表中
        result["data"]["ids"] = []
        result["data"]["count"] = []

        i = 0
        for _time in result["data"]["time"]:
            if _time in values_times_str:
                i += 1
                result["data"]["ids"].append(list(set(values_times_str[_time])))
                result["data"]["count"].append(len(list(set(values_times_str[_time]))))
            else:
                result["data"]["ids"].append([])
                result["data"]["count"].append(0)
        return result

    def searchByDocIdList(self, doc_ids):
        res = {"code": 0, "data": []}
        result = self.db.find_doc_detail_by_id(doc_ids)

        if len(result) != len(doc_ids):
            res["code"] = -1
            self.logger.error(f'Incoming id error')
            return res

        _id, title, content, channel, publish_time, site_name = \
            document_schema.get("_id"), document_schema.get("title"), \
            document_schema.get("content"), document_schema.get("channel"), \
            document_schema.get("publish_time"), document_schema.get("site_name")

        for data in result:
            add = {}
            nel = data[channel]
            if (data[publish_time] == -1):
                add["publish_time"] = ""
            elif (data[publish_time]) == "":
                add["publish_time"] = ""
            else:
                if isinstance(data[publish_time], str):
                    data[publish_time] = int(data[publish_time])
                _time = time.localtime(data[publish_time])
                end_time = time.strftime("%Y-%m-%d", _time)
                add["publish_time"] = end_time
                add["time"] = data[publish_time]

            add["id"] = data[_id]
            add["title"] = data[title]["en"]
            add["description"] = data[content]["en"]
            add["channel"] = STA.channel[nel] if nel in STA.channel else nel
            add["site_name"] = data[site_name]
            res["data"].append(add)
        return res

    def translate(self, id: str):
        res = {"code": 0, "data": []}
        try:
            s = self.db.find_doc_translate_by_id(id)[0]
            title, publish_time, content = document_schema.get("title"), \
                                           document_schema.get("publish_time"), \
                                           document_schema.get("content")
        except:
            res["code"] = -1
            self.logger.error(traceback.format_exc())
            return res
        res["data"] = {}
        res["data"]["title"] = s.get(title)["en"]
        res["data"]["title_translate"] = s.get(title)["ch"]
        res["data"]["publish_time"] = s.get(publish_time)
        res["data"]["description"] = s.get(content)["ch"]
        return res

    def findbyIdList(self, eventIds: list) -> dict:
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

        _id, event_type, event_subtype, event_content, \
        entity_list, time_list, location_list, publish_time = \
            event_schema.get("_id"), event_schema.get("event_type"), event_schema.get("event_subtype"), \
            event_schema.get("event_content"), event_schema.get("entity_list"), event_schema.get("time_list"), \
            event_schema.get("location_list"), event_schema.get("publish_time")

        Entity_id, Chinese_name, Entity_name = entity_schema.get("Entity_id"), \
                                               entity_schema.get("Chinese_name"), entity_schema.get("Entity_name")

        for data in result:
            add = {}
            _entity_names, _entity_ids = [], []
            for entity in data[entity_list]:
                _entity_ids.append(entity["id"])
                try:
                    name = self.db.find_entity_name_by_entity_id(entity["id"])
                    _entity_names.append(name[Chinese_name] if name[Chinese_name] else name[Entity_name])
                except TypeError:
                    _entity_names.append(entity["name"])

            type_lower = data[event_type].lower()
            subtype_lower = data[event_subtype].lower()
            add["publish_time"] = data[publish_time]
            add["id"] = data[_id]
            add["event_type"] = MAPPING.chinese['type'][type_lower] if \
                type_lower in MAPPING.chinese['type'] else type_lower
            add["event_subtype"] = MAPPING.chinese['type'][subtype_lower] if \
                subtype_lower in MAPPING.chinese['type'] else subtype_lower
            add["description"] = data[event_content]["ch"]
            add["entity_list"] = {"names": list(set(_entity_names)), "ids": list(set(_entity_ids))}
            add["time_list"] = data[time_list]
            add["location_list"] = data[location_list]
            res["data"].append(add)
        return res

    def accFindbyIdList(self, idlist: list):
        Entity_id, Chinese_name, Entity_name, Entity_type, population, area, Chinese_text, English_text = \
            entity_schema.get("Entity_id"), entity_schema.get("Chinese_name"), \
            entity_schema.get("Entity_name"), entity_schema.get("Entity_type"), \
            entity_schema.get("population"), entity_schema.get("area"), \
            entity_schema.get("Chinese_text"), entity_schema.get("English_text")

        res = {}
        res["data"] = []
        purpose = []
        searchRes = self.db.find_entity_detail_by_entity_id(idlist)
        for tmp in searchRes:
            tmp["id"] = tmp[Entity_id]
            if "name" in tmp:
                tmp["real_name"] = tmp.pop("name")
            if Chinese_text in tmp:
                tmp["description"] = tmp[Chinese_text]
                del tmp[Chinese_text]
            elif English_text in tmp:
                tmp["description"] = tmp[English_text]
                del tmp[English_text]
            else:
                tmp["description"] = ''
            del tmp[Entity_id]
            del tmp["_id"]
            purpose.append(tmp["id"])
            tmp["img"] = "http://10.60.1.143/pic_lib/padded/{id}.png".format(id=tmp["id"]) \
                if tmp["id"] in self.entity_img.data["{}".format(tmp["id"][:2])] else \
                "http://10.60.1.140/assets/images/{}.png".format(tmp[Entity_type])
            if "" == tmp[Chinese_name]:
                tmp[Chinese_name] = tmp[Entity_name]
                tmp["name"] = tmp[Entity_name]
            else:
                tmp["name"] = tmp[Chinese_name]
            res["data"].append(tmp)
        error_ids = [_id for _id in idlist if _id not in purpose]
        res["code"] = 0
        # typ = {"human": [], "organization": [], "administrative": [],
        #        "weapon": [], "geographic_entity": [], "project": [], "other": []}
        typ = {k: [] for k in self._config['entity_subtype']}
        for item in res["data"]:
            typ[item[Entity_type]].append(item)
        data = []
        for key in typ:
            if len(typ[key]) == 0:
                continue
            # 待白龙更新一起写翻译更改此处
            if key in ["human", "organization", "administrative", "weapon", "CyberUser", "other"]:
                data.extend(TOOL.es_search_res_handle(key, typ[key]))
            elif key in ["geographic_entity"]:
                data.extend([{"_".join(k.split(" ")): _dict[k] for k in _dict} for _dict in typ[key]])
        res["data"] = data
        for item in data:
            if population in item:
                item[population] = item[population][-1]
            if area in item:
                item[area] = item[area][-1]
            if Entity_type in item:
                if "_id" in item:
                    del item["_id"]
            if Chinese_name not in item or "" == item[Chinese_name]:
                item[Chinese_name] = item[Entity_name]
                item["name"] = item[Entity_name]
            else:
                item["name"] = item[Chinese_name]
        return res, error_ids

    def roughFindbyIdList(self, idlist: list):
        res = {"code": 0, "data": []}
        tmp_nodes = {}
        tmp_nodes["nodes"] = []
        Entity_type = entity_schema.get("Entity_type")
        data = self.accFindbyIdList(idlist)
        data_end = data[0]["data"]
        for item in data_end:
            tmp = {}
            tmp["id"] = item["id"]
            tmp["img"] = item["img"]
            tmp["Entity_type"] = item[Entity_type]
            tmp["name"] = item["name"]
            tmp["loaded"] = True
            tmp_nodes["nodes"].append(tmp)
        res["data"].append(tmp_nodes)
        return res, data[1]

    def fieldTranslate(self, type: str):
        '''
        根据输入的类型标签，返回对应的字段翻译信息
        类型分为："human", "organization", "administrative", "weapon", "geographic_entity"
                 "event", "document"
        '''
        result = {"code": 0, "data": []}
        all = list(CF.all.keys())
        entity = [d_e for d_e in all if d_e not in ["event", "document"]]
        func = lambda x: [{"cname": CF.translate[x][field], \
                           "ename": '_'.join(field.lower().split(" "))} for field in CF.translate[x]]

        def translate(type):
            index, res = [], {}
            res["type"] = type
            res["type_cn"] = MAPPING.chinese['type'][type.lower()]
            res["attr"] = func(type)
            for _rec in res["attr"]:
                if _rec["ename"] in ["id", "_id"]:
                    index.append(res["attr"].index(_rec))
            for _in in index[::-1]:
                res["attr"].pop(_in)
            result["data"].append(res)

        if type in all:
            translate(type)
        elif type == "entity":
            for _type in entity:
                translate(_type)
        elif type == "all":
            for _type in all:
                translate(_type)
        else:
            self.logger.error(f'Type tag error, value is {type}')
            return {"code": -3}

        return result

    def keywordMatch(self, type: str, Attr: list, page: int, pageSize: int, max: int):
        res = {"code": 0}
        nodes = self.db.find_nodes_by_keyword(type, Attr[0], page, pageSize, max, self._config["entity_subtype"])
        res["data"] = nodes
        return res

    def nodeDetail(self, type: str, nodeIds: list):
        res = {"code": 0, "data": []}
        filter_field = [
            entity_schema.get("Entity_id"), entity_schema.get("Entity_name"), \
            entity_schema.get("Chinese_name"), entity_schema.get("Entity_type"), \
            entity_schema.get("English_text"), entity_schema.get("Chinese_text"),\
        ]

        # 推特账户字段与entity不相同(_), 因此需略过，之后统一配置类似字段
        twitter_field = [
         "followers_count", "friends_count", "listed_count", "favourites_count", "statuses_count", "real_name"
        ]

        def select_node(sql, ids, nodeType):
            nodes = []
            if nodeType == "entity":
                s_data = self.accFindbyIdList(idlist=nodeIds)
                data = NestedHelper(s_data[0]).deep_drop_empty()["data"]
            else:
                data = sql(ids)["data"]
            for record in data:
                node = []
                for _each in record:
                    if nodeType == "entity":
                        cn = CF.translate[record[entity_schema.get("Entity_type")]][" ".join(_each.split("_")) \
                            if _each not in filter_field and _each not in twitter_field else _each] \
                                 if record[entity_schema.get("Entity_type")] != "geographic_entity" else _each,
                    else:
                        cn = CF.translate[nodeType][_each]
                    node.append({
                        "cn": cn[0] if nodeType == "entity" else cn,
                        "en": _each,
                        "val": record[_each]
                    })
                nodes.append(node)
            return nodes

        if type == "entity":
            res["data"] = select_node(sql=self.accFindbyIdList, ids=nodeIds, nodeType=type)
        elif type == "event":
            res["data"] = select_node(sql=self.findbyIdList, ids=nodeIds, nodeType=type)
        elif type == "document":
            res["data"] = select_node(self.searchByDocIdList, ids=nodeIds, nodeType=type)
        else:
            self.logger.error(f'Type tag error, value is {type}')
            return {"code": -3}
        return res

    def doc_top(self, idList: list, data=None):
        l, _list, _dict = [], [], {}
        keywords = document_schema.get("keywords")
        for k in MAPPING.wordType.values():
            l.extend(k)

        result = {
            "code": 0,
            "data": {
                key: [] for key in l
            }
        }

        if not data:
            res = self.db.find_word_by_document(idList)
        else:
            res = data

        # 处理返回的字段
        for record in res:
            for _rec in record:
                if _rec == keywords:
                    _list.extend(record[keywords])
                else:
                    for w_type in record[_rec]:
                        if w_type not in _dict:
                            _dict[w_type] = {}
                        for _d in dict(record[_rec][w_type]):
                            if _d not in _dict[w_type]:
                                _dict[w_type][_d] = dict(record[_rec][w_type])[_d]
                            else:
                                _dict[w_type][_d] = _dict[w_type][_d] + dict(record[_rec][w_type])[_d]
        set_list = list(set(_list))
        _dict[keywords] = {k: _list.count(k) for k in set_list}

        # 更改为前端需求的格式
        for match in _dict:
            for _m in _dict[match]:
                result["data"][match].append({"name": _m, "value": _dict[match][_m]})

        # 排序
        for key in result["data"]:
            result["data"][key] = sorted(result["data"].pop(key), key=lambda x: x["value"], reverse=True)

        # 唯有"PER"不排序，单独排一下
        result["data"]["PER"] = sorted(result["data"]["PER"], key=lambda x: x["value"], reverse=True)

        return result

    def doc_top_by_topic(self, idList: list, ids: list, names: list):
        result = {
            "code": 0,
            "data": []
        }
        if not ids:
            return self.doc_top(idList[0])
        else:
            for _each in range(len(idList)):
                data = self.doc_top(idList[_each])["data"]
                data["name"] = names[_each]
                data["id"] = ids[_each]
                result["data"].append(data)
        return result


    def doc_top_time(self, idList: list, times: list):
        result = {
            "code": 0,
            "data": []
        }
        pass_time = {}
        for _time in times:
            timeArray = time.localtime(int(_time))
            str_today_time = time.strftime("%Y-%m-%d", timeArray)
            today_time = list(self.m_tool.get_timestamp(int(_time)))
            pass_time[str_today_time] = today_time
        pass_time_sorted = {key: pass_time[key] for key in sorted(pass_time, key=lambda x: x, reverse=False)}

        res = self.db.find_word_by_document_from_time(idList)

        _dict = {}
        for rec in res:
            for today in pass_time_sorted:
                if rec["publish_time"] >= pass_time_sorted[today][0] and rec["publish_time"] <= pass_time_sorted[today][1]:
                    del rec["publish_time"]
                    if today not in _dict:
                        _dict[today] = [rec]
                    else:
                        _dict[today].append(rec)
                    break
        for t in _dict:
            processed_data = {}
            processed_data["time"] = t
            processed_data.update(self.doc_top([], _dict[t])["data"])
            result["data"].append(processed_data)
        result["data"] = sorted(result["data"], key=lambda x: x["time"], reverse=False)
        return result

    def wordDoc(self, idList: list, word: list, speech: str):
        result = {
            "code": 0,
            "data": {
                "ids": []
            }}
        _id, keywords = document_schema.get("_id"), document_schema.get("keywords")

        res = self.db.find_doc_by_word_and_type(idList, word, speech)

        # 处理返回的字段
        if speech == keywords:
            result["data"]["ids"] = [k[_id] for k in res]
        else:
            for record in res:
                _dict = {k: [] for k in list(set(reduce(operator.add, list(MAPPING.wordType.values()))))}
                for _rec in record:
                    if _rec not in [keywords, _id]:
                        for w_type in record[_rec]:
                            _dict[w_type] = list(dict(record[_rec][w_type]).keys())
                # 判断所有关键词是否在这条记录的对应的词性中
                if not [False for k in word if k not in _dict[speech]]:
                    result["data"]["ids"].append(record["_id"])

        return result

    def doc_highlight(self, doc_id: str):
        result = {"code": 0}
        data = {}
        related_graph = self.graph.select_related(nodeIds=[doc_id], type_label="entity")
        if not related_graph["data"][0]:
            result["message"] = "No related nodes"
            return result
        for record in related_graph["data"][0][doc_id]["nodes"]:
            data[record["id"]] = {}
            data[record["id"]]["name"], data[record["id"]]["Chinese_name"] = \
                [record["Entity_name"]], [record["Chinese_name"]]

        related_mongo = self.db.find_entity_list_from_doc(doc_id)
        for rec in related_mongo:
            if rec["id"] in data and rec["name"] not in data[rec["id"]]["name"]:
                data[rec["id"]]["name"].append(rec["name"])
            elif rec["id"] not in data:
                data[rec["id"]] = {}
                data[rec["id"]]["name"], data[rec["id"]]["Chinese_name"] = \
                    [rec["name"]], []
        result["data"] = data
        return result

    def get_entity(self, ids: list):
        result = {"code": 0}
        _keys = {}
        data = self.db.find_entity_list_detail_by_doc_id(ids)
        for con in data:
            if con["_id"] not in _keys:
                _keys[con["_id"]] = {}
            for val in con["entity_list"]:
                if val["id"] not in _keys[con["_id"]]:
                    _keys[con["_id"]][val["id"]] =[]
                    _keys[con["_id"]][val["id"]].append(val["name"])
                else:
                    _keys[con["_id"]][val["id"]].append(val["name"])

        result["data"] = _keys
        return result

    def doc_sentiment_time(self, idList: list, Time: list):
        # 分组时间为天
        pass_time = {}
        for _time in Time:
            timeArray = time.localtime(int(_time))
            str_today_time = time.strftime("%Y-%m-%d", timeArray)
            today_time = list(self.m_tool.get_timestamp(int(_time)))
            pass_time[str_today_time] = today_time
        from_times_str = list(pass_time.keys())
        from_times_str.sort()
        all_data = self.math.filling_time_count(from_times_str)["data"]["time"]

        result = {"code": 0,
                  "data": {
                      "Positive": [0 for t in all_data],
                      "Neutral": [0 for t in all_data],
                      "Negative": [0 for t in all_data]
                  }}

        data = self.db.find_sentiment_from_doc(idList)
        # 获取每天的倾向性
        for con in data:
            timeArray = time.localtime(int(con["publish_time"]))
            con_today_time = time.strftime("%Y-%m-%d", timeArray)
            if con["sentiment"] == "Positive":
                result["data"]["Positive"][all_data.index(con_today_time)] += 1
            elif con["sentiment"] == "Neutral":
                result["data"]["Neutral"][all_data.index(con_today_time)] += 1
            elif con["sentiment"] == "Negative":
                result["data"]["Negative"][all_data.index(con_today_time)] += 1
        for pos in range(len(result["data"]["Negative"])):
            # if result["data"]["Negative"][pos] and result["data"]["Negative"][pos] > 0:
            if result["data"]["Negative"][pos]:
                result["data"]["Negative"][pos] = 0 - result["data"]["Negative"][pos]
        return result

    def doc_sentiment(self, idList: list):
        result = {"code": 0,
                  "data": {
                      "Positive": [0],
                      "Neutral": [0],
                      "Negative": [0],
                      "posIds": [],
                      "neuIds": [],
                      "negIds": []
                  }}
        sentiment, _id = document_schema.get("sentiment"), document_schema.get("_id")
        data = self.db.find_sentiment_from_doc(idList)

        count = 0
        for con in data:
            if con[sentiment] == "Positive":
                count += 1
                result["data"]["Positive"][0] += 1
                result["data"]["posIds"].append(con[_id])
            elif con[sentiment] == "Neutral":
                count += 1
                result["data"]["Neutral"][0] += 1
                result["data"]["neuIds"].append(con[_id])
            elif con[sentiment] == "Negative":
                count += 1
                result["data"]["Negative"][0] += 1
                result["data"]["negIds"].append(con[_id])

        for value in list(result["data"].values())[0:3]:
            value[0:0] = [round((value[0]/count) * 100, 2) if value[0] != 0 else 0]

        return result

    def doc_sentiment_by_topic(self, idList: list, ids: list, names: list):
        result = {
            "code": 0,
            "data": []
        }
        if not ids:
            return self.doc_sentiment(idList[0])
        else:
            for _each in range(len(idList)):
                data = self.doc_sentiment(idList[_each])["data"]
                data["name"] = names[_each]
                data["id"] = ids[_each]
                result["data"].append(data)

            return result
