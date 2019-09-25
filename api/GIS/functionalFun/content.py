from api.GIS.config import GIS_mgdb_config
from api.GIS.GIS_query.queryMongoDB import QueryMGO as QMGO
from threading import Thread

class GIS_Content():
    def __init__(self,contentIds):
        self.contentIds = contentIds
        self.eventIdsWithDBConfig = self.classifyIdsByDB(contentIds)
        self.EventIds = []

    def relatedEventIds(self):
        rows = []
        eventIds = []
        qmgo = QMGO()
        threads = [Thread(target=qmgo.queryEventIdsByDocIds,args=(ec['config'],ec['ids'],rows)) for  ec in self.eventIdsWithDBConfig]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        for row in rows:
            pass
            QBIdKey = row['fieldConfig']['QBId']
            Id = row['row'][QBIdKey]
            eventIds.append(Id)
        return eventIds

    def classifyIdsByDB(self,ids):
        mapConfig = GIS_mgdb_config.idMapColl
        dbConfig = GIS_mgdb_config.dataBaseConfig
        eventIdsByType = {}
        eventIdsWithDBConfig = []
        for id in ids:
            ident = id[0:8]
            if ident not in mapConfig:
                break
            collName = mapConfig[ident]
            if collName in eventIdsByType:
                eventIdsByType[collName].append(id)
            else:
                eventIdsByType[collName] = [id]

        for dbconfigId,eventIds in eventIdsByType.items():
            dbconfig = {}
            classifyWithDBConfig = {}
            for config in dbConfig:
                if config['id'] == dbconfigId:
                    dbconfig = config
                    break
            classifyWithDBConfig['config'] = dbconfig
            classifyWithDBConfig['ids'] = eventIds
            eventIdsWithDBConfig.append(classifyWithDBConfig)
        return eventIdsWithDBConfig