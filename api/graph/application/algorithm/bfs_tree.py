""" algorithm to generate a breadth-first tree of a graph """

from networkx import MultiDiGraph, MultiGraph
from collections import defaultdict


def new_child(nodeId: str, depth: int, node_number_stat: defaultdict):
    child = {"depth": depth, "order": node_number_stat[depth], "id": nodeId, "children": []}
    node_number_stat[depth] += 1
    return child


def do_bfs(already_append: list, graph: MultiGraph, node_dict: dict, depth: int, node_number_stat: defaultdict):
    append = False
    for nbr in graph.neighbors(node_dict["id"]):
        if nbr not in already_append:
            already_append.append(nbr)
            node_dict["children"].append(new_child(nbr, depth + 1, node_number_stat))
            append = True
    if not append:
        return
    for child in node_dict["children"]:
        do_bfs(already_append, graph, child, depth + 1, node_number_stat)
    return


def bfs_tree(nodes: list, edges: list, root_node_id_list: list):
    graph = MultiDiGraph()
    for node in nodes:
        graph.add_node(node)
    for edge in edges:
        graph.add_edge(edge["from"], edge["to"], edge["id"])
    graph = graph.to_undirected()

    # bfs tree
    node_number_stat = defaultdict(lambda: 0)
    # result = [new_child(nodeId=root_node_id, depth=0, node_number_stat=node_number_stat)]
    result = []
    already_append = []
    for root_node_id in root_node_id_list:
        if root_node_id not in already_append:
            already_append.append(root_node_id)
            new_root = new_child(nodeId=root_node_id, depth=0, node_number_stat=node_number_stat)
            result.append(new_root)
            do_bfs(already_append, graph, new_root, depth=0, node_number_stat=node_number_stat)
    # add isolate nodes that can't be reached from root
    # for node in graph.nodes:
    #     if node not in already_append:
    #         result.append(new_child(nodeId=node, depth=0, node_number_stat=node_number_stat))

    # 将没有用到的节点s筛选出来
    nodes = []
    for node in graph.nodes:
        if node not in already_append:
            nodes.append(node)
    return result, nodes
