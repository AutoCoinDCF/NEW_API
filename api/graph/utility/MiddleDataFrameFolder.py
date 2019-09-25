from pandas import DataFrame
import pandas as pd
import requests

pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

import api.configs.entity_img as entity_img

from collections import Callable
from ast import literal_eval

from api.configs.MiddleEndConfig import CONFIG
from api.graph.application.config.config_column_mapping import CONFIG_column_mapping
from api.graph.application.config.config_keep_certain_type_links import CONFIG_extend_relation_types
from api.graph.utility.relation_rule.merge_relation import reduction, protogenesis
from api.graph.application.config.config_edge_translate import translate_dict, nodes_translate_dict
from api.graph.application.config.config_direct_to_undirect import undirected_link_types
from api.graph.utility.utility import NestedHelper, Match_list


class MiddleDataFrameFolder(object):
    def __init__(self, code: int = 0, message: str = ""):
        self.code = code
        self.message = message
        self.data = dict()
        self.entity_img = entity_img

    def set_table(self, table_name: str, table_data: DataFrame or list or dict, primary_key: str = None,
                  drop_primary_key_column=True):
        self.data[table_name] = DataFrame(table_data)
        if primary_key:
            self.data[table_name].set_index(keys=primary_key, inplace=True, drop=drop_primary_key_column)
            if not drop_primary_key_column:
                self.data[table_name].index.name = None

    def set_data(self, key: str, value: object):
        self.data[key] = value

    def select_columns(self, table_name: str, columns: list = "*") -> None:
        if not isinstance(self.data[table_name], DataFrame):
            raise TypeError("data '%s' is not a DataFrame" % table_name)
        if self.data[table_name].empty:
            return
        if columns != "*":
            self.data[table_name] = self.data[table_name][columns]

    def rename_columns(self, table_name: str, column_map: dict or tuple or Callable = None):
        if not isinstance(self.data[table_name], DataFrame):
            raise TypeError("data '%s' is not a DataFrame" % table_name)
        if self.data[table_name].empty:
            return

        if not column_map:
            return

        if isinstance(column_map, tuple):
            mapper = NestedHelper(CONFIG_column_mapping).deep_get(multi_index=column_map)
        else:
            mapper = column_map

        self.data[table_name].rename(columns=mapper, inplace=True)
        # print("change data[table_name]")
        # print(self.data[table_name])
        # note:if column_map is a dict it's okay to have columns in column_map but not in dataframe

    def to_dict(self):
        def df_to_dict(dataframe: DataFrame):
            if dataframe.index.name is None:  # default index: 0,1,2...
                return dataframe.to_dict(orient='records')
            else:
                return dataframe.reset_index().to_dict(orient='records')

        return {
            "code": self.code,
            "message": self.message,
            "data": [{
                k: df_to_dict(v) if isinstance(v, DataFrame) else v
                for k, v in self.data.items()
            }]
        }


