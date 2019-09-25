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
        collection_list = self.handler.client['humanEventGraph'].list_collection_names()
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
    data_list = test.find("humanEventGraph", "eventData", {})
    doc_list = test.find("nlu", "LabelData", {})
    graph = Graph()
    relation_file = './event/relation.csv'
    entity_file = './event/entity.csv'
    document_file = './event/document.csv'
    event_file = './event/event.csv'
    if not os.path.exists('./event'):
        os.makedirs('./event')

    data_frame = json_normalize(data_list)
    doc_frame = json_normalize(doc_list)
    data_frame.rename(columns={"_id": "entity_id"}, inplace=True)

    # Write event
    event = pd.DataFrame(data_frame, columns=["entity_id",
                                              "doc_id",
                                              "event_type",
                                              "event_subtype",
                                              "event_content",
                                              "time_list",
                                              "entity_list",
                                              "location_list"])
    event["entity_type"] = "event"
    event.to_csv(event_file, index=False)
    # Write document
    document = pd.DataFrame(doc_frame, columns=["_id",
                                             "adp",
                                             "author",
                                             "sent",
                                             "title",
                                             "human_topic",
                                             "url"])
    document.rename(columns={"_id": "entity_id"}, inplace=True)
    document["entity_type"] = "document"
    document.to_csv(document_file, index=False)
    
    # Generate relation
    relation_list = []
    for index, row in data_frame.iterrows():
        relation_id = "{}-{}".format(row["entity_id"], row["doc_id"])
        relation_list.append([relation_id, row["entity_id"], row["doc_id"], "include_event"])
        for entity in row["entity_list"]:
            relation_id = "{}-{}".format(row["entity_id"], entity["id"])
            relation_list.append([relation_id, row["entity_id"], entity["id"], entity["role"]])

            relation_id = "{}-{}".format(row["doc_id"], entity["id"])
            relation_list.append([relation_id, row["doc_id"], entity["id"], "include_entity"])
        #print(row["entity_id"])
    relation_dataframe = pd.DataFrame(relation_list, columns=["relation_id", 
                                                              "start_id",
                                                              "end_id",
                                                              "relation_type"])
         
    relation_dataframe.to_csv(relation_file, index=False)
    return

    


if __name__ == "__main__":
    #es_utils = Es_Utils()
    start_time = datetime.datetime.now()
    run()
    end_time = datetime.datetime.now()
    print("Time:%s"%str((end_time - start_time).seconds))
