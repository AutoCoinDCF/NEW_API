#!/usr/bin/env python
# coding: utf-8

#%%
from pandas import concat, DataFrame, Index
from tqdm import tqdm, tqdm_notebook
import requests
import csv


#%%
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


#%% 脚本参数
INF = 10**100  # 无穷大
restful_client = Client()  # 用来发sql请求
csv_file_dir = "./csv/"  # csv文件目录
csv_file_name = "KnowledgeGraph_big_table_with_in_out_neighbor.csv"  # csv文件名
database = "KnowledgeGraph"  # 数据库名
graph = "relationGraph" # 图表
edge = "relations" # 边表
img_url_pattern = "http://10.60.1.143/pic_lib/entity/{id}.png"

fetch_all = True  # 是否一次性从数据库中读取所有数据
# 只有在fetch_all = False时，以下两个参数才有用
batch_size = 100  # 每次从sqlgraph取数据的batch size
max_rows = 200  # 取回的数据总量上限（INF为无穷大。可设定为一个较小的值来检验脚本的执行结果）
start = 0


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


#%% 取节点本身属性
print("fetch vertex property")
sql_to_select_vertex_property = f"""
            select 
                *,
                __v.1 as __v
            from 
                vertex({database}.{graph})
            {'' if fetch_all else 'limit {start},{batch_size}'}
            """
response = restful_client.execute(query=sql_to_select_vertex_property.format(start=start, batch_size=batch_size), format="JSON")
all_properties = response.json()["data"]

#%% 取所有in邻居
print("fetch in neighbor")
sql_to_select_in_neighbor = f"""
                    select
                        dst.1 as _id,
                        relation_type,
                        groupArray(src.1) as in_ids,
                        groupArray(in_name) as in_names
                    from
                        (
                        select
                            edge.1 as src,
                            type as relation_type,
                            edge.2 as dst,
                            (
                            case when vertexProperty(src.2, 'chinese_name') != '' 
                            then vertexProperty(src.2, 'chinese_name')
                            else vertexProperty(src.2, 'entity_name')
                            end
                            ) as in_name
                        from
                            out({database}.{graph}, (select __v.1  from vertex({database}.{graph})), 1)
                        )
                    group by
                        _id,
                        relation_type
"""
response = restful_client.execute(query=sql_to_select_in_neighbor.format(start=start, batch_size=batch_size), format="JSON")
all_in_neighbors = response.json()["data"]

#%% 取所有out邻居
print("fetch out neghbor")
sql_to_select_out_neighbor = f"""
                    select
                        src.1 as _id,
                        relation_type,
                        groupArray(dst.1) as out_ids,
                        groupArray(out_name) as out_names
                    from
                        (
                        select
                            edge.1 as src,
                            type as relation_type,
                            edge.2 as dst,
                            (
                            case when vertexProperty(dst.2, 'chinese_name') != '' 
                            then vertexProperty(dst.2, 'chinese_name')
                            else vertexProperty(dst.2, 'entity_name')
                            end
                            ) as out_name
                        from
                            out({database}.{graph}, (select __v.1  from vertex({database}.{graph})), 1)
                        )
                    group by
                        _id,
                        relation_type
"""
response = restful_client.execute(query=sql_to_select_out_neighbor.format(start=start, batch_size=batch_size), format="JSON")
all_out_neighbors = response.json()["data"]


#%% 处理节点本身的属性
print("raw data to DataFrame")
df_all_property = DataFrame(data=all_properties)
df_all_property.drop(columns=useless_vertex_propertys, inplace=True)
df_all_property.rename(columns={"__v":"_id"}, inplace=True)
df_all_property.set_index("_id", inplace=True)
# 添加img
df_all_property["img"] = df_all_property.index.to_series().apply(lambda x: img_url_pattern.format(id=x))
# 处理in
df_all_in = DataFrame(data=all_in_neighbors)
df_all_in.set_index("_id", inplace=True)
# 处理out邻居
df_all_out = DataFrame(data=all_out_neighbors)
df_all_out.set_index("_id", inplace=True); df_all_out.head()


#%% 将节点属性、in邻居、out邻居三张表拼在一起
print("concat three table: vertex property, in neighbor, out neighbor")
big_table = df_all_property.copy()
for df, prefix in zip([df_all_in, df_all_out], ["in_", "out_"]):
    df.columns.name = "ids_or_names"
    pivot = df.pivot(columns="relation_type")
    pivot = pivot.reorder_levels(["relation_type", "ids_or_names"], axis="columns")
    pivot.sort_index(axis="columns", level="relation_type", inplace=True)
    new_columns = pivot.columns.to_series().apply(lambda x: "%s_%s_%s" % (prefix, x[0].replace(" ","_"), x[1].replace(prefix, "")))
    pivot.columns = Index(new_columns)
    big_table = concat([big_table, pivot], axis="columns", sort=False)


#%% 写入csv
print("write big table into csv")
big_table.to_csv(csv_file_dir+csv_file_name, index_label="_id")

print("success!")
