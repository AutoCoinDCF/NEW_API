from pymongo import MongoClient, GEO2D


class MGO:

    def __init__(self, host='10.60.1.140', port=6080, user=None, pwd=None, dbname='QBData'):
        # host='10.60.1.140', port='6080', user='root', pwd='111111', dbname='未知'
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.dbname = dbname

    @staticmethod
    def connectMG(host, port, user, pwd, dbname):
        try:
            Client = MongoClient(host, port)
            if (user and pwd):
                Admin = Client.admin
                Admin.authenticate(user, pwd)
            db = Client[dbname]
            return db
        except:
            print("连接数据库" + dbname + "出错，未连接成功！")

    def find(self, collName, findObj, outField = {}):
        try:
            mydb = MGO.connectMG(self.host, self.port, self.user, self.pwd, self.dbname)
            myColl = mydb[collName]
            if outField == {}:
                rows = myColl.find(findObj)
            else:
                rows = myColl.find(findObj,outField)
            return rows
        except:
            print("查询失败！")
        else:
            print("查询成功！")
