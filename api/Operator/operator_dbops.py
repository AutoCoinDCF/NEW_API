import pymongo

import api.configs.dynamic_config as dy_config
from api.log.QBLog import QBLog
from api.Mongo.abc_dbops import AbstractDbOps


class MongoDbOps(AbstractDbOps):

    def __init__(self, host: str = '10.60.1.140', port: int = 6080,
                 usr: str = "root", pwd: str = "111111"):
        self.config = MongoDbConf(host, port, usr, pwd)
        mongo_ins = MongoDbIns(self.config)
        self.db = mongo_ins.client

        # 当前所用库
        self.dbname = self.db[self.config.dbname]

        # 实体游标
        self.entity = self.db[self.config.dbname][self.config.entity]

        # 事件游标
        self.events_gtd = self.db[self.config.dbname][self.config.events_gtd]
        self.events_labeled = self.db[self.config.dbname][self.config.events_labeled]
        self.events_taiwan = self.db[self.config.dbname][self.config.events_taiwan]

        # 文档游标
        self.documents_darpa = self.db[self.config.dbname][self.config.documents_darpa]
        self.documents_gtd = self.db[self.config.dbname][self.config.documents_gtd]
        self.documents_labeled = self.db[self.config.dbname][self.config.documents_labeled]
        self.documents_humanrights = self.db[self.config.dbname][self.config.documents_humanrights]
        self.documents_taiwan = self.db[self.config.dbname][self.config.documents_taiwan]

        self.logger = QBLog({'LOG_LEVEL': dy_config.LOG_LEVEL}, self.__class__.__name__)

    # ------------------------------------------------------------------------------------start>>>
    def document_group_search(self, idlist: list, func):
        '''分组doc_id，并在对应表中查询请求'''
        darpa, gtd, labeled, humanrights, taiwan = [], [], [], [], []
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

        for group_table in [darpa, gtd, labeled, humanrights, taiwan]:
            if group_table:
                if group_table == darpa:
                    result += func(self.documents_darpa, darpa)
                elif group_table == gtd:
                    result += func(self.documents_gtd, gtd)
                elif group_table == labeled:
                    result += func(self.documents_labeled, labeled)
                elif group_table == humanrights:
                    result += func(self.documents_humanrights, humanrights)
                elif group_table == taiwan:
                    result += func(self.documents_taiwan, taiwan)
        return result

    def event_group_search(self, idlist, func):
        '''分组event_id，并在对应表中查询请求'''
        gtd, labeled, taiwan = [], [], []
        result = {} if dict else []
        for _id in idlist:
            label_id = _id[:8]
            if label_id == "ca8fcda5":
                gtd.append(_id)
            elif label_id == "d713ba29":
                labeled.append(_id)
            elif label_id == "37836765":
                taiwan.append(_id)

        for group_table in [gtd, labeled, taiwan]:
            if group_table:
                if group_table == gtd:
                    result += func(self.events_gtd, gtd)
                elif group_table == labeled:
                    result += func(self.events_labeled, labeled)
                elif group_table == taiwan:
                    result += func(self.events_taiwan, taiwan)

        return result

    def find_event_detail_by_id(self, idlist):
        def func(table: str, ids: list):
            res = table.find({"_id": {"$in": ids}})
            return list(res)

        return self.event_group_search(idlist, func)



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
        self.entity = "entity"

        self.events_gtd = "events_gtd"
        self.events_labeled = "events_labeled"
        self.events_taiwan = "events_taiwan"

        self.documents_darpa = "documents_darpa1"
        self.documents_gtd = "documents_gtd1"
        self.documents_labeled = "documents_labeled1"
        self.documents_humanrights = "documents_humanrights1"
        self.documents_taiwan = "documents_taiwan1"
