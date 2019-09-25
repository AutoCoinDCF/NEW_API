"""The flask-resources of the qb-system"""

import copy
from typing import Dict

from api.log.QBLog import QBLog
import api.configs.dynamic_config as dy_config
from .ResourceWithParser import ResourceWithParser as MyBaseResource
from api.BackendAPI.BackendAPI import SPACE_BACKEND_API
from api.graph.utility.utility import NestedHelper
from api.web.utils import new_response
# from api.web.utils import func_line_time
from api.web.utils import totalTime, asynchronous_task

logger = QBLog({
    'LOG_LEVEL': dy_config.LOG_LEVEL
})


def add_timestamp(data: dict, timestamp: str) -> dict:
    data["timestamp"] = timestamp
    return data


# -----------------------------------------search----------------------------------

class FuzzyMatch(MyBaseResource):
    """ The id of FuzzyMatched entity(node) """

    @totalTime
    def get(self) -> Dict:
        """
        Front end send a name pattern string to get the nodeId list fuzzy match that name
        :return the operation code and the nodeId list which match the name send by front end
        """
        args = self._parser.parse_args()
        params = dict(
            query=args["pattern"],
            size=args["size"]
        )
        try:
            data = SPACE_BACKEND_API.EsObj_API.fuzzyMatch(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class QBSearch(MyBaseResource):
    @totalTime
    def get(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            keyword=args["keyword"],
            type=args["type"]
        )
        try:
            data = SPACE_BACKEND_API.EsObj_API.QBSearch(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# -----------------------------------------entity----------------------------------

class EntityInfo(MyBaseResource):
    """ The coarse information of nodes """

    @totalTime
    def post(self) -> Dict:
        """
        Front end send a nodeIds list to get* the list of rough information of each node
        :return: the operation code and the summary information list of each node
        """
        args = self._parser.parse_args()
        params = dict(
            idlist=args["nodeIds"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.roughFindbyIdList(**params)
            # fake id to deal with
            for error_id in data[1]:
                data[0]["data"][0]["nodes"].append({
                    "id": error_id,
                    "img": "",
                    "Entity_type": "",
                    "name": "",
                    "loaded": ''
                }, )
            return data[0]
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class EntityDetail(MyBaseResource):
    """ The detail information of nodes """

    @totalTime
    def post(self) -> Dict:
        """
        Front end send a nodeIds list to get* the list of detail information of each node

        :return: the operation code and the detail information list of each node

        *Note: The reason why we use POST rather than GET, is that we need to send a list, which
        should be passed by json through html body. POST has body but GET doesn't have.
        """
        args = self._parser.parse_args()

        params = dict(
            idlist=args["nodeIds"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.accFindbyIdList(**params)
            data_end = NestedHelper(data[0]).deep_drop_empty()
            for error_id in data[1]:
                data_end["data"].append({"id": error_id})
            return data_end
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# -----------------------------------------event----------------------------------

class EventDetail(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            eventIds=args["EventIds"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.findbyIdList(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class EventDoc2Time(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        """
        Front end send a list of eventIds, and Backend return their time
        :return: the time and count of the events
        """
        args = self._parser.parse_args()
        params = dict(
            eventIds=args["eventIds"],
            docIds=args["docIds"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.event_2_time(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# -----------------------------------------document----------------------------------

class ContextById(MyBaseResource):
    @totalTime
    def get(self) -> Dict:
        """
        Front end send a context id to get the context
        :return: the context
        """
        args = self._parser.parse_args()
        params = dict(
            doc_ids=[args["idValue"]]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.searchByDocIdList(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DocumentDetail(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        """
        Front end send a list of doc id, and es return the articles matching the ids
        :return: the articles matching the ids
        """
        args = self._parser.parse_args()
        params = dict(
            doc_ids=args["docIds"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.searchByDocIdList(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class Translate(MyBaseResource):
    @totalTime
    def get(self):
        args = self._parser.parse_args()
        params = dict(
            id=args["id"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.translate(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class ContextByText(MyBaseResource):
    @totalTime
    def get(self) -> Dict:
        """
        Front end send a text string, and es search context associated with the string
        :return: the associated contexts' summary
        """
        args = self._parser.parse_args()

        params = dict(
            query=args["query"], page=args["page"], timeStart=args["timeStart"],
            timeEnd=args["timeEnd"], isSortByTime=args["isSortByTime"],
            PageSize=args["PageSize"], limit=args["limit"]
        )
        try:
            data = SPACE_BACKEND_API.EsObj_API.fullTextSearch(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class ContextSectionSearch(MyBaseResource):
    @totalTime
    def get(self) -> Dict:
        """
        Front end send a string(key words for searching), and es return the sentences
        matching the keywords
        :return: the the sentences matching the keywords
        """
        args = self._parser.parse_args()
        params = dict(
            query=args["keyword"]
        )
        try:
            data = SPACE_BACKEND_API.EsObj_API.sectionSearch(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# 618_v1.0版本的词云接口
class RowDocTop(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            ids=args["ids"],
            typeLabel=args["typeLabel"],
            word=args["word"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.row_doc_top(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DocTop(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            idList=args["idList"],
            ids=args["ids"],
            names=args["names"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.doc_top_by_topic(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DocTopTime(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            idList=args["idList"],
            times=args["times"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.doc_top_time(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class WordDoc(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            idList=args["idList"],
            word=args["word"],
            speech=args["speech"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.wordDoc(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# -----------------------------------------GIS----------------------------------

class Node2GIS(MyBaseResource):
    @totalTime
    def post(self):
        """
            Given nodeids
            Return related locations and their Geographic coordinates
            :return:a dict of two fields:
                "time": time in which the article mentioning the key word is published
                "count": articles number at each time
        """
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.node2GIS(nodeIds=args["nodeIds"])
        return data


class LocationName(MyBaseResource):
    @totalTime
    def get(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.searchLocationName(localName=args["localName"])
        return data


class ExploreOrg(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.exploreOrg(geometry=args["geometry"])
        return data


class exploreEvent(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.exploreEvent(geometry=args["geometry"])
        return data


class ExploreGeoTar(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.exploreGeoTar(geometry=args["geometry"])
        return data


class getEventByIds(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.getEventByIds(event_ids=args["ids"])
        return data


# class getParamByIds(MyBaseResource):
#     @totalTime
#     def post(self):
#         args = self._parser.parse_args()
#         data = SPACE_BACKEND_API.GIS_API.getParamsByIds(param_ids=args["nodeIds"])
#         return data

class getParamByIds(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.getParamsByIds(orgIds=args["orgIds"],eventIds=args["eventIds"],contentIds=args["contentIds"])
        return data


class searchAreaByIds(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.searchAreaByIds(aids=args["nodeIds"])
        return data


class getOrgByIds(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.getOrgByIds(org_ids=args["ids"])
        return data


class searchthematic(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.searchthematic(queryWord=args["queryWord"])
        return data

class createLouce(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.createLouce(ids=args["ids"])
        return data

class recommendThematics(MyBaseResource):
    def get(self):
        # args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.recomThematics()
        return data


class raiseThematicClickCount(MyBaseResource):
    def post(self):
        args = self._parser.parse_args()
        data = SPACE_BACKEND_API.GIS_API.raiseThematicWeight(thematicNames=args["thematicNames"])


# -----------------------------------------set&project----------------------------------

class IndexSetData(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            data=args["data"]
        )
        try:
            data = SPACE_BACKEND_API.EsUtils_API.insert_index_set_data(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise

    @totalTime
    def put(self):
        args = self._parser.parse_args()
        params = dict(
            data=args["data"]
        )
        try:
            data = SPACE_BACKEND_API.EsUtils_API.update_index_set_data(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class LoadSetData(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            idlist=args["idlist"], label=args["label"],
            query=args["query"], page=args["page"], size=args["pagesize"],
            limit=args["limit"]
        )
        try:
            data = SPACE_BACKEND_API.EsUtils_API.findSetorProject(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DeleteSetData(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            idlist=args["idlist"], label=args["label"], type=args["type"]
        )
        try:
            data = SPACE_BACKEND_API.EsUtils_API.deleteSetorProject(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class IndexProjectData(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            data=args["data"]
        )
        try:
            data = SPACE_BACKEND_API.EsUtils_API.insert_index_project_data(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise

    @totalTime
    def put(self):
        args = self._parser.parse_args()
        params = dict(
            data=args["data"]
        )
        try:
            data = SPACE_BACKEND_API.EsUtils_API.update_index_project_data(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# -----------------------------------------related----------------------------------

class FindPath(MyBaseResource):
    """ The neighbor relations (links) and entities (nodes) of a node """

    @totalTime
    def get(self) -> Dict:
        """
        Front end send a nodeId to get its neighbor links and nodes summary information.
        This is a coarse-grained expand, including two ways: event expand and knowledge expand.

        :return: The neighbor links and nodes of a node in the specified expanding way
        (event or knowledge or both)
        """
        args = self._parser.parse_args()
        params = dict(
            start_node=args['start'],
            end_node=args['end'],
            step_num=args['step']
        )
        try:
            data = SPACE_BACKEND_API.Graph_API.select_path(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class CalculateBFSTree(MyBaseResource):
    @totalTime
    def post(self):
        """
        frontend give a nodeId list and a root nodeId, return a breadth-first tree of these nodes
        http_args:
            :nodeIds: a list of nodeId
            :RootNodeId: root of the tree
            :EdgeList: [optimal, default None] the edge list used in the bfs-tree generation
            :edge_from_backend:[default True] if True, use edges from database, else use edges from EdgeList
        :return: a breadth-first tree of the nodes
        """
        args = self._parser.parse_args()
        params = dict(
            nodeIds=args["nodeIds"], root_node_id_list=args["RootNodeIdList"],
            edge_list=args["EdgeList"], edge_from_backend=args["edge_from_backend"]
        )
        try:
            data = SPACE_BACKEND_API.Graph_API.calculate_bfs_tree(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class RelatedAll(MyBaseResource):
    @totalTime
    # @func_line_time
    def post(self):
        args = self._parser.parse_args()
        type_label = args["TypeLabel"]
        Group = args["Group"]
        data = {"RelatedEntity": {},
                "RelatedEvent": {},
                "RelatedDocument": {}}

        sub_type = lambda type_label: SPACE_BACKEND_API.Graph_API.select_related(
            nodeIds=args["NodeIds"], type_label=type_label)
        if type_label == "all":
            sub_data_entity = sub_type("entity")
            sub_data_event = sub_type("event")
            sub_data_document = sub_type("document")
        else:
            sub_data = sub_type(type_label)

        if type_label == "entity":
            data["RelatedEntity"] = dict(data["RelatedEntity"], **sub_data["data"][0])
        elif type_label == "event":
            data["RelatedEvent"] = dict(data["RelatedEvent"], **sub_data["data"][0])
        elif type_label == "document":
            data["RelatedDocument"] = dict(data["RelatedDocument"], **sub_data["data"][0])
        elif type_label == "all":
            data["RelatedEntity"] = dict(data["RelatedEntity"], **sub_data_entity["data"][0])
            data["RelatedEvent"] = dict(data["RelatedEvent"], **sub_data_event["data"][0])
            data["RelatedDocument"] = dict(data["RelatedDocument"], **sub_data_document["data"][0])

        data = new_response(code=0, message="", data=[data])

        try:
            l = {}
            for x in data["data"]:
                for y in x:
                    for z in x[y]:
                        for t in x[y][z]["links"]:
                            if t["from"] + t["to"] in l or t["to"] + t["from"] in l:
                                if t["from"] + t["to"] in l:
                                    t["id"] = l[t["from"] + t["to"]]
                                elif t["to"] + t["from"] in l:
                                    t["id"] = l[t["to"] + t["from"]]
                            else:
                                l[t["from"] + t["to"]] = t["id"]
        except:
            return {
                "code": 0,
                "data": [
                    {"RelatedEntity": {},
                     "RelatedEvent": {},
                     "RelatedDocument": {}}
                ]
            }

        if Group:
            for related_type in data["data"][0]:
                if related_type == "RelatedEntity":
                    relation_nodes = copy.deepcopy(data["data"][0][related_type])
                    for _related in data["data"][0][related_type]:
                        relation = {}
                        relation_nodes[_related]["nodes"] = []
                        for group_node in data["data"][0][related_type][_related]["nodes"]:
                            if group_node["relation"] in relation:
                                relation[group_node["relation"]].append(group_node)
                            else:
                                relation[group_node["relation"]] = []
                                relation[group_node["relation"]].append(group_node)
                            del group_node["relation"]
                            relations_group = [{"relation": key, "data": relation[key]} for key in relation]
                        for _each in relations_group:
                            relation_nodes[_related]["nodes"].append(_each)
                    data["data"][0][related_type] = relation_nodes

        return data


class ShortPath(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            nodeIds_start=args["NodeIds_single"],
            nodeIds_end=args["NodeIds_double"],
            typeLabel=args['typeLabel'],
            step=args["step"]
        )
        try:
            data = SPACE_BACKEND_API.Graph_API.short_path(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class CommonAll(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            nodeIds=args["NodeIds"],
            com_label=args['ComLabel']
        )
        try:
            data = SPACE_BACKEND_API.Graph_API.select_common(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class Community(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            from_ids=args["from_ids"], to_ids=args["to_ids"],
            method=args["method"], num=args["num"]
        )
        try:
            data = SPACE_BACKEND_API.Graph_API.community(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# -----------------------------------------Statistics----------------------------------

class GraphAttr(MyBaseResource):
    # @func_line_time
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            entityIds=args["entityIds"],
            eventIds=args["eventIds"],
            docIds=args['docIds'],
            type=args["type"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.graphAttr(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class Aggregation(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            allNodeIds=args["allNodeIds"],
            selectNodeIds=args["selectNodeIds"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.aggregation(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class FieldTranslate(MyBaseResource):
    @totalTime
    def get(self):
        args = self._parser.parse_args()
        params = dict(
            type=args["type"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.fieldTranslate(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class KeywordMatch(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            type=args["type"], Attr=args["Attr"],
            page=args["page"], pageSize=args["pageSize"],
            max=args["max"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.keywordMatch(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class NodeDetail(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            type=args["type"],
            nodeIds=args["nodeIds"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.nodeDetail(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


# -----------------------------------------other----------------------------------

class NodeStatisticsInType(MyBaseResource):
    @totalTime
    def post(self):
        args = self._parser.parse_args()
        params = dict(
            ids=args["nodeIds"],
            typename=args["typename"]
        )
        try:
            data = SPACE_BACKEND_API.EsObj_API.nodeStatisticsInType(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DocStatistics(MyBaseResource):
    @totalTime
    def get(self) -> Dict:
        """
        Front end send a string, and es return articles matching the string
        :return: articles matching the string
        """
        args = self._parser.parse_args()
        params = dict(
            query=args["query"]
        )
        try:
            data = SPACE_BACKEND_API.EsObj_API.docStatistics(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DataSearch(MyBaseResource):
    # @asynchronous_task
    @totalTime
    def get(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            keyword=args["query"],
            website=args["website"],
            requestNumber=args["requestNumber"]
        )
        try:
            data = SPACE_BACKEND_API.Fake_API.dataSearch(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class IndexDataSet(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            name=args["name"],
            des=args["des"],
            source=args["source"],
            ids=args["ids"],
            titles=args["titles"],
            urls=args["urls"]
        )
        try:
            data = SPACE_BACKEND_API.Fake_API.indexDataSet(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class SearchTask(MyBaseResource):
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            status=args["status"],
            source=args["source"],
            page=args["page"],
            pageSize=args["pageSize"]
        )
        try:
            data = SPACE_BACKEND_API.Fake_API.searchTask(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class ToDoTask(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            task_ids=args["task_ids"],
            dispose_type=args["dispose_type"]
        )
        try:
            data = SPACE_BACKEND_API.Fake_API.to_do_task(**params)
            return add_timestamp(data, args["timestamp"])
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class UploadTask(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            name=args["name"],
            des=args["des"],
            content=args["content"],
            source=args["source"]
        )
        try:
            data = SPACE_BACKEND_API.Fake_API.upload_task(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class SearchAttr(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            ids=args["ids"],
            ses=args["ses"]
        )
        try:
            data = SPACE_BACKEND_API.Fake_API.search_attr(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class SeAttr(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            search_id=args["search_id"],
            ids=args["ids"]
        )
        try:
            data = SPACE_BACKEND_API.Fake_API.se_attr(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class Test(MyBaseResource):
    def post(self) -> Dict:
        args = self._parser.parse_args()
        print(args)
        return args


class DocHighlight(MyBaseResource):
    @totalTime
    def get(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            doc_id=args["doc_id"],
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.doc_highlight(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class GetEntity(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            ids=args["ids"],
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.get_entity(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DocSentimentTime(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            idList=args["idList"],
            Time=args["Time"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.doc_sentiment_time(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class DocSentiment(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            idList=args["idList"],
            ids=args["ids"],
            names=args["names"]
        )
        try:
            data = SPACE_BACKEND_API.Mongo_API.doc_sentiment_by_topic(**params)
            return data
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class StrongConnectedSubgraph(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            from_ids=args["from_ids"],
            to_ids=args["to_ids"],
            node_num=args["node_num"]
        )
        res = {"code": 0, "data": {}}
        try:
            if args["node_num"] < 2:
                res["code"] = -1
                res["message"] = "not enough values to unpack (expected 2)"
                del res["data"]
            else:
                res["data"]["return_from_ids"], res["data"]["return_to_ids"] = \
                    SPACE_BACKEND_API.OperatorGraph_API.strong_connected_subgraph(**params)
            return res
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class CommunityDetect(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            from_ids=args["from_ids"],
            to_ids=args["to_ids"],
            community_num=args["community_num"]
        )
        res = {"code": 0, "data": {}}
        try:
            res["data"]["return_from_ids"], res["data"]["return_to_ids"] = \
                SPACE_BACKEND_API.OperatorGraph_API.community_detect(**params)
            return res
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class NodeImportance(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            from_ids=args["from_ids"],
            to_ids=args["to_ids"]
        )
        res = {"code": 0}
        try:
            res["data"]= SPACE_BACKEND_API.OperatorGraph_API.node_importance(**params)
            return res
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class EdgeImportance(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            from_ids=args["from_ids"],
            to_ids=args["to_ids"]
        )
        res = {"code": 0}
        try:
            res["data"]= SPACE_BACKEND_API.OperatorGraph_API.edge_importance(**params)
            return res
        except:
            logger.info(f'---error keys---\n{params}')
            raise


class TextClustering(MyBaseResource):
    @totalTime
    def post(self) -> Dict:
        args = self._parser.parse_args()
        params = dict(
            text_dict=args["text_dict"],
            class_num=args["class_num"]
        )
        res = {"code": 0, "data": {}}
        try:
            if args["class_num"] < 2:
                res["code"] = -1
                res["message"] = "not enough values to unpack (expected 2)"
                del res["data"]
            else:
                res["data"]["cluster_result"], res["data"]["keywords"], res["data"]["center_doc"] \
                    = SPACE_BACKEND_API.OperatorDoc_API.text_clustering(**params)
            return res
        except:
            logger.info(f'---error keys---\n{params}')
            raise
