import networkx as nx
from networkx.algorithms.clique import enumerate_all_cliques


class OperatorGraph():
    def __init__(self):
        pass

    def strong_connected_subgraph(self, from_ids, to_ids, node_num):
        G = nx.Graph(zip(from_ids, to_ids))

        return_from_ids = []
        return_to_ids = []
        for clique in enumerate_all_cliques(G):
            if len(clique) == node_num:
                head, tail = zip(*list(G.subgraph(clique).edges))
                return_from_ids.append(list(head))
                return_to_ids.append(list(tail))
        return return_from_ids, return_to_ids

    def community_detect(self, from_ids, to_ids, community_num):
        G = nx.Graph(zip(from_ids, to_ids))
        communities = [list(G.nodes)]
        while len(communities) != community_num:
            edge = max(nx.edge_betweenness_centrality(G).items(), key=lambda item: item[1])[0]
            G.remove_edge(edge[0], edge[1])
            communities = list(nx.connected_components(G))

        return_from_ids = []
        return_to_ids = []
        for community in communities:
            head, tail = [], []
            if len(community) > 1:
                head, tail = zip(*list(G.subgraph(community).edges))
            else:
                head = tail = community
            return_from_ids.append(list(head))
            return_to_ids.append(list(tail))
        return return_from_ids, return_to_ids

    def node_importance(self, from_ids, to_ids):
        nodes = []
        edges = []
        edge_size = len(from_ids)

        for i in range(edge_size):
            edges.append((from_ids[i], to_ids[i]))

        G = nx.Graph()
        G.add_edges_from(edges)
        node_with_pr = nx.pagerank(G, alpha=0.85)
        result = sorted(node_with_pr.items(), key=lambda x: x[1], reverse=True)
        return result

    def edge_importance(self, from_ids, to_ids):
        nodes = []
        edges = []
        edge_size = len(from_ids)

        for i in range(edge_size):
            edges.append((from_ids[i], to_ids[i]))
        G = nx.Graph()

        G.add_edges_from(edges)
        edge_with_betweeness = nx.edge_betweenness_centrality(G)
        result = sorted(edge_with_betweeness.items(), key=lambda x: x[1], reverse=True)
        return result
