import time, pymongo, os, collections, json
from elasticsearch import Elasticsearch
from functools import reduce

import api.es.es_query as ES
import api.es.utility as TOOL
import api.es.config.config_statistics as STA
from api.es.es_base import ESClient
from api.GIS.GISApplication import GISApplication
from api.graph.application.graph_application import GraphApplication


# from api.web.utils import func_line_time


class esObj():

    def __init__(self, host: str = "10.60.1.145", port: str = "9200", timeout: int = 5000):
        """
        Create a instance to handle data
        :param host: es host
        :param port: es port
        :param timeout: es timeout
        """
        path = "/config/es.config"
        config_path = os.path.join(os.path.dirname(__file__) + path)
        self._config = {}
        with open(config_path, "r") as f:
            self._config = collections.OrderedDict(json.load(f))
        self.client = ESClient()
        self.Client = Elasticsearch(host=host, port=port, timeout=timeout)
        self.mapp = {}
        self.graph = GraphApplication()

    def fullTextSearch(self, query: str, page: int, timeStart: int, timeEnd: int, isSortByTime: str,
                       limit: bool, PageSize: int = 20):
        """
        find the docment which include the query

        :param query: string for search
        :param page: page number of resultset
        :param PageSize: the size of resultset
        :param timeStart: upper limit of resultset public time
        :param timeEnd: lower limit of resultset public time
        :param isSortByTime: if sort the resultset by time and how to sort (desc/asc/null)
        """
        if limit in ["all", "count"]:
            page = -1
        body = self.generateMatchPhraseDSL(self._config["param"]["es"]["doc"]["index"], query, page, PageSize,
                                           timeStart, timeEnd, isSortByTime)
        searchResult = self.Client.search(self._config["param"]["es"]["doc"]["index"], body=body)
        # res = self.resData(searchResult["hits"]["hits"], 35)
        res = self.resData(searchResult["hits"]["hits"], -1)
        if limit == "count":
            return {"code": 0, "count": len(res["data"])}
        return res

    def sectionSearch(self, query: str):
        body = self.generateMatchPhraseDSL("document_sg", query, highlight=1)
        searchResult = self.Client.search(index="document_sg", body=body)
        data = []
        searchResult = searchResult["hits"]["hits"]
        for item in searchResult:
            for sec in item["highlight"]["content.en"]:
                sec = sec.replace("<em>", "")
                data.append(sec)
        response = {}
        if (len(data) == 0):
            response["code"] = -1
        else:
            response["code"] = 0
            response["data"] = {}
            response["data"]["num"] = len(data)
            response["data"]["data"] = data
        return response

    def generateMatchPhraseDSL(self, index: str, query: str, page: int = -1, size: int = 0,
                               timeStart: int = -1, timeEnd: int = -1, isSortByTime: str = "",
                               highlight: int = -1):
        frm = (page - 1) * size
        if (page == -1):
            frm = 0
            size = 100000
        res = {
            "query": {
                "bool": {
                    "must": [],
                    "must_not": [],
                    "should": []
                }
            },
            "from": frm,
            "size": size,
            "sort": {}
        }
        # match_phrase
        match_phrase = {
            "match_phrase": {
                "content.en": query
            }
        }
        res["query"]["bool"]["must"].append(match_phrase)
        # timerange
        if (timeStart != -1 & timeEnd != -1):
            timerange = {
                "range": {
                    "publish_time": {
                        "gt": -1,
                        "lt": -1
                    }
                }
            }
            timerange["range"]["publish_time"]["gt"] = timeStart
            timerange["range"]["publish_time"]["lt"] = timeEnd
            res["query"]["bool"]["must"].append(timerange)
        # sort
        if (isSortByTime != ""):
            res["sort"]["publish_time"] = isSortByTime
        if (highlight == 1):
            hl = {
                "pre_tags": [
                    "<em>"
                ],
                "post_tags": [
                    "<em>"
                ],
                "fields": {"content.en": {}}
            }
            res["highlight"] = hl
        return res

    def resData(self, rawData: dict, pos: int):
        data = []
        for i in rawData:
            data.append(self.getInfo(i, pos))
        docDataList = {}
        docDataList["code"] = (0 if len(data) else 1)
        docDataList["data"] = data
        return docDataList

    def getInfo(self, data: dict, pos: int = -1, detail=False):
        add = {}
        nel = data["_source"]["channel"]
        add["id"] = data["_id"]
        add["title"] = data["_source"]["title"]["en"]
        add["description"] = data["_source"]["content"]["en"]
        add["channel"] = STA.channel[nel] if nel in STA.channel else nel
        if (data["_source"]["publish_time"] == -1):
            add["publish_time"] = ""
        else:
            if data["_source"]["publish_time"] == "":
                data["_source"]["publish_time"] = -1
            _time = time.localtime(data["_source"]["publish_time"])
            end_time = time.strftime("%Y-%m-%d", _time)
            add["publish_time"] = end_time
            # add["time"] = datetime.datetime.utcfromtimestamp(data["_source"]["publish_time"]).strftime("%Y-%m-%d %H:%M:%S")
        add["site_name"] = data["_source"]["site_name"]
        if (pos != -1):
            add["description"] = add["description"][:pos]
        return add

    # @func_line_time
    def fuzzyMatch(self, query: str, size: int = 100):
        ids = []
        index = self._config["param"]["es"]["entity"]["index"]
        doc_type = self._config["param"]["es"]["entity"]["doc_type"]
        # find
        # test
        # ga = GraphApplication()
        # print("委内瑞拉航空的出入度: ",ga.entity_num(entity_id="Q1531524"))
        prewildcardquery = query + "*"
        middlewildcardquery = "*" + query + "*"
        wildcardsize = 800
        if not TOOL.is_ascii(query):
            # deny term query
            ids.extend(self.client.term(index, "chinese_name.keyword", query, size, ["id"])["values"])
            # print("1")
            # print(ids)
            # ids.extend(self.client.matchterm(index, "chinese_name", query, size, ["id"])["values"])
            # print("2")
            # print(ids)
            # ids.extend(self.client.prefix(index, "chinese_name", query, size, ["id"])["values"])
            # ids.extend(self.client.matchPhrase(index, "entity_name", query, 5, size, ["id"])["values"])
            # if len(ids) == 0:
            ids.extend(
                self.client.wildcard(index, "chinese_name.keyword", prewildcardquery, wildcardsize, ["id"])["values"])
            # ids.extend(self.client.matchPhrase(index, "chinese_name.keyword", query, 5, size, ["id"])["values"])
            ids.extend(self.client.wildcard(index, "chinese_name.keyword", middlewildcardquery, wildcardsize, ["id"])[
                           "values"])
            # for uchar in query:
            #     ids.extend(self.client.fuzzy(index, "chinese_name.keyword", uchar, size, ["id"])["values"])
        else:
            ids.extend(self.client.term(index, "entity_name.keyword", query, size, ["id"])["values"])
            ids.extend(self.client.term(index, "entity_name", query, size, ["id"])["values"])
            ids.extend(
                self.client.wildcard(index, "entity_name.keyword", prewildcardquery, wildcardsize, ["id"])["values"])
            # ids.extend(self.client.matchPhrase(index, "chinese_name.keyword", query, 5, size, ["id"])["values"])
            ids.extend(
                self.client.wildcard(index, "entity_name.keyword", middlewildcardquery, wildcardsize, ["id"])["values"])
            # ids.extend(self.client.matchPhrase(index, "entity_name.keyword", query, 5, size, ["id"])["values"])
            # ids.extend(self.client.prefix(index, "entity_name.keyword", query, size, ["id"])["values"])
        # ids = list(set(ids))
        # print("3")
        # print(ids)
        # score
        # data = ES.findByIdList(index, doc_type, ids, False, ["in*", "out*"])["data"]
        # rank = []
        # print("data")
        # print(data)
        # # graph
        # for item in data:
        #     id = item["id"]
        #     count = 0
        #     for key in item:
        #         if key in ["id", "type", "score", "instagram_username", "inception"]:
        #             continue
        #         tmp = self.str_to_container(item[key])
        #         count += len(tmp)
        #     rank.append({"id": id, "count": count})
        # rank.sort(key=lambda k: k["count"], reverse=True)
        # # get info
        # ids = []
        # res = {"code": 0, "data": {"nodes": []}}
        # flag = 0
        # for i in range(len(ids)):
        #     tmp = ES.findById(index, doc_type, rank[i]["id"], False,
        #                       ["id", "entity_name", "entity_type", "chinese_name", "img"])["data"]
        #     tmp["name"] = tmp["chinese_name"]
        #     if tmp["name"] == "":
        #         tmp["name"] = tmp["entity_name"]
        #     tmp.pop("chinese_name")
        #     tmp.pop("entity_name")
        #     tmp["type"] = tmp["entity_type"]
        #     tmp.pop("entity_type")
        #     res["data"]["nodes"].append(tmp)
        #     flag += 1
        #     if (flag >= 20):
        #         break
        # ids = []
        # get rid of repeated ids without influencing the order
        # print("ids before", ids)
        grrfunc = lambda x, y: x if y in x else x + [y]
        ids = reduce(grrfunc, [[], ] + ids)
        # print("ids after", ids)

        res = {"code": 0, "data": {"nodes": []}}
        flag = 0
        entity_list = \
        ES.findByIdList(index, doc_type, ids, False, ["id", "entity_name", "entity_type", "chinese_name", "img"])[
            "data"]
        from .rescoreFuncs import rescore_chinese_entities
        # res["data"]["nodes"] = rescore_chinese_entities(entity_list)
        # return res
        after_rescored = rescore_chinese_entities(entity_list)

        for entity in after_rescored:
            #     tmp = ES.findById(index, doc_type, ids[i], False,
            #                       ["id", "entity_name", "entity_type", "chinese_name", "img"])["data"]
            #
            #     # print(tmp["chinese_name"], tmp["entity_name"])
            #     # if tmp["entity_type"] == "other":
            #     #     continue
            entity["name"] = entity["chinese_name"]
            if entity["name"] == "":
                entity["name"] = entity["entity_name"]
            entity.pop("chinese_name")
            entity.pop("entity_name")
            entity["type"] = entity["entity_type"]
            entity.pop("entity_type")
            entity.pop("weight")
            res["data"]["nodes"].append(entity)
            flag += 1
            if (flag >= 30):  # before is 20
                break

        # res["data"]["nodes"] = rescore_chinese_entities(entity_list)
        return res

    # @func_line_time
    def QBSearch(self, keyword: str, type: str):

        """
        :param idlist: query idlist
        :param type: "geo" / "net" / "document"
        :return:
        """
        res = {"code": 0, "data": {}}
        SearchEntity = []

        set_index = self._config["table_name"]["set"]
        pro_index = self._config["table_name"]["project"]
        for _d in self.fuzzyMatch(keyword)["data"]["nodes"]:
            _d["img"] = "http://10.60.1.143/pic_lib/padded/{id}.png".format(id=_d["id"])
            SearchEntity.append(_d)
        SearchSet = self.client.match(set_index, set_index, "name", query=keyword, source=["id", "name", "type"])
        SearchPro = self.client.match(pro_index, pro_index, "name", query=keyword, source=["id", "name", "type"])

        if type == "net":
            res["data"]["SearchEntity"] = [_each for _each in SearchEntity if _each["type"] != "other"]
            res["data"]["SearchSet"] = SearchSet
            res["data"]["SearchPro"] = SearchPro

        elif type == "geo":
            _search = []
            entity_ids,result_ids = [], []
            gis = GISApplication()
            for _location in gis.searchLocationName(localName=keyword)["data"]:
                _location["type"] = "locationName"
                _location["img"] = ""
                _search.append(_location)
            for _each in SearchEntity:
                if _each["type"] == "organization":
                    _search.append(_each)

                elif _each["type"] != "other":
                    entity_ids.append(_each["id"])
            # 香港case实体有6.9万关系事件，1500关系实体，暂时放掉
            try:
                for x in ["Q8646", "Q17704", "Q19483", "Q143946", "Q220207", "Q597725", "Q598086"]:
                    if x in entity_ids:
                        entity_ids.remove(x)
                a = self.graph.select_related(entity_ids, "event")
                result_ids = [id for id in self.graph.select_related(entity_ids, "event")["data"][0]]
            except:
                pass
            for _each in SearchEntity:
                if _each["id"] in result_ids:
                    _search.append(_each)

            res["data"]["SearchEntity"] = _search
            res["data"]["SearchSet"] = SearchSet

        elif type == "document":
            res["data"]["SearchEntity"] = SearchEntity
            res["data"]["SearchSet"] = SearchSet
        else:
            res["code"] = -1
            return res

        return res

    ##############################################start#################################################################
    '''待定接口--->>> 文档统计'''

    def docStatistics(self, query: str, database: str = "nlu", collection: str = "ParsedData"):
        self.MongoClient()
        self.response = {}
        self.response["code"] = 0
        self.response["data"] = []

        body = self.generateMatchPhraseDSL(self._config["param"]["es"]["doc"]["index"], query)
        searchResult = self.Client.search(index=self._config["param"]["es"]["doc"]["index"], body=body)
        searchResult = searchResult["hits"]["hits"]
        if (len(searchResult) == 0):
            self.response["code"] = -1
            return self.response

        self.entity = {}
        self.entity["child"] = []
        self.entity["num"] = 0
        self.entity["name"] = "entity"
        self.entitylabel = ["PER", "ORG"]

        self.topic = {}
        self.topic["child"] = []

        for doc in searchResult:
            filter = {}
            filter["_id"] = doc["_id"]
            res = self.mongoDBFind(database, collection, filter)
            for i in res:
                self.entityCount(i["_nlu_ner"], doc["_id"])
                self.topicCount(i["_nlu_topic"], doc["_id"])

        cnt = 0
        num = 0
        for i in self.entity["child"]:
            cnt += i["count"]
            num += i["num"]
        self.entity["total"] = cnt
        self.entity["num"] = num
        for i in self.entity["child"]:
            i["per"] = int(i["count"] * 100 / cnt)
            for item in i["child"]:
                # 按照value进行排序
                for (docid, count) in sorted(item["tmp"].items(), key=lambda x: x[1], reverse=True):
                    item["ItemList"].append(docid)
                del item["tmp"]
                item["per"] = int(item["count"] * 100 / cnt)
            i["child"].sort(key=lambda x: x["count"], reverse=True)

        self.topic["name"] = "topic"
        self.topic["num"] = len(self.topic["child"])
        cnt = 0
        for i in self.topic["child"]:
            cnt += i["count"]
        self.topic["total"] = cnt
        for i in self.topic["child"]:
            i["per"] = int(i["count"] * 100 / self.topic["total"])

        self.response["data"].append(self.entity)
        self.response["data"].append(self.topic)
        # self.response["data"].append(self.time)
        return self.response

    def MongoClient(self, host: str = "10.60.1.140", port: int = 6080, usr: str = "root", pwd: str = "111111"):
        self.mongoclient = pymongo.MongoClient(host, port)
        self.admin = self.mongoclient.admin
        self.admin.authenticate(usr, pwd)

    def topicCount(self, topic: str, docid: str):
        index = self.getObjIndex(self.topic["child"], "name", topic)
        if (index == -1):
            add = {}
            add["name"] = topic
            add["count"] = 1
            add["ItemList"] = []
            add["ItemList"].append(docid)
            self.topic["child"].append(add)
        else:
            self.topic["child"][index]["count"] += 1
            self.topic["child"][index]["ItemList"].append(docid)

    def entityCount(self, data: list, docid: str):
        for i in range(len(data)):
            for j in range(len(data[i])):
                if (data[i][j][1].startswith("B-")):
                    st = data[i][j][0]
                    match = data[i][j][1][2:]
                    if (match not in self.entitylabel):
                        continue
                    # entity type
                    matchindex = self.getObjIndex(self.entity["child"], "name", match)
                    if (matchindex == -1):
                        tmp = {}
                        tmp["name"] = match
                        tmp["num"] = 0
                        tmp["count"] = 0
                        tmp["child"] = []
                        self.entity["child"].append(tmp)
                    j += 1
                    while (i < len(data) and data[i][j][1].endswith(match) and not data[i][j][1].startswith("B-")):
                        st += " " + data[i][j][0]
                        j += 1
                    # entity
                    index = self.getObjIndex(self.entity["child"][matchindex]["child"], "name", st)
                    if (index == -1):
                        add = {}
                        add["name"] = st
                        add["count"] = 1
                        add["ItemList"] = []
                        add["tmp"] = {}
                        self.entity["child"][matchindex]["num"] += 1
                        self.entity["child"][matchindex]["count"] += 1
                        self.entity["child"][matchindex]["child"].append(add)
                    else:
                        self.entity["child"][matchindex]["count"] += 1
                        self.entity["child"][matchindex]["child"][index]["count"] += 1
                    # docid
                    if (docid in self.entity["child"][matchindex]["child"][index]["tmp"]):
                        self.entity["child"][matchindex]["child"][index]["tmp"][docid] += 1
                    else:
                        self.entity["child"][matchindex]["child"][index]["tmp"][docid] = 1

    def mongoDBFind(self, database: str, collection: str, filter: dict):
        db = self.mongoclient[database]
        col = db[collection]
        res = col.find(filter)
        return res

    def getObjIndex(self, List: list, field: str, key: str):
        for i in range(len(List)):
            if (List[i][field] == key):
                return i
        return -1
    #################################################end################################################################
