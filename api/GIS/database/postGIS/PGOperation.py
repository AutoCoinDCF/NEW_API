import psycopg2

class PGO:
    """ PGO (PostGISOperation),操作postgis数据库 """
    def __init__(self, host='10.60.1.142', port='5432', user='postgres', pwd='example', dbname='qbsys_geo'):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.dbname = dbname

    @staticmethod
    def connectPG(host, port, user, pwd, dbname):
        try:
            conn = psycopg2.connect(database=dbname, user=user, password=pwd, host=host, port=port)
            #cur = conn.cursor()
            return conn 
        except:
            print("连接数据库" + dbname + "出错，未连接成功！")

    def select(self,selectSql):
        try:
            myconn = PGO.connectPG(self.host, self.port, self.user, self.pwd, self.dbname)
            mycur = myconn.cursor()
            mycur.execute(selectSql)
            rows=mycur.fetchall()
            return rows
        except:
            print('查询数据库' + self.dbname + '失败！')
        finally:
            mycur.close()
            myconn.close()

    def selectOne(self,selectSql):
        try:
            myconn = PGO.connectPG(self.host, self.port, self.user, self.pwd, self.dbname)
            mycur = myconn.cursor()
            mycur.execute(selectSql)
            row=mycur.fetchone()
            return row
        except:
            print('查询数据库失败！')
        finally:
            mycur.close()
            myconn.close()

    def updata(self,updataSql):
        try:
            myconn = PGO.connectPG(self.host, self.port, self.user, self.pwd, self.dbname)
            mycur = myconn.cursor()
            mycur.execute(updataSql)
        except:
            print('操作数据库失败!')
        else:
            print('操作成功')
        finally:
            myconn.commit()
            myconn.close()
        
    def Intersect(self,sql):
        try:
            myconn = PGO.connectPG(self.host, self.port, self.user, self.pwd, self.dbname)
            mycur = myconn.cursor()
            mycur.execute(sql)
            result = mycur.fetchone()
            return result[0]
        except:
            print('查询包含失败！')
        else:
            print('查询包含成功！')
        finally:
            mycur.close()
            myconn.close()
    
    @staticmethod 
    def is_Chinese(word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False
    
    