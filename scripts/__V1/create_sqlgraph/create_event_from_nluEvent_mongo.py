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

    def generate_eventID(self, doc_id: str, event_id: str) -> str:
        return "{}_d{}".format(doc_id, event_id)
        

        
    
def run():
    test = Test()
    #test.create_collection("humanEventGraph", "eventData")
    test.create_collection("LabeledEventGraph", "eventData")
#    data_list = test.find("nlu", "ParsedData", {"_id": ObjectId("5c4305e75ee5d656ce9213a6")})
    data_list = test.find("nlu", "LabelData", {})
    terr_list = test.find("GlobalTerroris", "QBEvents", {})
    num_event = 0
    num_entity_nel = 0
    num_entity_event = 0
    num_match = 0
    entity_name_dict = {}

    # 暴恐数据
    for event in terr_list:
        event_data = {}
        num_event += 1
        event_data = {}
        doc_id = event["doc_id"]
        print('+++++++++++++++++++++++')
        #print(doc_id)
        #event_id = test.generate_eventID(doc_id, event["_id"])
        event_id = event["_id"]
        event_data["_id"] = event_id
        event_data["doc_id"] = str(doc_id)
        event_data["event_type"] = event["event_type"]
        event_data["event_subtype"] = event["event_subtype"]
        event_data["event_content"] = event["event_content"]
        if "event_translate" in event:
            event_data["event_translate"] = event["event_translate"]
        else:
            event_data["event_translate"] = event["event_content"]
        event_data["event_attribute"] = event["event_attribute"]
        event_data["entity_list"] = event["entity_list"]
        event_data["time_list"] = event["time_list"]
        event_data["location_list"] = event["location_list"]
        event_data["argument_list"] = event["argument_list"]
        event_data["publish_time"] = event["publish_time"]
        test.insert("LabeledEventGraph", "eventData", event_data)



    for data in data_list:
        doc_id = data["_id"]
        if data.get("human_events") == None:
            continue

        entity_name_dict = {}
        for s_index, sentence in enumerate(data["human_nel"]):
            for entity_link in sentence:
                num_entity_nel += 1
                key = str.strip(entity_link["content"]).lower()
                entity_name_dict[key] = [entity_link["beg"], entity_link["end"], entity_link["entity_id"]]


        for e_index, event in enumerate(data["human_events"]):
            num_event += 1
            event_data = {}
            #print('+++++++++++++++++++++++')
            print(doc_id)
            event_id = test.generate_eventID(doc_id, e_index)
            event_data["_id"] = event_id
            event_data["doc_id"] = str(doc_id)
            event_data["event_type"] = event["event_type"]
            event_data["event_subtype"] = event["event_subtype"]
            event_data["event_content"] = event["event_content"]
            event_data["event_translate"] = event["event_content"]
            event_data["event_attribute"] = {"event_attribute": "event_attribute"}
            event_data["publish_time"] = event["publish_time"]
            entity_list, location_list, time_list, argument_list = [], [], [], []
            for event_item in event["entity_list"]:
                num_entity_event += 1
                iflink, entity_id = link(entity_name_dict, event_item['beg'], event_item['end'])
                if iflink:
                    each = {}
                    each["id"] = entity_id
                    each["name"] = event_item['argument_content']
                    each["role"] = str.strip(event_item['argument_role']).lower()
                    entity_list.append(each)
                    num_match += 1
                    print(each)
            # for event_item in event["time_list"]:
            #     num_entity_event += 1
            #     key = str.strip(event_item['argument_content']).lower()
            #     if str.strip(event_item['argument_content']).lower() in entity_name_dict.keys():
            #         each = {}
            #         each["id"] = entity_name_dict[key]
            #         each["name"] = key
            #         each["role"] = str.strip(event_item['argument_role']).lower()
            #         time_list.append(each)
            #         num_match += 1
            #         print('+++++++++++++++++++++++')
            for event_item in event["location_list"]:
                num_entity_event += 1
                key = str.strip(event_item['argument_content']).lower()
                iflink, entity_id = link(entity_name_dict, event_item['beg'], event_item['end'])
                if iflink:
                    each = {}
                    each["id"] = entity_id
                    each["name"] = key
                    each["role"] = str.strip(event_item['argument_role']).lower()
                    location_list.append(each)
                    num_match += 1
                    print(each)
            # for event_item in event["argument_list"]:
            #     num_entity_event += 1
            #     each = {}
            #     each["beg"] = event_item['beg']
            #     each["end"] = event_item['end']
            #     each["name"] = str.strip(event_item['argument_content']).lower()
            #     each["role"] = str.strip(event_item['argument_role']).lower()
            #     argument_list.append(each)
            # Add entity list, time list, location list
            event_data["entity_list"] = entity_list
            event_data["time_list"] = event["time_list"]
            event_data["location_list"] = location_list
            event_data["argument_list"] = event["argument_list"]
            test.insert("LabeledEventGraph", "eventData", event_data)
    print("Total Event number is {0}".format(num_event))
    print("Entity Number in human_nel is {0}".format(num_entity_nel))
    print("Entity Number in Event Argument List is {0}".format(num_entity_event))
    print("Event and Entity Matching Number is {0}".format(num_match))


def link(entity_dict: dict, beg: int, end: int):

    for key, value in entity_dict.items():
        entity_beg = value[0]
        entity_end = value[1]
        entity_id = value[2]
        # 如果两个区间有重合则是link的
        if ((beg <= entity_end) and (beg >= entity_beg)) or ((end <= entity_end) and (end >= entity_beg)):
            return True, entity_id
    else:
        return False, ""


if __name__ == "__main__":
    run()
