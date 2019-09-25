"""
SQLGraphAPI utility level:
1.create a sql query
2.call executor to execute sql query and get raw response data
3.simply pre-process raw data (generate frontend-defined response code, extract useful data from raw data)
"""

import time

# from .restful_executor import Executor
from api.graph.utility.restful_executor import Executor
from api.graph.utility.utility import create_response_dict
from api.configs.MiddleEndConfig import CONFIG
from api.graph.utility.utility import Match_list
import api.configs.dynamic_config as dy_config
from api.log.QBLog import QBLog

logger = QBLog({
    'LOG_LEVEL': dy_config.LOG_LEVEL
})


class UtilityBaseGraphInquiry(object):
    """
    a base class of some basic method to get sql data and simply pre-process raw sqlgraph response data
    """

    def __init__(self, user: str = None, password: str = None, ip: str = '10.60.1.142',
                 port: int or str = 8123, database_name: str = 'default', graph_name: str = "relationGraph",
                 event_graph_database_name: str = 'default', event_graph_graph_name: str = "relationGraph", ):
        self.database_name = database_name
        self.graph_name = graph_name
        self.event_graph_database_name = event_graph_database_name
        self.event_graph_graph_name = event_graph_graph_name
        self.executor = Executor(user=user, password=password, ip=ip, port=port, database_name=database_name)
        self.match_list = Match_list()

    def get_nodes(self, query: str) -> dict:
        """
        execute sql query and return nodes from SQLgraph format JSON response
        :param query: sql string
        :return: a response dict with nodes
        """
        response = self.executor.execute(query, format="JSON")
        if response.status_code != 200:
            return create_response_dict(code=-1, message=response.text)
        else:
            return create_response_dict(code=0, nodes=response.json()["data"])

    def get_nodes_and_links(self, query: str) -> dict:
        """
        execute sql query and return nodes and links from SQLgraph fromat Graph response
        :param query: sql string
        :return: a response dict with nodes and links
        """
        response = self.executor.execute(query, format="Graph")
        if response.status_code != 200:
            return create_response_dict(code=-1, message=response.text)
        else:
            return create_response_dict(code=0, nodes=response.json()["nodes"], links=response.json()["links"])

    def post_sqlGraph(self, query: str, insert=False):
        try:
            self.executor.execute(query, format="", insert=insert)
        except Exception as error:
            logger.error(f'error operating sqlgraph database: {error}')

    def post_related(self, query: str):
        try:
            response = self.executor.execute_related(query)
            return create_response_dict(code=0, nodes=response["nodes"], links=response["links"])
        except Exception as error:
            logger.error(f'related search the failed error: {error}')
            return dict(code=-1)

