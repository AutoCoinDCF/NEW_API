import pytest
import pymongo
import typing

from mongoapi import MongoDBHandler
from bson.objectid import ObjectId
from pymongo.results import InsertOneResult, InsertManyResult


class Test():
    """
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
        collection_list = self.handler.client['eventGraph'].list_collection_names()
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
        

        
    
def run():
    test = Test()
    test.create_collection("eventGraph", "eventData")
#    data_list = test.find("nlu", "ParsedData", {"_id": ObjectId("5c4305e75ee5d656ce9213a6")})
    data_list = test.find("nlu", "ParsedData", {})
    for data in data_list:
        doc_id = data["_id"]
        if data.get("_nlu_event") == None:
            continue
        
        event_length = len(data["_nlu_event"])
        nel_length = len(data["_nlu_nel"])
        if event_length != nel_length:
            print('event_length != nel_length')
            continue

        for s_index, sentence in enumerate(data["_nlu_event"]):
            for e_index, event in enumerate(sentence):
                event_data = {}
                event_id = test.generate_eventID(doc_id, s_index, e_index)
                event_data["_id"] = event_id
                event_data["doc_id"] = str(doc_id)
                event_data["event_type"] = event["event_type"]
                event_data["event_subtype"] = event["event_subtype"]
                
                entity_dict = {}
                for entity_link in data["_nlu_nel"][s_index]:
                    [entity_link[2], entity_link[3]]
                    entity_dict[(entity_link[0], entity_link[1])] = [entity_link[2], entity_link[3]]
                
                entity_list = []
                time_list = []
                location_list = []
                for entity in event["entity_list"]:
                    entity_start = entity["argument_start"]
                    entity_length = entity["argument_end"] - entity["argument_start"] + 1
                    link_key = (entity_start, entity_length)
                    # Each entity in entity_list
                    if link_key in entity_dict:
                        each = {}
                        each["id"] = entity_dict[link_key][1]
                        each["name"] = entity_dict[link_key][0]
                        each["role"] = entity["argument_role"]
                        entity_list.append(each)
                # This may be change
                time_list = event["time_list"]
                #location_list = event["location_list"]
                for loc in event["location_list"]:
                    location_list.append(loc["argument_content"])
                
                # Add entity list, time list, location list
                event_data["entity_list"] = entity_list
                event_data["time_list"] = time_list
                event_data["location_list"] = location_list
                test.insert("eventGraph", "eventData", event_data)


if __name__ == "__main__":
    run()
