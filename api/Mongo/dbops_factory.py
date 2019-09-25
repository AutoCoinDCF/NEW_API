'''DbOpsFactory: 数据库操作工厂类

@author: shishidun@ict.ac.cn
@last_modified: 2018.06.20
'''

from .mongo_dbops import MongoDbOps


class DbOpsFactory(object):
    @staticmethod
    def get_dbops_instance(db_type, host, port, usr, pwd):
        if db_type == "mongo":
            return MongoDbOps(host, port, usr, pwd)
        else:
            raise NotImplementedError
