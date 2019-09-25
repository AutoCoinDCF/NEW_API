'''MongoDbOps: Mongodb操作接口类

@author: shishidun@ict.ac.cn
@last_modified: 2018.06.20
'''
import pymongo, multiprocessing

import api.configs.dynamic_config as dy_config

from api.log.QBLog import QBLog
from .abc_dbops import AbstractDbOps
from api.Mongo import config_data_purpose_field as CF
from api.Mongo.schema import entity_schema, event_schema, document_schema


# from api.web.utils import func_line_time


class MongoDbOps(AbstractDbOps):

    def __init__(self, host: str = '10.60.1.140', port: int = 6080,
                 usr: str = "root", pwd: str = "111111"):
        self.config = MongoDbConf(host, port, usr, pwd)
        mongo_ins = MongoDbIns(self.config)
        self.db = mongo_ins.client

        # 当前所用库
        self.dbname = self.db[self.config.dbname]
        self.SG_dbname = self.db[self.config.SG_dbname]

        # 实体游标
        self.entity = self.db[self.config.dbname][self.config.entity]
        self.entity_twitter = self.db[self.config.SG_dbname][self.config.entity_twitter]

        # 事件游标
        self.event = self.db[self.config.dbname][self.config.event]
        self.events_gtd = self.db[self.config.dbname][self.config.events_gtd]
        self.events_labeled = self.db[self.config.dbname][self.config.events_labeled]
        self.events_taiwan = self.db[self.config.dbname][self.config.events_taiwan]
        self.events_sg = self.db[self.config.dbname][self.config.events_sg]
        self.events_twitter = self.db[self.config.SG_dbname][self.config.events_twitter]

        # 文档游标
        self.documents_darpa = self.db[self.config.dbname][self.config.documents_darpa]
        self.documents_gtd = self.db[self.config.dbname][self.config.documents_gtd]
        self.documents_labeled = self.db[self.config.dbname][self.config.documents_labeled]
        self.documents_humanrights = self.db[self.config.dbname][self.config.documents_humanrights]
        self.documents_taiwan = self.db[self.config.dbname][self.config.documents_taiwan]
        self.documents_twitter = self.db[self.config.SG_dbname][self.config.documents_twitter]
        self.documents_sg = self.db[self.config.dbname][self.config.documents_sg]
        self.task_record = self.db[self.config.dbname][self.config.task_record]
        self.documents_task = self.db[self.config.dbname][self.config.documents_task]
        self.doc_search = self.db[self.config.dbname][self.config.doc_search]

        self.logger = QBLog({'LOG_LEVEL': dy_config.LOG_LEVEL}, self.__class__.__name__)

    # ------------------------------------------------------------------------------------start>>>
    def entity_group_search(self, idlist, func, dict=False):
        '''分组entity_id，并在对应表中查询请求'''
        entity, entity_twitter = [], []
        result = {} if dict else []
        for _id in idlist:
            # 推特中entity_list的实体id为int类型，待修改
            if isinstance(_id, int):
                _id = str(_id)
            if not _id.startswith("T"):
                entity.append(_id)
            else:
                # entity_twitter.append(_id.replace("T", ""))
                entity_twitter.append(_id)

        for group_table in [entity, entity_twitter]:
            if group_table:
                if group_table == entity:
                    if dict:
                        result.update(func(self.entity, entity))
                    else:
                        result += func(self.entity, entity)
                elif group_table == entity_twitter:
                    if dict:
                        result.update(func(self.entity_twitter, entity_twitter))
                    else:
                        result += func(self.entity_twitter, entity_twitter)

        return result

    def event_group_search(self, idlist, func, dict=False):
        '''分组event_id，并在对应表中查询请求'''
        gtd, labeled, taiwan, twitter, sg = [], [], [], [], []
        result = {} if dict else []
        for _id in idlist:
            label_id = _id[:8]
            if label_id == "ca8fcda5":
                gtd.append(_id)
            elif label_id == "d713ba29":
                labeled.append(_id)
            elif label_id == "37836765":
                taiwan.append(_id)
            elif label_id == "7e3bb7cb":
                sg.append(_id)
            elif label_id == "13c12502":
                twitter.append(_id)

        for group_table in [gtd, labeled, taiwan, twitter, sg]:
            if group_table:
                if group_table == gtd:
                    if dict:
                        result.update(func(self.events_gtd, gtd))
                    else:
                        result += func(self.events_gtd, gtd)
                elif group_table == labeled:
                    if dict:
                        result.update(func(self.events_labeled, labeled))
                    else:
                        result += func(self.events_labeled, labeled)
                elif group_table == taiwan:
                    if dict:
                        result.update(func(self.events_taiwan, taiwan))
                    else:
                        result += func(self.events_taiwan, taiwan)
                elif group_table == sg:
                    if dict:
                        result.update(func(self.events_sg, sg))
                    else:
                        result += func(self.events_sg, sg)
                elif group_table == twitter:
                    if dict:
                        result.update(func(self.events_twitter, twitter))
                    else:
                        result += func(self.events_twitter, twitter)

        return result

    def document_group_search(self, idlist: list, func, dict=False):
        '''分组doc_id，并在对应表中查询请求'''
        darpa, gtd, labeled, humanrights, taiwan, sg, task_list, twitter = [], [], [], [], [], [], [], []
        result = {} if dict else []
        for _id in idlist:
            label_id = _id[:8]
            if label_id == "e7764954":
                darpa.append(_id)
            elif label_id == "ca8fcda5":
                gtd.append(_id)
            elif label_id == "d713ba29":
                labeled.append(_id)
            elif label_id == "def57351":
                humanrights.append(_id)
            elif label_id == "37836765":
                taiwan.append(_id)
            elif label_id == "7e3bb7cb":
                sg.append(_id)
            elif label_id == "13c12502":
                twitter.append(_id)
            else:
                task_list.append(_id)

        for group_table in [darpa, gtd, labeled, humanrights, taiwan, sg, task_list, twitter]:
            if group_table:
                if group_table == darpa:
                    if dict:
                        result.update(func(self.documents_darpa, darpa))
                    else:
                        result += func(self.documents_darpa, darpa)
                elif group_table == gtd:
                    if dict:
                        result.update(func(self.documents_gtd, gtd))
                    else:
                        result += func(self.documents_gtd, gtd)
                elif group_table == labeled:
                    if dict:
                        result.update(func(self.documents_labeled, labeled))
                    else:
                        result += func(self.documents_labeled, labeled)
                elif group_table == humanrights:
                    if dict:
                        result.update(func(self.documents_humanrights, humanrights))
                    else:
                        result += func(self.documents_humanrights, humanrights)
                elif group_table == taiwan:
                    if dict:
                        result.update(func(self.documents_taiwan, taiwan))
                    else:
                        result += func(self.documents_taiwan, taiwan)
                elif group_table == twitter:
                    if dict:
                        result.update(func(self.documents_twitter, twitter))
                    else:
                        result += func(self.documents_twitter, twitter)
                elif group_table == sg:
                    if dict:
                        result.update(func(self.documents_sg, sg))
                    else:
                        result += func(self.documents_sg, sg)
                elif group_table == task_list:
                    if dict:
                        result.update(func(self.documents_task, task_list))
                    else:
                        result += func(self.documents_task, task_list)
        return result

    def entity_label_search(self, Attr, _skip, pageSize, func):
        """通过字符串匹配实体节点"""
        result = []

        for _cursor in [self.entity, self.entity_twitter]:
            result.extend(func(_cursor, Attr, _skip, pageSize))

        return result

    def event_label_search(self, Attr, _skip, pageSize, func):
        """通过字符串匹配事件节点"""
        result = []

        for _cursor in [self.events_gtd, self.events_labeled, self.events_taiwan, self.events_sg, self.events_twitter]:
            result.extend(func(_cursor, Attr, _skip, pageSize))

        return result

    def document_label_search(self, Attr, _skip, pageSize, func):
        """通过字符串匹配文档节点"""
        result = []

        for _cursor in [self.documents_darpa, self.documents_gtd, self.documents_labeled, \
                        self.documents_humanrights, self.documents_taiwan, self.documents_sg, self.documents_twitter]:
            result.extend(func(_cursor, Attr, _skip, pageSize))

        return result

    def document__search(self, time, ids, func):
        """通过事件匹配文档节点"""
        result = []

        for _cursor in [self.documents_darpa, self.documents_gtd, self.documents_labeled, \
                        self.documents_humanrights, self.documents_taiwan, self.documents_sg, self.documents_twitter]:
            result.extend(func(_cursor, time, ids))

        return result

    # ------------------------------------------------------------------------------------end>>>

    def find_entity_doc_id_by_event(self, id):
        '''通过event的idlist字段拓展entity_list和doc_id
        '''

        def func(table: str, ids: list):
            res = table.find_one({event_schema.get("_id"): ids[0]}, {
                event_schema.get("_id"): 1, event_schema.get("doc_id"): 1,
                event_schema.get("meta_type"): 1, event_schema.get("entity_list"): 1})
            return [res]

        return self.event_group_search([id], func)

    def find_entity_id_by_document(self, id):
        '''通过docid的idlist字段拓展出entity_list字段
        '''

        def func(table: str, ids: list):
            res = table.find_one({document_schema.get("_id"): ids[0]},
                                 {document_schema.get("_id"): 1, document_schema.get("meta_type"): 1,
                                  document_schema.get("entity_list"): 1})
            return [res]

        return self.document_group_search([id], func)

    def find_event_by_document(self, id):
        '''
        通过docid拓展出相关的事件的id
        '''

        def func(table: str, ids: list):
            res = table.find_one({event_schema.get("doc_id"): ids[0]}, {event_schema.get("_id"): 1})
            return [res]

        return self.event_group_search([id], func)

    def find_subtype_by_entity(self, idlist):
        '''
        通过entity_id拓展出以Entity_type进行分类的实体详情
        '''
        def func(table: str, ids: list):
            res = table.aggregate([
                {"$match": {entity_schema.get("Entity_id"): {"$in": ids}}},
                {"$group": {
                    "_id": "$%s" % entity_schema.get("Entity_type"),
                    "count": {"$sum": 1},
                    "idlist": {"$addToSet": '$%s' % entity_schema.get("Entity_id")}
                }}
            ])
            return [s for s in res if s[entity_schema.get("_id")]]
        return self.entity_group_search(idlist, func)

    def find_subtype_by_event(self, idlist):
        '''
        通过event_id拓展出以event_subtype进行分类的事件详情
        '''

        def func(table: str, ids: list):
            res = table.aggregate([
                {"$match": {event_schema.get("_id"): {"$in": ids}}},
                {"$group": {
                    "_id": "$%s" % event_schema.get("event_subtype"),
                    "count": {"$sum": 1},
                    "idlist": {"$addToSet": '$%s' % event_schema.get("_id")}
                }}
            ])
            return [s for s in res if s[event_schema.get("_id")]]

        return self.event_group_search(idlist, func)

    def find_subtype_by_document(self, idlist):
        '''
        通过doc_id拓展出以channel进行分类的文档详情
        '''

        def func(table: str, ids: list):
            res = table.aggregate([
                {"$match": {document_schema.get("_id"): {"$in": ids}}},
                {"$group": {
                    "_id": "$%s" % document_schema.get("channel"),
                    "count": {"$sum": 1},
                    "idlist": {"$addToSet": '$%s' % document_schema.get("_id")}
                }}
            ])
            return [s for s in res if s[document_schema.get("_id")]]

        return self.document_group_search(idlist, func)

    def find_subentity_by_entity_sub_type(self, idlist, sub_types):
        '''
         通过entity_id拓展出以二级属性sub_type进行分类的实体详情
        '''
        def func(table: str, ids: list):
            Entity_id = entity_schema.get("Entity_id")
            sub_types.append(Entity_id)
            res = table.find({Entity_id: {"$in": ids}}, {_r: 1 for _r in sub_types})
            return list(res)
        return self.entity_group_search(idlist, func)

    def find_subdoc_by_doc_sub_type(self, idlist, sub_types):
        '''
         通过document_id拓展出以二级属性sub_type进行分类的文档详情
         '''

        def func(table: str, ids: list):
            res = table.find({document_schema.get("_id"): {"$in": ids}}, {_r: 1 for _r in sub_types})
            return list(res)

        return self.document_group_search(idlist, func)

    def find_entity_list_by_event_id(self, idlist):
        '''
        通过event_id查找出对应的entity_list中的entity并和并在一个list
        '''
        _dict = {}

        def func(table: str, ids: list):
            _id, entity_list = event_schema.get("_id"), event_schema.get("entity_list")
            res = table.find({_id: {"$in": ids}},
                             {_id: 1, entity_list: 1})
            return {record[_id]: list(set([_id["id"] for _id in record[entity_list]])) for record in [s for s in res]}

        return self.event_group_search(idlist, func, dict=True)

    def find_entity_list_by_doc_id(self, idlist):
        '''
        通过doc_id查找出对应的entity_list中的entity并和并在一个list
        '''
        _dict = {}

        def func(table: str, ids: list):
            _id, entity_list = document_schema.get("_id"), document_schema.get("entity_list")
            res = table.find({_id: {"$in": ids}},
                             {_id: 1, entity_list: 1})
            return {record[_id]: list(set([_id["id"] for _id in record[entity_list]])) for record in [s for s in res]}

        return self.document_group_search(idlist, func, dict=True)

    def find_entity_list_detail_by_doc_id(self, idlist):
        '''
        通过doc_id查找出对应的entity_list及详细信息
        '''
        _dict = {}

        def func(table: str, ids: list):
            _id, entity_list = document_schema.get("_id"), document_schema.get("entity_list")
            res = table.find({_id: {"$in": ids}},
                             {_id: 1, entity_list: 1})
            return list(res)
        return self.document_group_search(idlist, func)

    def find_entity_info_by_entity_list(self, idlist):
        '''
        通过entity_list查找出entity的简要信息，并以二级属性为键分组返回
        '''
        def func(table: str, ids: list):
            _id, entity_type, entity_name, chinese_name, entity_id = \
                entity_schema.get("_id"), entity_schema.get("Entity_type"), \
                entity_schema.get("Entity_name"), entity_schema.get("Chinese_name"), \
                entity_schema.get("Entity_id")
            res = table.find(
                {entity_id: {"$in": ids}},
                {_id: 0, entity_id: 1, entity_type: 1, entity_name: 1, chinese_name: 1}
            )
            __di = {}
            for record in list(res):
                type = record[entity_type]
                del record[entity_type]
                if type in __di:
                    __di[type].append(record)
                else:
                    __di[type] = [record]
            return __di
        return self.entity_group_search(idlist, func, dict=True)

    def find_time_and_id_by_event_id(self, idlist):
        def func(table: str, ids: list):
            _id, time = event_schema.get("_id"), event_schema.get("publish_time")
            res = table.find(
                {_id: {"$in": ids}},
                {_id: 1, time: 1}
            )
            return list(res)

        return self.event_group_search(idlist, func)

    def find_time_and_id_by_document_id(self, idlist):
        def func(table: str, ids: list):
            _id, time = document_schema.get("_id"), document_schema.get("publish_time")
            res = table.find(
                {_id: {"$in": ids}},
                {_id: 1, time: 1}
            )
            return list(res)

        return self.document_group_search(idlist, func)

    def find_doc_detail_by_id(self, idlist):
        def func(table: str, ids: list):
            _id, title, description, i_sn, time, _from = \
                document_schema.get("_id"), document_schema.get("title"), \
                document_schema.get("content"), document_schema.get("channel"), \
                document_schema.get("publish_time"), document_schema.get("site_name")

            res = table.find(
                {_id: {"$in": ids}},
                {_id: 1, title: 1, description: 1,
                 i_sn: 1, time: 1, _from: 1
                 }
            )
            return list(res)

        return self.document_group_search(idlist, func)

    def find_doc_translate_by_id(self, doc_id):
        def func(table: str, ids: list):
            _id, title, text, time = \
                document_schema.get("_id"), document_schema.get("title"), \
                document_schema.get("content"), document_schema.get("publish_time")
            res = table.find_one(
                {_id: ids[0]},
                {_id: 1, title: 1, text: 1, time: 1}
            )
            return [res]

        return self.document_group_search([doc_id], func)

    def find_event_detail_by_id(self, idlist):
        def func(table: str, ids: list):
            res = table.find({event_schema.get("_id"): {"$in": ids}})
            return list(res)

        return self.event_group_search(idlist, func)

    def find_entity_detail_by_entity_id(self, idlist):
        def func(table: str, ids: list):
            res = table.find({entity_schema.get("Entity_id"): {"$in": ids}})
            return list(res)
        return self.entity_group_search(idlist, func)

    def find_nodes_by_keyword(self, type, Attr, page, pageSize, max, entity_subtype):
        last_record = max - page * pageSize
        _skip = pageSize * (page - 1)
        filter_field = [
            entity_schema.get("Entity_id"), entity_schema.get("Entity_name"), \
            entity_schema.get("Chinese_name"), entity_schema.get("Entity_type"), \
            entity_schema.get("English_text"), entity_schema.get("Chinese_text")
        ]
        if last_record < 0 and abs(last_record) > pageSize:
            return []
        elif last_record < 0 and abs(last_record) < pageSize:
            pageSize = abs(last_record)
        if type in entity_subtype:
            # 当_filter为空时，会显示全部，此时加上_filter["_id"] = 0会除了_id其他全部显示，当前geographic_entity是这种情况
            _filter = {f: 1 for f in list(CF.all[type].values())}
            def func(table: str, Attr: list, _skip: int, pageSize: int):
                _dict = {}
                _filter["_id"], _filter["Entity_id"] = 0, 1
                if "id" in _filter:
                    del _filter["id"]
                Attr[entity_schema.get("Entity_type")] = [type]
                for condition in Attr:
                    _dict[" ".join(condition.split("_")) if condition not in filter_field else condition] = {
                        "$in": Attr[condition]}
                res = table.find(_dict, _filter).skip(_skip).limit(pageSize)
                del Attr[entity_schema.get("Entity_type")]
                return list(res)
            return self.entity_label_search(Attr, _skip, pageSize, func)

        elif type == "event":
            _filter = {f: 1 for f in list(CF.all[type].values())}

            def func(table: str, Attr: list, _skip: int, pageSize: int):
                _dict = {}
                for condition in Attr:
                    _dict[condition] = {"$in": Attr[condition]}
                res = table.find(_dict, _filter).skip(_skip).limit(pageSize)
                return list(res)

            return self.event_label_search(Attr, _skip, pageSize, func)

        elif type == "document":
            _filter = {f: 1 for f in list(CF.all[type].values())}

            def func(table: str, Attr: list, _skip: int, pageSize: int):
                _dict = {}
                for condition in Attr:
                    _dict[condition] = {"$in": Attr[condition]}
                res = table.find(_dict, _filter).skip(_skip).limit(pageSize)
                return list(res)

            return self.document_label_search(Attr, _skip, pageSize, func)

        elif type == "all":
            res = []
            i = 0
            for label in ["human", "organization", "administrative", "weapon", "geographic_entity", "event",
                          "document"]:
                i += 1
                _sql = self.find_nodes_by_keyword(label, Attr, page, pageSize, max, entity_subtype)
                res.extend(_sql)
            return res

        else:
            self.logger.error(f'Type tag error, value is {type}')

    def find_sentiment_from_doc_and_time(self, today_time: list, ids: list,):
        """通过doc_id查询情感分类"""
        id, publish_time, sentiment= document_schema.get("_id"), \
                                     document_schema.get("publish_time"),\
                                     document_schema.get("sentiment")

        def func(table: str, Time: list, Ids: list):
            res=table.find({"$and": [{id: {"$in": Ids}}, {publish_time: {"$gte": Time[0]}}, \
                                     {publish_time: {"$lte": Time[1]}}]},
                                    {id: 0, sentiment: 1})
            return list(res)

        return self.document__search(today_time, ids, func)

    def find_sentiment_from_doc(self, idlist: list):
        """通过doc_id查询情感分类"""

        id, sentiment, publish_time = document_schema.get("_id"), document_schema.get("sentiment"),\
                                        document_schema.get("publish_time")
        def func(table: str, ids: list):
            res = table.find(
                {id: {"$in": ids}},
                {sentiment: 1, publish_time: 1}
            )
            return list(res)

        return self.document_group_search(idlist, func)

    def find_entity_name_by_entity_id(self, entity_id):
        """通过实体id查询其中文名"""
        Entity_id, Entity_name, Chinese_name = entity_schema.get("Entity_id"), \
                                               entity_schema.get("Entity_name"), \
                                               entity_schema.get("Chinese_name")
        def func(table: str, ids: list):
            res = table.find_one({Entity_id: ids[0]}, {"_id": 0, Entity_id: 1, Entity_name: 1, Chinese_name: 1})
            return res
        return self.entity_group_search([entity_id], func, dict=True)

    # def find_entity_type_by_id(self, entity_id):
    #     # 通过实体id去查找实体类型
    #     Entity_id, Entity_type = entity_schema.get("Entity_id"), entity_schema.get("Entity_type")
    #     def func(table: str, ids: list):
    #         print('--------------{}---------------'.format(ids[0]))
    #         res = table.find_one({Entity_id: ids[0]}, {"_id": 0, Entity_type: 1})
    #         print('-------------result--------------')
    #         print(res)
    #         if res:
    #             return res[Entity_type]
    #         else:
    #             return "default"
    #     return self.entity_group_search([entity_id], func)

    ###########################################new_doc########################################
    def find_doc_type_by_time(self, ids):
        '''
        查找文档id的词性
        '''
        id, publish_time = document_schema.get("_id"), document_schema.get("publish_time")

        def func(table: str, Ids: list):
            res = table.find({id: {"$in": Ids}}, {publish_time: 1})
            return list(res)

        return self.document_group_search(ids, func)

    def find_doc_by_time(self, today_time, ids):
        '''
        查找文档id的词性
        '''
        id, publish_time = document_schema.get("_id"), document_schema.get("publish_time")

        def func(table: str, Time: list, Ids: list):
            res = table.find({"$and": [{id: {"$in": Ids}}, {publish_time: {"$gte": Time[0]}},\
                                       {publish_time: {"$lte": Time[1]}}]}, {id: 1})
            return list(res)

        return self.document__search(today_time, ids, func)

    def find_word_by_document(self, idlist):
        '''
        查找文档id的词性
        '''
        id, keywords, ner, pos = document_schema.get("_id"), document_schema.get("keywords"), \
                                 document_schema.get("ner"), document_schema.get("pos")

        def func(table: str, ids: list):
            res = table.find({id: {"$in": ids}},
                             {id: 0, keywords: 1, ner: 1, pos: 1})
            return list(res)

        return self.document_group_search(idlist, func)

    def find_word_by_document_from_time(self, idlist):
        '''
        查找文档id的词性
        '''
        id, keywords, ner, pos, publish_time = document_schema.get("_id"), document_schema.get("keywords"), \
                                               document_schema.get("ner"), document_schema.get("pos"), \
                                               document_schema.get("publish_time")

        def func(table: str, ids: list):
            res = table.find({id: {"$in": ids}},
                             {id: 0, keywords: 1, ner: 1, pos: 1, publish_time: 1})
            return list(res)

        return self.document_group_search(idlist, func)

    def find_word_by_document_time(self, idlist):
        '''
        查找文档id的词性
        '''
        id, keywords, ner, pos,  publish_time = document_schema.get("_id"), document_schema.get("keywords"), \
                                 document_schema.get("ner"), document_schema.get("pos"), document_schema.get("publish_time")

        def func(table: str, ids: list):
            res = table.find({id: {"$in": ids}},
                             {id: 0, keywords: 1, ner: 1, pos: 1, publish_time: 1})
            return list(res)

        return self.document_group_search(idlist, func)

    def find_doc_by_word_and_type(self, idlist, word, speech):
        '''
        查找文档id的词性
        '''
        id, keywords, ner, pos = document_schema.get("_id"), document_schema.get("keywords"), \
                                 document_schema.get("ner"), document_schema.get("pos")

        def func(table: str, ids: list):
            if speech == "keywords":
                res = table.find({
                    id: {"$in": ids},
                    keywords: {"$all": word},
                }, {id: 1})
                return list(res)
            else:
                res = table.find({id: {"$in": ids}},
                                 {id: 1, keywords: 1, ner: 1, pos: 1})
                return list(res)

        return self.document_group_search(idlist, func)

    def find_entity_list_from_doc(self, doc_id):
        def func(table: str, ids: list):
            _id, entity_list = document_schema.get("_id"), document_schema.get("entity_list")
            res = table.find_one(
                {_id: ids[0]},
                {_id: 0, entity_list: 1}
            )
            return res["entity_list"]

        return self.document_group_search([doc_id], func)

    ############################################fake#####################################
    def data_search_test(self, id):
        _filter = {f: 1 for f in list(CF.all["document"].values())}
        res = self.documents_labeled.find_one({"_id": id}, _filter)
        return res

    # 将文章解析到mongo
    def creat_and_index_to_mongo(self, body: list):
        res = self.documents_task.insert(body)
        return res

    # 创建并添加关于任务状态的数据库表
    def insert_task_state(self, table_id: str, body: list):
        res = self.db[self.config.dbname][table_id].insert(body)
        return res

    # 更改task任务的状态
    def update_task_state_task(self, table_id: str, uu_id: str, type_key: str, type_val: str):
        res = self.db[self.config.dbname][table_id].update({"task_id": uu_id}, {"$set": {type_key: type_val}})
        return res

    def update_task_state(self, table_id: str, uu_id: str, content_id: str, type_key: str, type_val: str):
        res = self.db[self.config.dbname][table_id].update({"task_id": uu_id, "content.content_id": content_id},
                                                           {"$set": {type_key: type_val}})
        return res

    def update_task_state_to_do(self, table_id: str, uu_id: str, end: str):
        content = self.db[self.config.dbname][table_id].find_one({"task_id": uu_id}, {"_id": 0, "content": 1})["content"]
        for _rec in content:
            _rec["content_status"] = end
        res = self.db[self.config.dbname][table_id].update({"task_id": uu_id}, {"$set": {"content": content}})
        return res

    def search_task(self, status: str, source: str, page: int, pageSize: int):
        _filter = {"_id": 0, "set_id": 0}
        if status != "全部状态" and source != "全部来源":
            if page == 0 and pageSize == 0:
                res = self.task_record.find({"status": status, "source": source}, _filter)
            else:
                res = self.task_record.find({"status": status, "source": source}, _filter).skip(pageSize*(page-1)).limit(pageSize)
        elif status == "全部状态" and source != "全部来源":
            if page == 0 and pageSize == 0:
                res = self.task_record.find({"source": source}, _filter)
            else:
                res = self.task_record.find({"source": source}, _filter).skip(pageSize*(page-1)).limit(pageSize)
        elif status != "全部状态" and source == "全部来源":
            if page == 0 and pageSize == 0:
                res = self.task_record.find({"status": status}, _filter)
            else:
                res = self.task_record.find({"status": status}, _filter).skip(pageSize*(page-1)).limit(pageSize)
        else:
            if page == 0 and pageSize == 0:
                res = self.task_record.find({}, _filter)
            else:
                res = self.task_record.find({}, _filter).skip(pageSize*(page-1)).limit(pageSize)
        return list(res)

    def  drop_task_table(self, task_id):
        self.documents_task.remove({"task_id": task_id})

    def drop_task_record_table(self, task_id):
        self.task_record.remove({"task_id": task_id})

    def drop_task_set_id_table(self, task_id):
        res = self.task_record.find_one({"task_id": task_id}, {"_id": 0, "set_id": 1})
        return res["set_id"]

    # 将文章解析到mongo
    def search_index_to_mongo(self, body: list):
        res = self.doc_search.insert(body)
        return res

    # 根据搜索id和文档id，查询出匹配出的文档的详情
    def find_doc_from_doc_search(self, search_id: str, ids: list):
        res = self.doc_search.find({"search_id": search_id, "_id": {"$in": ids}})
        return list(res)

    def find_entity_list_by_doc_id_from_docSearch(self, idlist):
        '''
        通过doc_id查找出对应的entity_list中的entity并和并在一个list
        '''
        _dict = {}

        _id, entity_list = document_schema.get("_id"), document_schema.get("entity_list")

        res = self.doc_search.find({_id: {"$in": idlist}},
                         {_id: 1, entity_list: 1})
        return {record[_id]: list(set([_id["id"] for _id in record[entity_list]])) for record in [s for s in res]}

    def find_subdoc_by_doc_sub_type_from_docSearch(self, idlist, sub_types):
        '''
         通过document_id拓展出以二级属性sub_type进行分类的文档详情
         '''
        res = self.doc_search.find({document_schema.get("_id"): {"$in": idlist}}, {_r: 1 for _r in sub_types})
        return list(res)


