import os
import sys
sys.path.append("../..")

import datetime

import pytest
import pymongo
import typing
from pandas.io.json import json_normalize  
import pandas as pd

import requests
from mongoapi import MongoDBHandler
from pymongo.results import InsertOneResult, InsertManyResult




class Test():
    """
        This page is used to create a Graph in Sqlgraph which include three kinds of node ----Document, Event and Knowledge. 
    """
    def __init__(self):
        
        host = '10.60.1.140'
        port = 6080
        user = 'root'
        pwd = '111111'
    
        with pytest.raises(pymongo.errors.ServerSelectionTimeoutError):
            wrong = '1.1.1.1'
            _ = MongoDBHandler(wrong, port, user, pwd, serverSelectionTimeoutMS=5000)
        with pytest.raises(pymongo.errors.OperationFailure):
            wrong = 'roottt'
            _ = MongoDBHandler(host, port, wrong, pwd)
    
        self.handler = MongoDBHandler(host, port, user, pwd)

    def create_collection(self, databse: str, collection: str, **kwargs):
        """
        Create a new collection in this database if this collection
        is not exists.
    
        :param database: Database name.
        :param name: Collection name.
        :param kwargs: Additional parameters for :meth:`create_collention`.
        """
        collection_list = self.handler.client['QBData'].list_collection_names()
        if collection not in collection_list:
            self.handler.create(databse, collection)

    def find(self, database: str, collection: str,
             filters: typing.Optional[dict], **kwargs) -> list:
        """ 
        Find document in specific collection.

        :param database: Database name.
        :param collection: Collection name.
        :param filters: Optional, a dict specifying elements which
         must be present for a document to be included in the result set.
        :param kwargs: Additional variables can be passed to :meth:`find`.
        :return: An instance of :class:`Cursor`.
        
        """
        data = self.handler.find(database, collection, filters)
        return data
        
    def find_one(self, database: str, collection: str,
             filters: typing.Optional[dict], **kwargs) -> list:
        """ 
        Find document in specific collection.

        :param database: Database name.
        :param collection: Collection name.
        :param filters: Optional, a dict specifying elements which
         must be present for a document to be included in the result set.
        :param kwargs: Additional variables can be passed to :meth:`find`.
        :return: An instance of :class:`Cursor`.
        
        """
        db = self.handler.client[database]
        col = db[collection]
        return col.find_one()

    def insert(self, database: str, collection: str,
               data: typing.Union[dict, typing.List[dict]],
               **kwargs) -> typing.Union[InsertOneResult, InsertManyResult]:
        """
        Insert document(s) to specific collection.

        :param database: Database name.
        :param collection: Collection name.
        :param data: Document or a iterable of documents to insert.
        :param kwargs: Additional parameters for :meth:`insert_one`
         or :meth:`insert_many`.
        :return: An instance of :class:`InsertOneResult` or
         :class:`InsertManyResult`.
        """
        self.handler.insert(database, collection, data)
        

    def generate_eventID(self, doc_id: str, sentence_id: str,
                         event_id: str) -> str:
        return "{}_d{}_s{}".format(doc_id, sentence_id, event_id)
        

class Graph(object):
    """
    """
    def __init__(self):
        
        host = '10.60.1.143'
        port = 8123
    
        self.url = 'http://{0}:{1}/?query='.format(host, port)
        self.format_json = ' FORMAT JSON;'
        self.format_graph = ' FORMAT Graph;'

    def insert(self, table, values):
        values = str(values)
        values = values.replace("[", "")
        values = values.replace("]", "")
        # print("---------------This is values:", values)
        sql = self.url
        sql += "insert into EntityEventDocGraph.{} values ".format(table)
        sql += values
        data = {'query': sql}
        # result = requests.post(self.url, data)
        result = requests.post(sql)
        result = result.text
        
        
    