class GraphInquiry(UtilityBaseGraphInquiry):
    """
    each utility method to get different data from sqlgraph
    """

    def select_entity_detail_by_id(self, nodeIds: list) -> dict:
        """
        a detailed inquire for entities
        :param nodeIds: the list of entity id
        :return: a list of entities id, name, type, image
        """
        query = f"""
            select
                *,
                __v.1 as __v
            from
                vertex({self.database_name}.{self.graph_name})
            where 
                __v in {f"({str(nodeIds)[1:-1]})"}
        """
        # print("%s %s" % ("select_entity_detail_by_id", query))
        return self.get_nodes(query)

    def select_neighbor_by_id(self, nodeIds: list, className: list = None) -> dict:
        """
        select all neighbors from nodeIds
        :param nodeIds: a list of nodeId
        :param className: if not None, neighbors' className should be in list className
        :return: all neighbors' nodes and links
        """
        query = f"""
            select
                *
            from
                out({self.database_name}.{self.graph_name}, {nodeIds}, 1)
            {f"where vertexProperty(edge.2.2, 'className') in {className}" if className else ""}
            union all
            select
                {"*"}
            from
                in({self.database_name}.{self.graph_name}, {nodeIds}, 1)
            {f"where vertexProperty(edge.2, 'className') in {className}" if className else ""}
        """
        # print("%s %s" % ("select_neighbor_by_id", query))
        return self.get_nodes_and_links(query)

    def select_in_by_id(self, nodeIds: list, className: list = None) -> dict:
        """
        select in neighbors from nodeIds
        :param nodeIds: a list of nodeId
        :param className: if not None, neighbors' className should be in list className
        :return: in neighbors' nodes and links
        """
        query = f"""
            select
                *
            from
                in({self.database_name}.{self.graph_name}, {nodeIds}, 1)
            {f"where vertexProperty(edge.2, 'className') in {className}" if className else ""}
        """
        # print("%s %s" % ("select_in_by_id", query))
        return self.get_nodes_and_links(query)

    def select_out_by_id(self, nodeIds: list, className: list = None) -> dict:
        """
        select out neighbors from nodeIds
        :param nodeIds: a list of nodeId
        :param className: if not None, neighbors' className should be in list className
        :return: out neighbors' nodes and links
        """
        query = f"""
            select
                *
            from
                out({self.database_name}.{self.graph_name}, {nodeIds}, 1)
            {f"where vertexProperty(edge.2.2, 'className') in {className}" if className else ""}
        """
        # print("%s %s" % ("select_out_by_id", query))
        return self.get_nodes_and_links(query)

    def select_common_neighbor_by_id(self, nodeIds: list, className: list = None) -> dict:
        """
        select common neighbor of given nodeIds (ignore the direction of edge).
        :param nodeIds: a list of nodeId
        :param className: if not None, neighbors' className should be in list className
        :return: common neighbors' nodes and links
        """
        query = f"""
            select 
                * 
            from 
                commonneighbors({self.database_name}.{self.graph_name},{nodeIds})
            {f"where vertexProperty(edge.2.2, 'className') in {className}" if className else ""}                
        """
        # print("%s %s" % ("select_common_neighbor_by_id", query))
        return self.get_nodes_and_links(query)

    def select_path(self, start_node: str, end_node: str, step_num=None) -> dict:
        """
        select path , including from start_node to end_node, and from end_node to start_node
        :param start_node: one vertex id
        :param end_node: the other one vertex id
        :param step_num: the length of the path. if None, all paths (ignore length) could be selected
        :return: paths' nodes and links
        """
        query = f"""
            select
                *,
                vertexProperty(e.1, 'meta_type') as from_meta_type,
                vertexProperty(e.2, 'meta_type') as to_meta_type
            from
                {f"path({self.event_graph_database_name}.{self.event_graph_graph_name}, v('{start_node}'), v('{end_node}'), {step_num})" if step_num else
        f"path({self.event_graph_database_name}.{self.event_graph_graph_name}, v('{start_node}'), v('{end_node}'))"}
            union all
            select
                *,
                vertexProperty(e.1, 'meta_type') as from_meta_type,
                vertexProperty(e.2, 'meta_type') as to_meta_type
            from
                {f"path({self.event_graph_database_name}.{self.event_graph_graph_name}, v('{end_node}'), v('{start_node}'), {step_num})" if step_num else
        f"path({self.event_graph_database_name}.{self.event_graph_graph_name}, v('{end_node}'), v('{start_node}'))"}
        """
        # print("%s %s" % ("select_path", query))
        return self.get_nodes_and_links(query)

    def select_edges_inside_nodes(self, nodeIds: list) -> dict:
        """
        select edges between given nodes
        :param nodeIds: a list of nodeId
        :return: nodes and links between these nodes
        """
        query = f"""
            select
                *,
                key(e) as __e, 
                vertexProperty(e.1, 'meta_type') as from_meta_type, 
                vertexProperty(e.2, 'meta_type') as to_meta_type, 
                vertexProperty(e.1, 'Entity_type') as from_entity_type, 
                vertexProperty(e.2, 'Entity_type') as to_entity_type 
            from
                edge({self.database_name}.{self.graph_name})
            where
                __e.1.1 in {f"({str(nodeIds)[1:-1]})"} and
                __e.2.1 in {f"({str(nodeIds)[1:-1]})"}
        """
        # print("%s %s" % ("select_edges_inside_nodes", query))
        return self.get_nodes_and_links(query)

    def select_edges_between_two_groups(self, nodeIds1: list, nodeIds2: list) -> dict:
        """
        select edges between two groups of nodeIds
        :param nodeIds1: a list of nodeId
        :param nodeIds2: another list of nodeId
        :return: the input nodes, and links between these two groups
        """
        query = f"""
            select
                *
            from
                edge({self.database_name}.{self.graph_name})
            where
                __e.1.1 in {f"({str(nodeIds1)[1:-1]})"} and
                __e.2.1 in {f"({str(nodeIds2)[1:-1]})"}
                or
                __e.1.1 in {f"({str(nodeIds2)[1:-1]})"} and
                __e.2.1 in {f"({str(nodeIds1)[1:-1]})"}
        """
        # print("%s %s" % ("select_edges_between_two_groups", query))
        return self.get_nodes_and_links(query)

    def select_related_out(self, nodeIds: list, type_label: str = None):
        query = f"""
            select
                *,
                key(e) as edge,
                vertexProperty(e.1, 'meta_type') as from_meta_type,
                vertexProperty(e.2, 'meta_type') as to_meta_type,
                vertexProperty(e.1, 'Entity_type') as from_entity_type,
                vertexProperty(e.2, 'Entity_type') as to_entity_type
            from
                out({self.event_graph_database_name}.{self.event_graph_graph_name}, v({nodeIds}), 1)
            {f"where vertexProperty(e.2, 'meta_type') = '{type_label}'" if type_label else ""}"""
        # print("%s %s" % ("select_related_out", query))
        return self.post_related(query)

    def short_path_str(self, start_node: str, end_node: str, step: str):
        query = f"""
            select 
                *,
                vertexProperty(e.1, 'meta_type') as from_meta_type,
                vertexProperty(e.2, 'meta_type') as to_meta_type,
                vertexProperty(e.1, 'Entity_type') as from_entity_type,
                vertexProperty(e.2, 'Entity_type') as to_entity_type  
            from 
                allshortestpath({self.event_graph_database_name}.{self.event_graph_graph_name},v('{start_node}'), v('{end_node}'), {step})
        """
        print("%s %s" % ("short_path_str", query))
        return self.get_nodes_and_links(query)

    def short_path_list(self, start_node: list, end_node: list, step: str):
        query = f"""
            select 
                *,
                vertexProperty(e.1, 'meta_type') as from_meta_type,
                vertexProperty(e.2, 'meta_type') as to_meta_type,
                vertexProperty(e.1, 'Entity_type') as from_entity_type,
                vertexProperty(e.2, 'Entity_type') as to_entity_type  
            from 
                allshortestpath({self.event_graph_database_name}.{self.event_graph_graph_name}, v({start_node}),  v({end_node}), {step})
        """
        # print("%s %s" % ("short_path_list", query))
        return self.get_nodes_and_links(query)

    def select_common(self, nodeIds: list, com_label: str = None) -> dict:
        query = f"""
            select
                *,
                vertexProperty(e.1, 'meta_type') as from_meta_type,
                vertexProperty(e.2, 'meta_type') as to_meta_type,
                vertexProperty(e.1, 'Entity_type') as from_entity_type,
                vertexProperty(e.2, 'Entity_type') as to_entity_type  
            from
                commonneighbors({self.event_graph_database_name}.{self.event_graph_graph_name}, v({nodeIds}), 2)
                {f"where vertexProperty(e.2,'meta_type') = '{com_label}'" if com_label in ['entity', 'event',
                                                                                           'document'] else ""}
        """
        # print("%s %s" % ("select_common", query))
        return self.get_nodes_and_links(query)

    def entity_num(self, entity_id):
        query = f"""
            select
                *
            from
                out({self.event_graph_database_name}.{self.event_graph_graph_name}, '{entity_id}', 1)
            union all
            select
                *
            from
                in({self.event_graph_database_name}.{self.event_graph_graph_name}, '{entity_id}', 1)
        """
        # print("%s %s" % ("entity_num", query))
        return self.get_nodes_and_links(query)

    # 创建graph图集-------------------------------------------------start!

    def creat_vertex_table(self, vertex_table_name, field, databases_name=None):
        if databases_name:
            query_drop_database = f"""
                            drop database if exists {databases_name}
                        """
            query_creat_database = f"""
                create database if not exists {databases_name}
            """
            self.post_sqlGraph(query_drop_database)
            self.post_sqlGraph(query_creat_database)
        query_vertex_table = f"""
            create table if not exists {databases_name}.{vertex_table_name} ({field[0]} String Key) engine=V
        """
        self.post_sqlGraph(query_vertex_table)

    def creat_edge_table(self, databases_name, edge_table_name, field, rely):
        query = f"""
            create table if not exists {databases_name}.{edge_table_name} (
            {field[0]} VS({rely[0]}),
            {field[1]} VD({rely[0]}),
            {field[2]} UInt32
            ) engine=E
        """
        self.post_sqlGraph(query)

    def insert_vertex_table(self, vertex_table_name, idlist):
        val = ['(%s)' % id for id in idlist]
        query_s = f"""
                    insert into {vertex_table_name} values {val}
                """
        query = query_s.replace("[", "").replace("]", "").replace("'(", "('").replace(")'", "')")
        self.post_sqlGraph(query, insert=True)

    def insert_edge_table(self, edge_table_name, idlist):
        val = [(k[0], k[1], k[2]) for k in idlist]
        query_s = f"""
                        insert into {edge_table_name} values {val}
                   """
        query = query_s.replace("[", "").replace("]", "")
        self.post_sqlGraph(query, insert=True)

    def creat_graph(self, graph_name, rely_edge_name):
        query = f"""
            create symmetric graph {graph_name} populate \
            as edgeGroup({rely_edge_name[0]});
        """
        self.post_sqlGraph(query)
        self.post_sqlGraph(f'load property {graph_name}')

    def drop_databases(self, databases_name):
        self.post_sqlGraph(f'drop database {databases_name}')

    # --------------------------------------------------------------end!

    def sql_community(self, graph_name, c_method, column):
        if c_method == "community" or c_method == "louvain":
            query = f""" select community, key(v) from community({graph_name}, {column}) """
        elif c_method == "labelprop":
            query = f""" select community, key(v) from labelprop({graph_name}) """
        elif c_method == "cc":
            query = f""" select id, key(v) from cc({graph_name}) """
        result = self.get_nodes(query)

        nodes = result["data"][0]['nodes']
        group_list = [list(g.values())[0] for g in nodes]
        group_dict = {}
        for group in group_list:
            group_dict[group] = [list(val.values())[1] for val in nodes if list(val.values())[0] == group]
        result["data"][0]['groups'] = [group_dict[x] for x in
                                       sorted(group_dict, key=lambda x: len(group_dict[x]), reverse=True)]

        del result["data"][0]['nodes']
        del result["data"][0]['links']
        return result


if __name__ == '__main__':
    from pprint import pprint

    a = GraphInquiry()
    a.creat_vertex_table("node", ["entity_id", "entity_name"], "CommunityDetection")

    # a.insert_vertex_table("CommunityDetection.node", ['A', 'B', 'C', 'a', 'b', 'c'])
    # a.insert_edge_table("CommunityDetection.edge", {'A': 'a', 'B': 'b', 'C': 'c'})
    a.creat_graph("CommunityDetection.relationGraph", ["CommunityDetection.edge"])

    # b = a.sql_community("CommunityDetection.relationGraph")
    # print("-----------------b-----------------")
    # pprint(b)

    # a.drop_databases("CommunityDetection")

