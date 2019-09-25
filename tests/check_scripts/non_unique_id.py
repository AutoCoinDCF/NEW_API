from pandas import DataFrame, Series, read_csv
from tests.utils.code_timer import code_timer

csv_pwd = "/home/wyz/qb-system/qbapi-dev/scripts/create_table/csv/KnowledgeGraph_big_table_with_in_out_neighbor.csv"

with code_timer("read big table csv:") as timer:
    df = read_csv(csv_pwd)

print(df["_id"].value_counts()[lambda x:x>=2].index)
pass
