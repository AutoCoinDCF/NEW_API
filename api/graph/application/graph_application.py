"""
SQLGraphAPI application level:
1.call utility method to get graph data
2.use encapsulated DataFrame or Graph data processing
"""


# configs
from api.graph.application.config.config_column_mapping import CONFIG_column_mapping
# database API
from api.graph.utility.graph_inquiry import GraphInquiry
# process data
from api.graph.utility.MiddleDataFrameFolder import MiddleDataFrameGraph
# algorithm
from api.graph.application.algorithm import bfs_tree
from api.graph.utility.utility import Match_list
# from api.web.utils import func_line_time

import api.configs.dynamic_config as dy_config
from api.log.QBLog import QBLog


class GraphApplication(object):
    def __init__(self, user: str = None, password: str = None, ip: str = '10.60.1.142',
                 port: int or str = 8123, database_name: str = 'default',
                 graph_name: str = "relationGraph",
                 event_graph_database_name: str = 'EEDGraphSingular_v16', event_graph_graph_name: str = "relationGraph",
                 ):
        self.graph_inquiry_helper = GraphInquiry(
            user=user, password=password, ip=ip, port=port, database_name=database_name, graph_name=graph_name,
            event_graph_database_name=event_graph_database_name, event_graph_graph_name=event_graph_graph_name)
        self.database_name = database_name
        self.event_graph_database_name = event_graph_database_name
        self.math = Match_list()
        self.logger = QBLog({'LOG_LEVEL': dy_config.LOG_LEVEL}, self.__class__.__name__)

    def select_path(self, start_node: str, end_node: str, step_num=None) -> dict:
        result = self.graph_inquiry_helper.select_path(start_node, end_node, step_num)
        if result["code"] != 0:
            self.logger.error(f'select_path sql error {result}')
            return {"code": -2}
        graph = MiddleDataFrameGraph(
            code=result["code"],
            message=result["message"],
            vertex_data=result["data"][0]["nodes"],
            edge_data=result["data"][0]["links"], )

        graph.rename_column()
        graph.add_picture()
        graph.add_name()
        graph.fliter_links_column()

        def nodes_combination(meta_type="entity"):
            if not graph.data["nodes"].empty:
                column_list = list(
                    CONFIG_column_mapping["SQLGraph"][self.event_graph_database_name][meta_type].values())
                meta_type_nodes = graph.data["nodes"].loc[graph.data["nodes"]["meta_type"].isin([meta_type]), :]
                if meta_type == "entity":
                    return meta_type_nodes.loc[:, [x for x in column_list] + ["name", "img"]].to_dict(orient='records')
                else:
                    return meta_type_nodes.loc[:, [x for x in column_list]].to_dict(orient='records')
            else:
                return []

        nodes_all = nodes_combination("entity") + nodes_combination("event") + nodes_combination("document")
        links_end = graph.data["links"].to_dict(orient='records')
        nodes_end = self.math.links_to_end(nodes_all, links_end)

        return {
            "code": 0,
            "message": "",
            "data": {
                "nodes": nodes_end,
                "links": links_end
            }
        }

    def calculate_bfs_tree(self, nodeIds: list, root_node_id_list: list, edge_list: list = None,
                           edge_from_backend: bool = True):
        nodes = nodeIds
        if not edge_from_backend:
            edges = edge_list if edge_list else []
        else:
            subgraph_data = self.graph_inquiry_helper.select_edges_inside_nodes(
                nodeIds=nodeIds)
            if subgraph_data["code"] != 0:
                self.logger.error(f'select_path sql error {subgraph_data}')
                return {"code": -2}
            subgraph = MiddleDataFrameGraph(
                code=subgraph_data["code"],
                vertex_data=subgraph_data["data"][0]["nodes"],
                edge_data=subgraph_data["data"][0]["links"], )
            if subgraph.code != 0:
                return subgraph.to_dict()
            subgraph.rename_column()
            edges = subgraph.to_dict()["data"][0]["links"]
        data = bfs_tree.bfs_tree(nodes=nodes, edges=edges, root_node_id_list=root_node_id_list)
        for node in data[1]:
            nodeIds.remove(node)
        return {
            "code": 0,
            "message": "",
            "nodes": nodeIds,
            "data": [data[0]]
        }

    # @func_line_time
    def select_related(self, nodeIds: list, type_label: str = None):
        result = self.graph_inquiry_helper.select_related_out(nodeIds=nodeIds, type_label=type_label)
        if result["code"] != 0:
            self.logger.error(f'select_path sql error {result}')
            return {"code": -2}
        graph = MiddleDataFrameGraph(
            code=result["code"],
            message=result["message"],
            vertex_data=result["data"][0]["nodes"],
            edge_data=result["data"][0]["links"], )
        if graph.code != 0:
            return graph.to_dict()
        graph.rename_column()
        if type_label == "entity":
            graph.add_name()
            graph.add_picture()
        if type_label == "event":
            graph.keep_certain_types_links(nodeIds=nodeIds, whether_event=True)
        else:
            graph.keep_certain_types_links(nodeIds=nodeIds)
        graph.links_translate()
        graph.nodes_translate()
        graph.links_directed_to_undirected()
        graph.separator_to_underline()
        # if type_label == "event" or type_label == "document":
        #     graph.relation_name_T()
        result = graph.to_dict_join_link_type_to_node(type_label)
        for x in result["data"][0]:
            for y in result["data"][0][x]["links"]:
                y["type"], y["undirected_type"] = y["undirected_type"], y["type"]
        return result

    def short_path_str(self, start_node, end_node, typeLabel: str, sql_type: str, step: str) -> dict:
        if sql_type == "short_path_str":
            result = self.graph_inquiry_helper.short_path_str(start_node, end_node, step)
        elif sql_type == "short_path_list":
            result = self.graph_inquiry_helper.short_path_list(start_node, end_node, step)

        if result["code"] != 0:
            self.logger.error(f'select_path sql error {result}')
            return {"code": -2}

        graph = MiddleDataFrameGraph(
            code=result["code"],
            message=result["message"],
            vertex_data=result["data"][0]["nodes"],
            edge_data=result["data"][0]["links"], )
        if graph.code != 0:
            return -1

        if graph.code == 0 and not result["data"][0]["nodes"]:
            return [[], []]
        graph.rename_column()
        graph.add_picture()
        graph.add_name()
        if typeLabel == "event":
            graph.keep_certain_types_links(nodeIds=[start_node, end_node], whether_path=True, whether_event=True)
        else:
            graph.keep_certain_types_links(nodeIds=[start_node, end_node], whether_path=True)
        graph.links_translate()
        if sql_type == "short_path_str":
            res = graph.filter_column([start_node], [end_node], typeLabel)
        elif sql_type == "short_path_list":
            res = graph.filter_column(start_node, end_node, typeLabel)

        def nodes_combination(meta_type="entity"):
            if not res["nodes"].empty:
                column_list = list(
                    CONFIG_column_mapping["SQLGraph"][self.event_graph_database_name][meta_type].values())
                meta_type_nodes = res["nodes"].loc[res["nodes"]["meta_type"].isin([meta_type]), :]
                if meta_type == "entity":
                    return meta_type_nodes.loc[:, [x for x in column_list] + ["name", "img"]].to_dict(orient='records')
                else:
                    return meta_type_nodes.loc[:, [x for x in column_list]].to_dict(orient='records')
            else:
                return []

        end_nodes = nodes_combination("entity") + nodes_combination("event") + nodes_combination("document")
        end_links = res["links"].to_dict(orient='records')

        return end_nodes, end_links

    def short_path(self, nodeIds_start: list, step: str, nodeIds_end: list = None, typeLabel: str = "all") -> dict:
        all_nodes = []
        all_links = []
        if not nodeIds_end:
            nodeIds_row = [x for x in self.math.group_id(nodeIds_start) if len(x) == 2]
            nodeIds_T = nodeIds_row.copy()
            for x in nodeIds_T:
                x[0], x[1] = x[1], x[0]
            nodeIds = nodeIds_row + nodeIds_T

            for node_id in nodeIds:
                result = self.short_path_str(node_id[0], node_id[1], typeLabel, "short_path_str", step)
                all_nodes += result[0]
                all_links += result[1]
        else:
            forward_result = self.short_path_str(nodeIds_start, nodeIds_end, typeLabel, "short_path_list", step)
            T_result = self.short_path_str(nodeIds_end, nodeIds_start, typeLabel, "short_path_list", step)
            if forward_result == -1 or T_result == -1:
                return {"code": -1}
            else:
                all_nodes = all_nodes + forward_result[0] + T_result[0]
                all_links = all_links + forward_result[1] + T_result[1]

        end_nodes = self.math.links_nodes_filter(all_nodes)
        end_links = self.math.links_nodes_filter(all_links)

        return {
            "code": 0,
            "message": "",
            "data": {
                "nodes": end_nodes,
                "links": end_links
            }
        }

    def select_common(self, nodeIds: list, com_label: str = None) -> dict:
        result = self.graph_inquiry_helper.select_common(nodeIds, com_label)
        if result["code"] != 0:
            self.logger.error(f'select_path sql error {result}')
            return {"code": -2}
        graph = MiddleDataFrameGraph(
            code=result["code"],
            message=result["message"],
            vertex_data=result["data"][0]["nodes"],
            edge_data=result["data"][0]["links"], )
        if graph.code != 0:
            return graph.to_dict()
        graph.rename_column()
        graph.add_name()
        graph.add_picture()
        if com_label == "event":
            graph.keep_certain_types_links(nodeIds=nodeIds, whether_path=True, whether_event=True)
        else:
            graph.keep_certain_types_links(nodeIds=nodeIds, whether_path=True)
        graph.links_translate()
        graph.separator_to_underline()
        graph.fliter_links_column()

        def nodes_combination(meta_type="entity"):
            if not graph.data["nodes"].empty:
                column_list = list(
                    CONFIG_column_mapping["SQLGraph"][self.event_graph_database_name][meta_type].values())
                meta_type_nodes = graph.data["nodes"].loc[graph.data["nodes"]["meta_type"].isin([meta_type]), :]
                if meta_type == "entity":
                    return meta_type_nodes.loc[:, [x for x in column_list] + ["name", "img"]].to_dict(orient='records')
                else:
                    return meta_type_nodes.loc[:, [x for x in column_list]].to_dict(orient='records')
            else:
                return []

        nodes_end = nodes_combination("entity") + nodes_combination("event") + nodes_combination("document")
        links_end = graph.data["links"].to_dict(orient='records')
        return {
            "code": 0,
            "message": "",
            "data": {
                "nodes": nodes_end,
                "links": links_end
            }
        }

    def entity_num(self, entity_id: str):
        return len(self.graph_inquiry_helper.entity_num(entity_id)["data"][0]["links"])

    def community(self, from_ids: list, to_ids: list, method: str, num: list):
        ids_list = from_ids + to_ids
        ids_group = [[from_ids[_index], to_ids[_index], num[_index]] for _index in range(len(from_ids))] if num \
            else [[from_ids[_index], to_ids[_index], 1] for _index in range(len(from_ids))]
        self.graph_inquiry_helper.creat_vertex_table(vertex_table_name='node', field=["entity_id"],
                                                     databases_name='CommunityDetection', )
        self.graph_inquiry_helper.creat_edge_table(databases_name='CommunityDetection', edge_table_name='edge',
                                                   field=["from_id", "to_id", "num"], rely=['CommunityDetection.node'])
        self.graph_inquiry_helper.insert_vertex_table(vertex_table_name='CommunityDetection.node',
                                                      idlist=list(set(ids_list)))
        self.graph_inquiry_helper.insert_edge_table(edge_table_name='CommunityDetection.edge', idlist=ids_group)
        self.graph_inquiry_helper.creat_graph(graph_name='CommunityDetection.relationGraph',
                                              rely_edge_name=['CommunityDetection.edge'])
        result = self.graph_inquiry_helper.sql_community(graph_name='CommunityDetection.relationGraph', c_method=method,
                                                         column="num")
        self.graph_inquiry_helper.drop_databases(databases_name='CommunityDetection')

        return result
