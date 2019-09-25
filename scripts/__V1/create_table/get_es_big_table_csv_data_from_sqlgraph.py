import requests


class Client(object):
    def __init__(self, user: str=None, password: str=None, ip: str='10.60.1.143', port: int or str=8123,
                 database_name: str='default'):
        self._config = {
            "user": user,
            "password": password,
            "ip": ip,
            "port": port,
            "database_name": database_name,
        }

    @property
    def _restful_url_prefix(self):
        if self._config["user"] is not None:
            return "http://{user}:{password}@{ip}:{port}/{database_name}/".format(**self._config)
        else:
            return "http://{ip}:{port}/{database_name}/".format(**self._config)

    def execute(self, query, format="Graph"):
        return requests.get(self._restful_url_prefix, params={"query": query + "format %s" % format})

import csv
import json

# 脚本参数
INF = 10**100  # 无穷大
restful_client = Client()  # 用来发sql请求
csv_file_dir = "./csv/"  # csv文件目录
csv_file_name = "KnowledgeGraph_big_table_with_in_out_neighbor.csv"  # csv文件名
database = "KnowledgeGraph"  # 数据库名
img_url_pattern = "http://10.60.1.143/pic_lib/entity/{id}.png"

fetch_all = True  # 是否一次性从数据库中读取所有数据
# 只有在fetch_all = False时，以下两个参数
# 才有用
batch_size = 100  # 每次从sqlgraph取数据的batch size
max_rows = 200  # 取回的数据总量上限（INF为无穷大。可设定为一个较小的值来检验脚本的执行结果）

# 数据库的graph中，所有vertex共有的属性
vertex_propertys = [
    "entity_name",
    "chinese_name",
    "entity_type",
    "birth_name",
    "name_in_native_language",
    "date_of_birth",
    "date_of_death",
    "floruit",
    "image",
    "height",
    "mass",
    "email",
    "nickname",
    "twitter_username",
    "facebook_id",
    "instagram_username",
    "official_website",
    "official_blog",
    "population",
    "coordinate_location",
    "area",
    "coordinates_of_northernmost_point",
    "coordinates_of_southernmost_point",
    "coordinates_of_westernmost_point",
    "coordinates_of_easternmost_point",
    "coat_of_arms_image",
    "flag_image",
    "central_government_debt_as_a_percent_of_GDP",
    "gini_coefficient",
    "top_level_internet_domain",
    "human_development_index",
    "inception",
    "logo_image",
    "employees",
    "native_label",
    ]

# 查出vertex属性后不需要用到的属性
useless_vertex_propertys = {
    "image",
    "flag_image",
    "logo_image",
}

# 控制csv中每一条数据需要哪些列
def new_data_dict(vertex_propertys: list or set, relation_types: list or set):
    new_data = dict()
    new_data["_id"] = ""
    new_data["img"] = ""
    # 点本身的属性
    for vp in vertex_propertys:
        new_data[vp] = ""
    # 点的邻居
    for rt in relation_types:
        new_data["out__"+rt+"_ids"] = []
        new_data["out__"+rt+"_names"] = []
        new_data["in__"+rt+"_ids"] = []
        new_data["in__"+rt+"_names"] = []
    return new_data


# 查询sqlgraph的图谱中边的type总共都有哪些
sql_to_select_relation_types = f"""
          select
            type as link_type
          from
            {database}.relations
          group by
            link_type
          """
response = restful_client.execute(query=sql_to_select_relation_types, format="JSON")
relation_types = [data["link_type"].replace(" ", "_") for data in response.json()["data"]]


# 查询邻居,以及vertex的全部属性的sql模板
"""
此sql的解释：从内层select到外层select：
1.选出relationGraph的所有vertex的entity_id
2.选出每个entity的出去的邻居
3.选出每个源entity的每个出邻居类型、邻居id、邻居名字（有chinese_name就用chinese_name，否则用entity_name）
4.按每个源entity_id,relation_type对邻居id、邻居名字聚合，得到每个entity、每个relation_type下的邻居id数组、邻居名字数组
5.按每个源entity_id 对relation_type、邻居id数组、邻居名字数组聚合，得到每个entity的relation_type数组、邻居id数组的数组、邻居名字数组的数组
6.聚合邻居做完后，选出每个entity的全部vertexProperty加入到表中
最终得到的表：
_id， relation_type数组，邻居节点id数组的数组，邻居节点name数组的数组，节点属性1，...，节点属性n
"""
sql_to_select_vertex_property_and_out_neighbor = f"""
            select 
                __src.1 as _id,
                relation_types,
                out_entity_ids_of_each_relation_type,
                out_names_of_each_relation_type,
                {','.join(["vertexProperty(__src.2, '{vp}') as {vp}".format(vp=vp) for vp in vertex_propertys])}
            from 
                (
                select
                    __src,
                    groupArray(relation_type) as relation_types,
                    groupArray(out_entity_ids) as out_entity_ids_of_each_relation_type,
                    groupArray(out_names) as out_names_of_each_relation_type
                from
                    (
                    select
                        __src,
                        relation_type,
                        groupArray(out_entity_id) as out_entity_ids,
                        groupArray(out_name) as out_names
                    from
                        (
                        select
                            edge.1 as __src,
                            type as relation_type,
                            edge.2.1 as out_entity_id,
                            (
                            case when vertexProperty(edge.2.2, 'chinese_name') != '' 
                            then vertexProperty(edge.2.2, 'chinese_name')
                            else vertexProperty(edge.2.2, 'entity_name')
                            end
                            ) as out_name
                        from
                            out(
                                {database}.relationGraph,
                                (
                                  select
                                    __v.1
                                  from
                                    vertex({database}.relationGraph)
                                ),
                                1
                              )
                            )
                    group by
                        __src,
                        relation_type
                    )
                group by
                    __src
                )
            order by
                _id
            {'' if fetch_all else 'limit {start},{batch_size}'}
            """

