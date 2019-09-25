from api.GIS.config import GIS_mgdb_config
from api.GIS.GIS_query.queryMongoDB import QueryMGO as QMGO
from api.Mongo.config_mapping import chinese
# from api.GIS.GIS_query.queryMongoDB import QueryMGO as QMGO

class GIS_Events():
    def __init__(self):
        self.events = []
    
    def addEvents_queryMongoByIds(self,ids):
        qmgo = QMGO()
        _events = qmgo.getEvents('id',ids)
        self.events.extend(_events)

    def addEvents_queryMongoByGeometries(self,Geometries):
        qmgo = QMGO()
        _events = qmgo.getEvents('geometry',Geometries)
        self.events.extend(_events)

    def getEvents(self):
        try:
            assert len(self.events) == 0,"events未赋值！"
            return self.events
        except AssertionError as e:
            print("\n 操作错误：",e)
        


    def getFeatures(self):
        # try:
        #     assert len(self.events) == 0,"events未赋值！"
            featureInfo = {}
            features = []
            for event in self.events:
                QBType = chinese['type'][event['QBName']]
                Param = {
                    "ParamId":event['ParamId'],
                    "QBId":event['QBId'],
                    'QBName':QBType,
                    "heatAttr":event['heatAttr']
                }
                ident = event['ident']
                location = event['geometry']
                localName = event['localName']
                if(ident in featureInfo):
                    EventArr = featureInfo[ident]['Params']
                    QBTypes = featureInfo[ident]['QBType']
                    if QBType in QBTypes:
                        QBTypes[QBType] = QBTypes[QBType] + 1
                    else:
                        QBTypes[QBType]  = 1
                    EventArr.append(Param)
                else:
                    featureInfo[ident] = {
                        "Params":[Param],
                        "location":location,
                        "localName":localName,
                        "QBType":{}
                    }
                    featureInfo[ident]['QBType'][QBType] = 1
            for k,v in featureInfo.items():
                location = v['location']
                featureId = k
                params = v['Params']
                localname = v['localName']
                QBTypes = v['QBType']
                feature = {
                    "type": "Feature",
                    "id": featureId,
                    "geometry": location,
                    "properties": {
                        'Params':params,
                        'locationName':localname,
                        'selectedNum':len(params),
                        'QBTypes':QBTypes
                    }
                }
                features.append(feature)
            return features
    
    def classifyIdByDB(self,ids):
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
