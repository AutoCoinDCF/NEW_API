from pandas import DataFrame, read_csv
import os
from tqdm import tqdm

meta_column_name = "meta_type"
file_pattern = "./csv/%s.csv"
new_file_pattern = "./new_csv/%s.csv"

tables = {
    "document": ["document"],
    "event": ["event"]
    #"entity": ["entity_all"]
}

for meta_type, table_names in tqdm(tables.items()):
    for table_name in tqdm(table_names):
        print("+++++++++++++")
        print(table_name)
        print("+++++++++++++")
        df = read_csv(file_pattern % table_name,sep = None, error_bad_lines=False)
        if meta_column_name not in df.columns:
            df.loc[:, meta_column_name] = meta_type
            df.to_csv(new_file_pattern % table_name, index=None)
print("success!!")

