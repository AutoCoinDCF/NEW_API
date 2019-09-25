from api.utils.es import es as ES
from api.graph.utility.graph_inquiry import GraphInquiry
from api.graph.utility.restful_executor import Executor

import csv
import json
import pandas as pd
from collections import defaultdict


def new_data_dict(relation_types):
    new_data = dict()
    new_data["entity_id"] = ""
    for rt in relation_types:
        new_data[rt+"_ids"] = []
        new_data[rt+"_names"] = []
    return new_data


sql_to_select_out_neighbor = """
          select
              entity_id,
              relation_type,
              groupArray(out_entity_id) as out_entity_ids,
              groupArray(out_entity_name) as out_entity_names
          from
              (
                  select
                      edge.1.1 as entity_id,
                      vertexProperty(edge.1.2, 'entity_name') as entity_name,
                      edge.2.1 as out_entity_id,
                      vertexProperty(edge.2.2, 'entity_name') as out_entity_name,
                      type as relation_type
                  from
                      out(
                          GSIH.relationGraph,
                          (
                            select
                              __v.1
                            from
                              vertex(GSIH.relationGraph)
                          ),
                          1
                        )
              )
          group by
              entity_id,
              relation_type
          order by
              entity_id,
              relation_type
          """

sql_to_select_relation_types = """
          select
            type as link_type
          from
            GSIH.relations
          group by
            link_type
          """

sql_to_select_all_entity_id = """
          select
              __v.1 as entity_id
          from
              vertex(GSIH.relationGraph)
          """

restful_client = Executor(database_name="GSIH")

response = restful_client.execute(query=sql_to_select_out_neighbor, format="JSON")
all_out_neighbors = response.json()["data"]
print("neighbors are selected from sqlgraph")

response = restful_client.execute(query=sql_to_select_relation_types, format="JSON")
relation_types = [data["link_type"] for data in response.json()["data"]]

response = restful_client.execute(query=sql_to_select_all_entity_id, format="JSON")
entity_ids = [data["entity_id"] for data in response.json()["data"]]

big_table_dict = {eid: new_data_dict(relation_types) for eid in entity_ids}
for data in all_out_neighbors:
    big_table_dict[data["entity_id"]]["entity_id"] = data["entity_id"]
    big_table_dict[data["entity_id"]][data["relation_type"] + "_ids"] = data["out_entity_ids"]
    big_table_dict[data["entity_id"]][data["relation_type"] + "_names"] = data["out_entity_names"]
print("big table ready to insert")

es = ES()
index = 0
for entity_id, data in big_table_dict.items():
    es.insert(index="relations", doc_type='relations', _id=entity_id, data=data)
    index += 1
    if index % 10000 == 0:
        print(index)
print("%d nodes has been inserted" % index)

"""
with open("./csv/big_table_with_out_neighbors.csv", 'w') as f:
    writer = csv.DictWriter(f, list(all_out_neighbors[0].keys()), lineterminator='\n')
    writer.writeheader()
    writer.writerows(all_out_neighbors)
    print("csv created")
"""
"""
    for index, data in enumerate(all_out_neighbors):
        if data["entity_id"] not in all_out_neighbors:
            new_data = dict()
            already_handled_id.add(data["entity_id"])
            new_data["entity_id"] = data["entity_id"]
            for relation_type in relation_types:
                new_data[relation_type + "_names"] = []
                new_data[relation_type + "_ids"] = []
        new_data[data["relation_type"] + "_ids"] = data["out_neighbor_ids"]
        new_data[data["relation_type"] + "_names"] = data["out_neighbor_names"]
        if index==100:
            break
"""

df = pd.read_csv("./csv/big_table_with_out_neighbors.csv")
pivot = df.pivot("entity_id", "relation_type")
print("success")