sql_to_select_in_neighbor = f"""
            select 
                __dst.1 as _id,
                relation_types,
                in_entity_ids_of_each_relation_type,
                in_names_of_each_relation_type,
                {','.join(["vertexProperty(__dst.2, '{vp}') as {vp}".format(vp=vp) for vp in vertex_propertys])}
            from 
                (
                select
                    __dst,
                    groupArray(relation_type) as relation_types,
                    groupArray(in_entity_ids) as in_entity_ids_of_each_relation_type,
                    groupArray(in_names) as in_names_of_each_relation_type
                from
                    (
                    select
                        __dst,
                        relation_type,
                        groupArray(in_entity_id) as in_entity_ids,
                        groupArray(in_name) as in_names
                    from
                        (
                        select
                            edge.2 as __dst,
                            type as relation_type,
                            edge.1.1 as in_entity_id,
                            (
                            case when vertexProperty(edge.1.2, 'chinese_name') != '' 
                            then vertexProperty(edge.1.2, 'chinese_name')
                            else vertexProperty(edge.1.2, 'entity_name')
                            end
                            ) as in_name
                        from
                            in(
                                {database}.relationGraph,
                                (
                                  select
                                    __v.1
                                  from
                                    vertex({database}.relationGraph)
                                ),
                                1
                              )
                            )
                    group by
                        __dst,
                        relation_type
                    )
                group by
                    __dst
                )
            order by
                _id
            {'' if fetch_all else 'limit {start},{batch_size}'}
            """

useful_vertex_propertys = set(vertex_propertys) - set(useless_vertex_propertys)

# 查询每个点的邻居，并写入csv
with open(csv_file_dir+csv_file_name, 'w') as f:
    writer = csv.DictWriter(f, list(new_data_dict(useful_vertex_propertys, relation_types).keys()), lineterminator='\n')
    writer.writeheader()
    print("creating csv")
    start = 0

    # 查询每个entity都有哪些邻居，按relation type进行聚合，相同relation type的邻居聚合为一个list
    # 只统计每个entity出去的relation
    while True:
        # 获取出邻居和节点属性
        response = restful_client.execute(
            query=sql_to_select_vertex_property_and_out_neighbor.format(start=start, batch_size=batch_size),
            format="JSON")
        all_out_neighbors_and_properties = response.json()["data"]
        # 获取入邻居
        response = restful_client.execute(
            query=sql_to_select_in_neighbor.format(start=start, batch_size=batch_size),
            format="JSON")
        all_in_neighbors_and_properties = response.json()["data"]
        print("%d data has been fetched from sqlgraph" % (start + len(all_out_neighbors_and_properties)))
        data_dict = {}

        # 将all_out_neighbors "转置"，得到每个entity对应的每种relation的邻居list
        # 处理节点属性和out邻居
        for data in all_out_neighbors_and_properties:
            entity_data = new_data_dict(useful_vertex_propertys, relation_types)
            data_dict[data["_id"]] = entity_data
            entity_data["_id"] = data["_id"]
            entity_data["img"] = img_url_pattern.format(id=data["_id"])
            # 添加entity本身的属性
            for vp in useful_vertex_propertys:
                entity_data[vp] = data[vp]
            # 添加作为属性的out relation
            for relation, oeid, oname in zip(data["relation_types"],
                                             data["out_entity_ids_of_each_relation_type"],
                                             data["out_names_of_each_relation_type"],):
                entity_data["out__" + relation.replace(" ", "_") + "_ids"] = oeid
                # 如果有中文名就用中文名，否则用实体名
                entity_data["out__" + relation.replace(" ", "_") + "_names"] = oname
            data_dict[data["_id"]] = entity_data

        # 处理in邻居
        for data in all_in_neighbors_and_properties:
            try:
                entity_data = data_dict[data["_id"]]
            except KeyError:
                # 这个点只有入边没有出边，因此在添加vertex属性和out邻居时没有产生这个点的数据
                entity_data = new_data_dict(useful_vertex_propertys, relation_types)
                data_dict[data["_id"]] = entity_data
                entity_data["_id"] = data["_id"]
                entity_data["img"] = img_url_pattern.format(id=data["_id"])
                # 添加entity本身的属性
                for vp in useful_vertex_propertys:
                    entity_data[vp] = data[vp]
            # 添加作为属性的in relation
            for relation, ieid, iname in zip(data["relation_types"],
                                             data["in_entity_ids_of_each_relation_type"],
                                             data["in_names_of_each_relation_type"], ):
                entity_data["in__" + relation.replace(" ", "_") + "_ids"] = ieid
                # 如果有中文名就用中文名，否则用实体名
                entity_data["in__" + relation.replace(" ", "_") + "_names"] = iname
        # 将此轮获取到的数据写入csv
        entity_rows = [row for key, row in data_dict.items()]
        writer.writerows(entity_rows)
        print("%d data has been written into csv" % (start + len(all_out_neighbors_and_properties)))
        # 是否跳出
        start += batch_size
        if fetch_all or len(all_out_neighbors_and_properties) == 0 or start >= max_rows:
            break
    print("csv created success")
