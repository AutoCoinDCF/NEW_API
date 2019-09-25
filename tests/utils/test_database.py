import pytest
import pymongo
from api.utils import MongoDBHandler


def test_mongo_handler():
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
    handler = MongoDBHandler(host, port, user, pwd)
    # handler.create('nlu', 'test_collection')
    # handler.rename('nlu', 'test_collection', 'new_collection')
    data = [{'cont': 'test content 1', 'abstr': 'test abstraction 1', '_ch': 1},
            {'cont': 'test content 2', 'abstr': 'test abstraction 2', '_ch': 1},
            {'cont': 'test content 3', 'abstr': 'test abstraction 3', '_ch': 1}]
    print(data)
    assert handler is not None
