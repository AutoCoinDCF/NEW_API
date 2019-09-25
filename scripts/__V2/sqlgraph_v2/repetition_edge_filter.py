import pandas

row = pandas.read_csv(r'relation_v2.csv',encoding='gbk')

row.drop_duplicates(subset=["Head_id","Tail"], inplace=True)

row.to_csv(r'relation.csv',encoding='gbk', index=False)
