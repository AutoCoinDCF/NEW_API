import os
import sys
sys.path.append("../..")

import datetime
import pymongo
from pandas.io.json import json_normalize
import pandas as pd

class Test():
    """
        This page is used to create a Graph in Sqlgraph which include three kinds of node ----Document, Event and Knowledge. 
    """
    def __init__(self, coll):

        host = '10.60.1.140'
        port = 6080
        usr = 'root'
        pwd = '111111'

        self.mongoclient = pymongo.MongoClient(host, port)
        self.admin = self.mongoclient.admin
        self.admin.authenticate(usr, pwd)
        self.coll = coll
        self.document = self.mongoclient["QBData"]["documents_task"]
    
    def run(self):
        doc_list = list(self.document.find({"task_id": self.coll}))
        if not os.path.exists('./api/fake/fake_data/{}'.format(self.coll)):
            os.makedirs('./api/fake/fake_data/{}'.format(self.coll))
        relation_file = './api/fake/fake_data/{}/set_relation_{}.csv'.format(self.coll, self.coll)
        document_file = './api/fake/fake_data/{}/set_document_{}.csv'.format(self.coll, self.coll)

        # 这里存在问题，第一条数据不显示，从第二条数据开始
        doc_frame = json_normalize(doc_list)
        # Write document
        document = pd.DataFrame(doc_frame, columns=["_id",
                                                 "raw_id",
                                                 "channel",
                                                 "site_name",
                                                 "title.en",
                                                 "publish_time",
                                                 "topic",
                                                 "entity_list",
                                                 "meta_type"])

        document.rename(columns={"_id": "Entity_id"}, inplace=True)
        document.rename(columns={"title.en": "title"}, inplace=True)
        document["Entity_type"] = "document"
        document.to_csv(document_file, index=False)

        # Generate relation
        relation_list = []
        # entity 和  doc关系
        # for 循环里面的Entity_id是什么意思,没明白,待弄懂
        for index, row in doc_frame.iterrows():
            entity_dict = []
            document_id = row["_id"]
            for sen in row["entity_list"]:
                if "Entity_id" in sen:
                    sen["id"] = sen["Entity_id"]
                if sen["id"] in entity_dict:
                    continue
                else:
                    entity_dict.append(sen["id"])
                    relation_id1 = "{}-{}".format(document_id, sen["id"])
                    relation_list.append([document_id, sen["id"], relation_id1, "include_entity", "include_entity"])

        relation_dataframe = pd.DataFrame(relation_list, columns=["Head_id", "Tail", "id", "relation_id", "type"])

        relation_dataframe.to_csv(relation_file, index=False)
        return


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    test = Test("0aeb6b24_ad19_11e9_b5c3_000c2970dd66")
    test.run()
    end_time = datetime.datetime.now()
    print ("Time:%s"%str((end_time - start_time).seconds))
