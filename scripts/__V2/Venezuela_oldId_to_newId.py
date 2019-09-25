import pymongo
import datetime
from pprint import pprint
from api.utils.creat_chart import SSH

from api.Mongo.utility import Mon_tool

class MongoApplication(object):
    def __init__(self, host: str = '10.60.1.140', port: int = 6080,
                 usr: str = "root", pwd: str = "111111"):
        self.mongoclient = pymongo.MongoClient(host, port)
        self.admin = self.mongoclient.admin
        self.admin.authenticate(usr, pwd)
        self.entity = self.mongoclient["QBData"]["entity"]
        self.event = self.mongoclient["QBData"]["events"]
        self.document = self.mongoclient["QBData"]["documents2"]
        self.documents_labeled = self.mongoclient["QBData"]["documents_labeled1"]
        self.documents_humanrights = self.mongoclient["QBData"]["documents_sg_2"]
        self.documents_twitter = self.mongoclient["SGData"]["social_media"]
        self.m_tool = Mon_tool()
        self.ssh = SSH('10.60.1.142', 'sqlgraph', 'sqlgraph')

    # 通过委内瑞拉老id获取新id
    def select_docID_from_rawID(self, idlist):
        l = []
        for raw_id in idlist:
            doc_id = self.documents_labeled.find({"raw_id": raw_id}, {"_id": 1})
            str_res = [record for record in doc_id]
            l.append(str_res[0]["_id"])
        data = ["{}".format(x) for x in l]
        print("------------------data------------------")
        pprint(data)

    def select_humanrightsID(self):
        doc_ids = self.documents_humanrights.find({}, {"_id": 1})
        str_res = list(doc_ids)
        l = [x["_id"] for x in str_res]
        with open('humanright_ids.txt', 'w') as f:
            for x in l:
                f.write("\"" +x + "\"" + "," + "\n")

    def select_labeled(self):
        doc_ids = self.documents_labeled.find({}, {"_id": 1})
        str_res = list(doc_ids)
        l = [x["_id"] for x in str_res]
        with open('documents_labeled.txt', 'w') as f:
            for x in l:
                f.write("\"" + x + "\"" + "," + "\n")

    def twitter(self):
        doc_ids = self.documents_twitter.find({"$and": [{"topic": {"$ne": "recreation"}}, {"publish_time": {"$gte": 1564674000}}, \
                                     {"publish_time": {"$lte": 1567265970}}]}, {"_id": 1})
        str_res = list(doc_ids)
        l = [x["_id"] for x in str_res]
        with open('documents_labeled.txt', 'w') as f:
            for x in l:
                f.write("\"" + x + "\"" + "," + "\n")

    # 筛选6月到9月的id
    def select_humanrightsID_time(self):
        doc_ids = self.documents_humanrights.find({"$and": [{"publish_time": {"$gte": 1559317200}}, \
                                     {"publish_time": {"$lte": 1568043600}}, {"site_name": {"$ne": ""}}]},
                                    {"_id": 1})
        str_res = list(doc_ids)
        l = [x["_id"] for x in str_res]
        with open('humanright_ids.txt', 'w') as f:
            for x in l:
                f.write("\"" +x + "\"" + "," + "\n")

# 委内瑞拉老id
idlist = [
"5c6c9a9c9c2b888d775948ec",
"5c63c2829c2b888d83ba7550",
"5c6b49d65ee5d656ce922ebd",
"5c6c713a5ee5d656cdf3f944",
"5c645d329c2b888d810f5b49",
"5c65687b9c2b888d83ba770f",
"5c6bf2a55ee5d656cf7c7e01",
"5c6c46649c2b888d7abb23ca",
"5c6b827f5ee5d656d02df13b",
"5c6c008d5ee5d656cdf3f8f4",
"5c65c4ed5ee5d656ce922b5e",
"5c6b65509c2b888d83ba7ca6",
"5c6514c15ee5d656ce922ac3",
"5c6bf2965ee5d656d02df14c",
"5c65aed59c2b888d77594816",
"5c6ce61e9c2b888d83ba7e23",
"5c6c9b3d5ee5d656cdf3f958",
"5c6328745ee5d656cdf3f4ea",
"5c64882b5ee5d656ce922a69",
"5c6e72dc5ee5d656ce9230e3",
"5c6cb6bc9c2b888d83ba7ded",
"5c64b1979c2b888d7abb2312",
"5c6b43375ee5d656ce922eb7",
"5c6c0e069c2b888d83ba7d37",
"5c6da69a5ee5d656cdf3f9ef",
"5c65f5d05ee5d656cf7c7c83",
"5c6b2d9d5ee5d656ce922eaa",
"5c6be4865ee5d656ce922f11",
"5c6568949c2b888d775947f7",
"5c6b1fb55ee5d656ce922ea4",
"5c6decbd5ee5d656d02df1f4",
"5c6c7d475ee5d656cf7c7e47",
"5c6c7f1d5ee5d656ce922f90",
"5c6441b45ee5d656cdf3f57a",
"5c6b322e9c2b888d83ba7c72",
"5c6e6d8b9c2b888d83ba7fa6",
"5c6dda7f5ee5d656ce92308e",
"5c6302d49c2b888d83ba747e",
"5c6c00149c2b888d83ba7d2b",
"5c64959a9c2b888d775947ce",
"5c6d569e9c2b888d83ba7e89",
"5c6d97bc9c2b888d83ba7ece",
"5c6360b45ee5d656cf7c7b68",
"5c6b57cd5ee5d656cdf3f8a9",
"5c6dd09d5ee5d656cdf3fa07",
"5c631a785ee5d656ce922942",
"5c63845e5ee5d656ce92299d",
"5c6c0ea75ee5d656ce922f33",
"5c65bcd69c2b888d83ba7772",
"5c6d59975ee5d656ce92301b",
"5c6b57409c2b888d83ba7c9a",
"5c6cfda85ee5d656cdf3f97e",
"5c6c132e9c2b888d83ba7d3f",
"5c63286f5ee5d656ce92294d",
"5c6530cd5ee5d656ce922ad1",
"5c6cc9fe9c2b888d83ba7e05",
"5c6543649c2b888d83ba76e8",
"5c6b660a5ee5d656cdf3f8b2",
"5c6dc7239c2b888d83ba7f0a",
"5c645d5f9c2b888d83ba760b",
"5c6576869c2b888d83ba771f",
"5c645d509c2b888d7abb2302",
"5c6327e69c2b888d83ba74b0",
"5c6cbbee9c2b888d83ba7df6"
]

# '''
# 通过日期获取时间戳的步骤：
# >>> tss1 = '2019-09-09 23:40:00'
# >>> timeArray = time.strptime(tss1, "%Y-%m-%d %H:%M:%S")
# >>> timeStamp = int(time.mktime(timeArray))
# >>> timeStamp
# 1568043600
# '''


if __name__ == '__main__':
    m = MongoApplication()
    # m.select_docID_from_rawID(idlist)
    m.select_humanrightsID_time()
    # m.select_labeled()
    # m.twitter()