def run():
    test = Test()
    data_list_events_labeled = test.find("QBData", "events_labeled", {})
    data_list_events_gtd = test.find("QBData", "events_gtd", {})
    data_list_events_taiwan = test.find("QBData", "events_taiwan", {})
    data_list = data_list_events_labeled + data_list_events_gtd + data_list_events_taiwan
    print("--------data_list----------")
    print(type(data_list))
    print(data_list)
    doc_list_documents_darpa = test.find("QBData", "documents_darpa", {})
    doc_list_documents_gtd = test.find("QBData", "documents_gtd", {})
    doc_list_documents_humanrights = test.find("QBData", "documents_humanrights", {})
    doc_list_documents_labeled = test.find("QBData", "documents_labeled", {})
    doc_list_documents_taiwan = test.find("QBData", "documents_taiwan", {})
    doc_list = doc_list_documents_darpa + doc_list_documents_gtd + doc_list_documents_humanrights + doc_list_documents_labeled + doc_list_documents_taiwan
    print("------------doc_list------------")
    print(doc_list)

    graph = Graph()
    relation_file = './csv/relation.csv'

    document_file = './csv/document.csv'
    event_file = './csv/event.csv'
    if not os.path.exists('./csv'):
        os.makedirs('./csv')

    data_frame = json_normalize(data_list)
    doc_frame = json_normalize(doc_list)
    data_frame.rename(columns={"_id": "entity_id"}, inplace=True)

    # Write event
    event = pd.DataFrame(data_frame, columns=["entity_id",
                                              "doc_id",
                                              "event_type",
                                              "event_subtype",
                                              "event_content.en",
                                              "publish_time",
                                              "time_list",
                                              "entity_list",
                                              "location_list",
                                              "meta_type"])

    event["entity_type"] = "event"
    print("start transport event!")
    event.to_csv(event_file, index=False)
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

    document.rename(columns={"_id": "entity_id"}, inplace=True)
    document["entity_type"] = "document"
    print("start transport document!")
    document.to_csv(document_file, index=False)
    
    # Generate relation
    relation_list = []
    for index, row in data_frame.iterrows():
        # 跳过暴恐数据
        # print(row)
        print(index)
        print(row["entity_id"])
        # print(row["entity_id"])
        # print(row["event_attribute.event_attribute"])
        #if row["event_attribute.event_attribute"] == "event_attribute":
            #continue
            # 如果不是暴恐数据，则
            # event 和 doc的关系
        relation_id1 = "{}-{}".format(row["entity_id"], row["doc_id"])
        relation_id2 = "{}-{}".format(row["doc_id"], row["entity_id"])
        relation_list.append([relation_id1, row["entity_id"], "include_event",  "include_event", row["doc_id"], "event", "document"])
        relation_list.append([relation_id2, row["doc_id"], "include_event", "include_event", row["entity_id"], "document", "event"])
        # entity和 event 关系
        for entity in row["entity_list"]:
            if entity["id"].lower() != "none":
                print(entity["id"])
                relation_id1 = "{}-{}".format(row["entity_id"], entity["id"])
                relation_id2 = "{}-{}".format(entity["id"], row["entity_id"])
                relation_list.append([relation_id1, row["entity_id"], entity["role"], entity["role"], entity["id"], "event", "entity"])
                relation_list.append([relation_id2, entity["id"], entity["role"], entity["role"], row["entity_id"], "entity", "event"])
            # relation_id1 = "{}-{}".format(row["doc_id"], entity["id"])
            # relation_id2 = "{}-{}".format(entity["id"], row["doc_id"])
            # relation_list.append([relation_id1, row["doc_id"],  "include_entity",  "include_entity", entity["id"]])
            # relation_list.append([relation_id2, entity["id"], "include_entity", "include_entity", row["doc_id"]])
        #print(row["entity_id"])
    # entity 和  doc关系
    for index, row in doc_frame.iterrows():
        entity_dict = []
        document_id = row["_id"]
        for sen in row["entity_list"]:
            print("------------sen-------------")
            print(sen)
            if "entity_id" in sen:
                sen["id"] = sen["entity_id"]
            if sen["id"] in entity_dict:
                continue
            else:
                entity_dict.append(sen["id"])
                relation_id1 = "{}-{}".format(document_id, sen["id"])
                relation_id2 = "{}-{}".format(sen["id"], document_id)
                relation_list.append([relation_id1, document_id,  "include_entity",  "include_entity", sen["id"], "document", "entity"])
                relation_list.append([relation_id2, sen["id"], "include_entity", "include_entity", document_id, "entity", "document"])

    relation_dataframe = pd.DataFrame(relation_list, columns=["id", "Head_id", "relation_id", "type", "Tail", "type_from", "type_to"])
         
    relation_dataframe.to_csv(relation_file, index=False)
    return

    


if __name__ == "__main__":
    #es_utils = Es_Utils()
    start_time = datetime.datetime.now()
    run()
    end_time = datetime.datetime.now()
    print ("Time:%s"%str((end_time - start_time).seconds))