class MongoDbIns(object):
    def __init__(self, config):
        self.host = config.host
        self.port = config.port
        self.usr = config.usr
        self.pwd = config.pwd
        self.client = pymongo.MongoClient(host=self.host, port=self.port)
        self.admin = self.client.admin
        self.admin.authenticate(self.usr, self.pwd)

    def __getitem__(self, item):
        return self.client[item]


class MongoDbConf(object):
    def __init__(self, host, port, usr, pwd):
        self.host = host
        self.port = port
        self.usr = usr
        self.pwd = pwd
        self.dbname = "QBData"
        self.SG_dbname = "SGData"

        self.entity = "entity"
        self.entity_twitter = "twitter_user"

        self.event = "events"
        self.events_gtd = "events_gtd"
        self.events_labeled = "events_labeled"
        self.events_taiwan = "events_taiwan"
        self.events_sg = "events_sg_4"
        self.events_twitter = "twitter_events"

        self.documents_task = "documents_task"
        self.task_record = "task_record"
        self.doc_search = "doc_search"
        self.documents_darpa = "documents_darpa1"
        self.documents_gtd = "documents_gtd1"
        self.documents_labeled = "documents_labeled1"
        self.documents_humanrights = "documents_humanrights1"
        self.documents_taiwan = "documents_taiwan1"
        self.documents_sg = "documents_sg_4"
        self.documents_twitter = "social_media"