class MiddleDataFrameGraph(MiddleDataFrameFolder):
    def __init__(self,
                 code: int = 0,
                 message: str = "",
                 name: str = "",

                 vertex_data: list = None,  # default: don't set primary_key
                 vertex_primary_key: str = None,

                 edge_data: list = None,
                 edge_primary_key: str = None,  # default: don't set primary_key
                 ):
        super().__init__(code, message)
        self.set_data("name", name)

        def str_to_container(str_or_obj: str or object):
            """
            transform string in database to container,
            for example: "['Q23','Q30']" --> ['Q23','Q30']
            """
            try:
                return literal_eval(str_or_obj)
            except (ValueError, SyntaxError):
                return str_or_obj

        if vertex_data:
            self.set_table("nodes",
                           table_data=vertex_data if code == 0 else None,
                           primary_key=vertex_primary_key,
                           drop_primary_key_column=False)
            self.data["nodes"]: DataFrame = self.data["nodes"].applymap(str_to_container)
        else:
            self.set_table("nodes", table_data=None)

        if edge_data:
            self.set_table("links",
                           table_data=edge_data if code == 0 else None,
                           primary_key=edge_primary_key,
                           drop_primary_key_column=False)
            self.data["links"]: DataFrame = self.data["links"].applymap(str_to_container)
        else:
            self.set_table("links", table_data=None)

    def graph_select_and_rename_columns(self,
                                        vertex_columns: list = "*", vertex_column_map_index: tuple = None,
                                        edge_columns: list = "*", edge_column_map_index: tuple = None) -> None:
        if not self.data["nodes"].empty:
            self.select_columns("nodes", vertex_columns)
            self.rename_columns("nodes", vertex_column_map_index)

        if not self.data["links"].empty:
            self.select_columns("links", edge_columns)
            self.rename_columns("links", edge_column_map_index)

    def rename_column(self):
        if self.data["nodes"].empty:
            return
        self.data["nodes"].rename(columns={"__key": "id"}, inplace=True)
        self.data["links"].rename(columns={"src": "from", "dst": "to"}, inplace=True)

    def add_picture(self, have_img_url=False) -> None:
        if self.data["nodes"].empty:
            return
        img_url_template = CONFIG.GraphAPIConfig.img_url_template
        if not have_img_url:
            nodeIds = self.data["nodes"].index.to_series() if self.data["nodes"].index.name is not None else \
            self.data["nodes"]["id"]
            nodes = nodeIds.copy().to_list()
            types = self.data["nodes"].index.to_series() if self.data["nodes"].index.name is not None else \
            self.data["nodes"]["Entity_type"].to_list()

            # row
            # self.data["nodes"]["img"] = nodeIds.apply(lambda node_id: img_url_template.format(id=node_id))

            # 判断143是否存在这个图片，如不存在赋默认值
            # self.data["nodes"]["img"] = nodeIds.apply(lambda node_id: img_url_template.format(id=node_id) \
            #     if requests.get(img_url_template.format(id=node_id)).status_code != 404 else "default")

            # 判断内存属性是否存在这个图片，如不存在赋默认图片
            self.data["nodes"]["img"] = nodeIds.apply(lambda node_id: img_url_template.format(id=node_id) \
                if node_id in self.entity_img.data["{}".format(node_id[:2])] else \
                "http://10.60.1.140/assets/images/{}.png".format(types[nodes.index(node_id)]))

        self.data["nodes"]["loaded"] = True

    def add_name(self) -> None:
        if self.data["nodes"].empty:
            return
        if "Chinese_name" in self.data["nodes"]:
            func = lambda row: row['Chinese_name'] if row['Chinese_name'] else row['Entity_name']
            self.data["nodes"]["name"] = self.data["nodes"].apply(func, axis="columns")

    def drop_by_type(self, drop_vertex_type: list = None, drop_edge_type: list = None):
        if drop_vertex_type and not self.data["nodes"].empty:
            self.data["nodes"] = self.data["nodes"].loc[
                                 self.data["nodes"]["entity_type"].apply(lambda x: x not in drop_vertex_type), :]
        if drop_edge_type and not self.data["links"].empty:
            self.data["links"] = self.data["links"].loc[
                                 self.data["links"]["type"].apply(lambda x: x not in drop_edge_type), :]

    def to_dict(self, reduce_link=True) -> dict:
        return_dict = super().to_dict()
        if return_dict["data"] and return_dict["data"][0].get("links") is not None and reduce_link:
            return_dict["data"][0]["links"] = reduction(return_dict["data"][0]["links"])
        if return_dict["data"] and return_dict["data"][0].get("links") is not None and not reduce_link:
            return_dict["data"][0]["links"] = protogenesis(return_dict["data"][0]["links"])
        return return_dict

    def separator_to_underline(self):
        if self.data["links"].empty:
            return
        func = lambda x: x.replace(" ", "_").replace("-", "_")
        self.data["links"]["type"] = self.data["links"]["type"].apply(func)

    def table_to_IdList(self, table_name: str):
        if not isinstance(self.data[table_name], DataFrame):
            return
        if self.data[table_name].empty:
            self.data[table_name] = []
            return
        id_list = self.data[table_name]["id"].to_list()
        self.data[table_name] = id_list

    def drop_edge_by_type(self, drop_types: list):
        if self.data["links"].empty:
            return
        self.data["links"].loc[:, :] = self.data["links"].loc[~self.data["links"]["type"].isin(drop_types), :]
        from_nodes, to_nodes = self.data["links"]["from"], self.data["links"]["to"]
        self.data["nodes"].loc[:, :] = self.data["nodes"].loc[
                                       self.data["nodes"]["id"].isin(pd.concat([from_nodes, to_nodes])), :]
        return

    def keep_certain_types_links(self, nodeIds, entity_graph=False, whether_path=False, whether_event=False):
        if self.data["links"].empty:
            return
        nodes, links = self.data["nodes"], self.data["links"]
        if entity_graph:
            nodes["meta_type"] = "entity"
        typed_nodes = nodes.loc[:, :]  # add a column ""vertex type", like 'human', 'organization'... for entity, 'Divorce' ... for event

        def vertex_type(row):
            if row["meta_type"] == 'entity':
                return row["Entity_type"]
            elif row["meta_type"] == 'event':
                return "event"
            elif row["meta_type"] == 'document':
                return 'document'
            else:
                raise TypeError(f"meta_type {row['meta_type']} is not 'entity', 'event' or 'document'")

        typed_nodes["vertex_type"] = nodes.apply(func=vertex_type, axis="columns")
        if not whether_path:
            input_nodes = typed_nodes.loc[typed_nodes["id"].isin(nodeIds), :]
        else:
            input_nodes = typed_nodes.loc[:, :]

        # filter links for each typed vertex
        filtered_links = DataFrame()  # links with certain types
        for name, group in input_nodes.groupby(["meta_type", "vertex_type"]):
            meta_type, vtx_type = name
            for root in ("from", "to"):
                #################################
                # todo: please remove after finish event's config, and use the following code instead
                if meta_type == "event" or whether_event:
                    append_links = links.loc[links[root].isin(group["id"]), :]
                elif meta_type == "entity" and vtx_type == "geographic_entity" or vtx_type == "project":
                    append_links = links.loc[links[root].isin(group["id"]), :]
                else:
                    append_links = links.loc[links[root].isin(group["id"]) &
                                             links["type"].isin(CONFIG_extend_relation_types[meta_type][vtx_type]), :]
                #################################
                # append_links = links.loc[links[root].isin(group["id"]) &
                #                          links["type"].isin(CONFIG_extend_relation_types[meta_type][vtx_type]), :]
                #################################
                filtered_links = filtered_links.append(append_links, ignore_index=True)
        filtered_links.drop_duplicates(subset=["id"], inplace=True)
        # remove nodes of type other
        filtered_links = filtered_links.loc[(filtered_links.to_entity_type != "other")]
        # keep nodes that are links head or tail
        filtered_nodes = nodes.loc[nodes["id"].isin(pd.concat([filtered_links["from"], filtered_links["to"]])), :]
        # filtered_nodes.drop_duplicates(subset=["id"], inplace=True)
        if entity_graph:
            filtered_nodes = filtered_nodes.drop(columns=["meta_type", "vertex_type"])
        self.data["nodes"], self.data["links"] = filtered_nodes, filtered_links

    # def keep_
    def links_translate(self):
        if self.data["links"].empty:
            return
        func = lambda x: translate_dict.get(x) if translate_dict.get(x) is not None else x
        self.data["links"].loc[:, "type"] = self.data["links"].loc[:, "type"].apply(func=func)

    def nodes_translate(self):
        if self.data["nodes"].empty:
            return

        func = lambda x: nodes_translate_dict.get(x.lower()) if not isinstance(x, float) and nodes_translate_dict.get(
            x.lower()) is not None else x
        if "event_subtype" in self.data["nodes"]:
            self.data["nodes"].loc[:, "event_subtype"] = self.data["nodes"].loc[:, "event_subtype"].apply(func=func)
        if "topic" in self.data["nodes"]:
            self.data["nodes"].loc[:, "topic"] = self.data["nodes"].loc[:, "topic"].apply(func=func)

    def links_directed_to_undirected(self):
        if self.data["links"].empty:
            return
        self.data["links"]["direct"] = True
        self.data["links"]["undirected_type"] = self.data["links"]["type"]
        self.data["links"]["direct"] = self.data["links"]["type"].apply(lambda x: x not in undirected_link_types.keys())
        self.data["links"]["undirected_type"] = self.data["links"]["type"].apply(
            lambda x: undirected_link_types.get(x) if undirected_link_types.get(x) is not None else x)

    def relation_name_T(self):
        if self.data["links"].empty:
            return

        def func(x):
            node_ids = x.split("-")
            if len(node_ids[0]) < len(node_ids[1]):
                node_ids[0], node_ids[1] = node_ids[1], node_ids[0]
                return "-".join(node_ids)
            return x

        self.data["links"]["id"] = self.data["links"]["id"].apply(func=func)

    def to_dict_join_link_type_to_node_help(self, nodes, links, on, group, group_columns,
                                            columns, group_links, meta_type):
        data = {}
        math_list = Match_list()
        links: DataFrame = links.join(other=nodes.set_index('id'), on=on)
        for name, group in links.groupby(group):
            node_from = name
            new_nodes = group.loc[:, group_columns].rename(columns=columns)
            new_links = group.reindex(columns=group_links)
            nodes = new_nodes.to_dict(orient="records")
            if meta_type == "entity":
                data[node_from] = {
                    "nodes": nodes,
                    "links": new_links.to_dict(orient="records"),
                    "statistics": math_list.statistics(nodes, "entity_type")
                }

            if meta_type == "event":
                data[node_from] = {
                    "nodes": nodes,
                    "links": new_links.to_dict(orient="records"),
                    "statistics": math_list.statistics(nodes, "event_subtype")
                }

            if meta_type == "document":
                data[node_from] = {
                    "nodes": nodes,
                    "links": new_links.to_dict(orient="records"),
                    "statistics": math_list.statistics(nodes, "topic")
                }
        return data

    def to_dict_join_link_type_to_node(self, type_label):
        nodes: DataFrame = self.data["nodes"].loc[:, :]
        links: DataFrame = self.data["links"].loc[:, :]
        if nodes.empty or links.empty:
            return {
                "code": 0,
                "message": "",
                "data": [{}]}

        data = {}
        if type_label == 'entity':
            group_columns = ["to", "img", "Entity_type", "Entity_name", "Chinese_name", "type", "name", "loaded"]
            columns = {"to": "id", "type": "relation"}
            group_links = ["id", "from", "to", "type", "undirected_type", "direct"]
            data = self.to_dict_join_link_type_to_node_help(nodes, links, on="to", group="from",
                                                            group_columns=group_columns, columns=columns,
                                                            group_links=group_links, meta_type="entity")

        elif type_label == 'event':
            group_columns = ["to", "doc_id", "event_type", "meta_type", "event_subtype",
                             "publish_time", "time_list", "entity_list", "location_list", "Entity_type"]
            columns = {"to": "id", "meta_type": "type"}
            group_links = ["id", "from", "to", "type", "undirected_type", "direct"]
            data = self.to_dict_join_link_type_to_node_help(nodes, links, on="to", group="from",
                                                            group_columns=group_columns, columns=columns,
                                                            group_links=group_links, meta_type="event")

        elif type_label == 'document':
            group_columns = ["to", "channel", "site_name", "title", "publish_time", "topic", "Entity_type", "meta_type"]
            columns = {"to": "id", "meta_type": "type"}
            group_links = ["id", "from", "to", "type", "undirected_type", "direct"]
            data = self.to_dict_join_link_type_to_node_help(nodes, links, on="to", group="from",
                                                            group_columns=group_columns, columns=columns,
                                                            group_links=group_links, meta_type="document")
        return {"code": 0,
                "message": "",
                "data": [data]}

    def creat_links_dataframe(self, all_links, filter_links):
        target = DataFrame()
        for x in all_links:
            target = target.append(filter_links[filter_links["from"].isin([x[0]]) & filter_links['to'].isin([x[1]])])
        cols = ["from", "to", "id", "relation_id", "type", "from_meta_type", "to_meta_type"]
        target = target.ix[:, cols]
        return target

    def fliter_links_column(self):
        if self.data["links"].empty:
            return
        cols = ["from", "to", "id", "relation_id", "type", "from_meta_type", "to_meta_type"]
        self.data["links"] = self.data["links"].ix[:, cols]

    def creat_nodes_dataframe(self, all_links, filter_nodes):
        all_links = all_links.to_dict(orient='list')
        all_links = list(set(all_links.get("from") + all_links.get("to")))
        filter_nodes = filter_nodes.to_dict(orient='records')
        _nodes = [x for x in filter_nodes if x["id"] in all_links]
        dict_nodes = {}
        for z in _nodes[0].keys():
            dict_nodes[z] = [y[z] for y in _nodes]
        return DataFrame(dict_nodes)

    def filter_column(self, start_node: list, end_node: list, typeLabel):
        math_list = Match_list()
        if typeLabel == "all":
            typeLabels = ["entity", "event", "document"]
        else:
            typeLabels = [typeLabel]
        filter_links = self.data["links"].loc[:, :]
        filter_nodes = self.data["nodes"].loc[:, :]
        # filter_links = filter_links.append([
        #                                     {'from': "Q23", 'to': "E78", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'entity', "to_meta_type": 'event'},
        #                                     {'from': "E78", 'to': "Q20", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'event', "to_meta_type": 'entity'},
        #
        #                                     {'from': "Q23", 'to': "D07", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'entity', "to_meta_type": 'document'},
        #                                     {'from': "D07", 'to': "Q20", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'document', "to_meta_type": 'entity'},
        #
        #                                     {'from': "Q23", 'to': "D31", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'entity', "to_meta_type": 'documrnt'},
        #                                     {'from': "D31", 'to': "E99", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'document', "to_meta_type": 'event'},
        #                                     {'from': "E99", 'to': "Q55", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'event', "to_meta_type": 'entity'},
        #                                     {'from': "Q55", 'to': "Q20", "id": "111","relation_id": "a11","relation_name": "aaa", "from_meta_type": 'entity',"to_meta_type": 'entity'}
        # ])
        # filter_nodes = filter_nodes.append([
        #                                     {"id": "E78", "entity_name": "AAA", "chinese_name": "", "meta_type": "event", "entity_type": "", "img": "", "loaded": "true", "name": "AAA"},
        #                                     {"id": "D07", "entity_name": "BBB", "chinese_name": "", "meta_type": "document", "entity_type": "", "img": "", "loaded": "true", "name": "BBB"},
        #                                     {"id": "D31", "entity_name": "CCC", "chinese_name": "", "meta_type": "document", "entity_type": "", "img": "", "loaded": "true", "name": "CCC"},
        #                                     {"id": "E99", "entity_name": "DDD", "chinese_name": "", "meta_type": "event", "entity_type": "", "img": "", "loaded": "true", "name": "DDD"},
        #                                     {"id": "Q55", "entity_name": "EEE", "chinese_name": "", "meta_type": "entity", "entity_type": "", "img": "", "loaded": "true", "name": "EEE"}
        # ])
        filter_links_frist = filter_links[filter_links["from"].isin(start_node) | filter_links['to'].isin(end_node)]
        filter_links_second = filter_links[
            filter_links["from_meta_type"].isin(typeLabels) & filter_links['to_meta_type'].isin(typeLabels)]
        filter_end = pd.concat([filter_links_frist, filter_links_second], axis=0, ignore_index=True).drop_duplicates()

        combination_links = filter_end.loc[:, ["from", "to"]].to_dict(orient='list')
        combination_links_node_check = filter_end.loc[:, ["to", "to_meta_type"]].to_dict(orient='list')
        combination_links_from = combination_links["from"]
        combination_links_to = combination_links["to"]
        combination_links_end = list(zip(combination_links_from, combination_links_to))
        all_links = math_list.recursion_combination_links(combination_links_end, start_node, end_node, typeLabels,
                                                          combination_links_node_check)

        if all_links:
            all_links = self.creat_links_dataframe(all_links, filter_links)
            all_nodes = self.creat_nodes_dataframe(all_links, filter_nodes)
            self.data["links"] = all_links.loc[:, :]
            self.data['nodes'] = all_nodes.loc[:, :]
        else:
            self.data["links"] = DataFrame()
            self.data["nodes"] = DataFrame()
        return self.data
