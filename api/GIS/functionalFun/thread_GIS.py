from threading import Thread,Lock
from api.GIS.config import GIS_mgdb_config
from api.GIS.database.mongoDB import MGO
import json
from api.GIS.GISStaticsFun import GisStaticsFun
class TheadFun():
    def __init__(self):
        pass
        # self.param = param
    
    def queryQBByIds(self,ids):
        DBConfig = []
        for cf in GIS_mgdb_config.dataBaseConfig:
            ctype = cf['type']
            if ctype == 'event' or ctype == 'org':
                DBConfig.append(cf)
        LocationInfo = {}
        features = []
        event_ids = []
        org_ids = []
        for id in ids:
            if len(id) < 20:
                org_ids.append(id)
            else:
                event_ids.append(id)
        threads = [Thread(target=TheadFun.queryDBById,args=(cf,ids,LocationInfo)) for  cf in DBConfig]
        # threads_org = [Thread(target=TheadFun.queryOrgById,args=(cf,org_ids,LocationInfo)) for  cf in orgDBConfig]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        features = TheadFun.getFeaturesByLocationInfo(LocationInfo)
        return features

    @staticmethod
    def queryDBById(cf, ids, LocationInfo):
        cType = cf['type']
        if cType == "event":
            TheadFun.queryEventById(cf, ids, LocationInfo)
        else:
            TheadFun.queryOrgAndTarById(cf, ids, LocationInfo)
    
    @staticmethod
    def queryOrgAndTarById(cf, ids, LocationInfo):
        mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
        dbName = cf['dbname']
        collName = cf['collName']
        fieldConfig = GIS_mgdb_config.fieldConfig
        fieldconfig = fieldConfig[dbName][collName]
        locationListKey = fieldconfig["locationList"]
        QBIdKey = fieldconfig["QBId"]
        TypeKey = fieldconfig["type"]
        locationNameKey = fieldconfig["locationName"]
        findObj = {QBIdKey:{'$in':ids}}
        rows = mg.find(collName,findObj)
        for row in rows:
            try:
                EventId = str(row[QBIdKey])
                localName = row[locationNameKey]
                locationlist = row[locationListKey]
                Type = row[TypeKey]
                for index,locationItem in enumerate(locationlist):
                    geometry = locationItem
                    X = str(geometry['coordinates'][0])
                    Y = str(geometry['coordinates'][1])
                    ident = "event&" + X + Y
                    heatAttr = GisStaticsFun.getHeatAttr(row,showHeatAttr,EventAttrKey)  ## 获取热力属性
                    Param = TheadFun.getParam(EventId,index,eventType,heatAttr)  ##获取param
                    location = geometry
                    TheadFun.getEventLocationInfo(Param,ident,location,localName,LocationInfo)  ##获取locationinfo
            except:
                print(row["_id"] + "失败！")

    @staticmethod
    def queryEventById(cf, ids, LocationInfo):
        mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
        dbName = cf['dbname']
        collName = cf['collName']
        fieldConfig = GIS_mgdb_config.fieldConfig
        fieldconfig = fieldConfig[dbName][collName]
        locationListKey = fieldconfig["locationList"]
        QBIdKey = fieldconfig["QBId"]
        SubtypeKey = fieldconfig["Subtype"]
        EventAttrKey = fieldconfig["EventAttr"]
        showHeatAttr = fieldconfig["showHeatAttr"]
        findObj = {QBIdKey:{'$in':ids}}
        rows = mg.find(collName,findObj)
        for row in rows:
            try:
                EventId = str(row[QBIdKey])
                localName = row[locationListKey][0]['name']
                locationlist = row[locationListKey]
                eventType = row[SubtypeKey]
                for index,locationItem in enumerate(locationlist):
                    geometry = locationItem['geometry']
                    X = str(geometry['coordinates'][0])
                    Y = str(geometry['coordinates'][1])
                    ident = "event&" + X + Y
                    heatAttr = GisStaticsFun.getHeatAttr(row,showHeatAttr,EventAttrKey)  ## 获取热力属性
                    Param = TheadFun.getParam(EventId,index,eventType,heatAttr)  ##获取param
                    location = geometry
                    TheadFun.getEventLocationInfo(Param,ident,location,localName,LocationInfo)  ##获取locationinfo
            except:
                print(row["_id"] + "失败！")

    def exploreEvents(self,geometryStrArr):
        eventsDBConfig = GIS_mgdb_config.dataBaseConfig['event']
        LocationInfo = {}
        features = []
        threads = [Thread(target=TheadFun.spatialQueryDB,args=(cf,geometryStrArr,LocationInfo)) for  cf in eventsDBConfig]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        features = TheadFun.getFeaturesByLocationInfo(LocationInfo)
        return features
    

    @staticmethod
    def spatialQueryDB(cf,geometryStrArr,LocationInfo):
        mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
        dbName = cf['dbname']
        collName = cf['collName']
        fieldConfig = GIS_mgdb_config.fieldConfig
        fieldconfig = fieldConfig[dbName][collName]
        locationListKey = fieldconfig["locationList"]
        geometryKey = fieldconfig["geometry"]
        QBIdKey = fieldconfig["QBId"]
        SubtypeKey = fieldconfig["Subtype"]
        EventAttrKey = fieldconfig["EventAttr"]
        showHeatAttr = fieldconfig["showHeatAttr"]
        findOrArr = []
        for geometryStr in geometryStrArr:
            geometryObj = json.loads(geometryStr)
            findO_point = {locationListKey:{'$elemMatch':{geometryKey:{"$within":{"$geometry":geometryObj}}}}}
            findOrArr.append(findO_point)
        findObj = {'$or':findOrArr}
        rows = mg.find(collName,findObj)
        for row in rows:
            try:
                EventId = str(row[QBIdKey])
                localName = row[locationListKey][0]['name']
                locationlist = row[locationListKey]
                eventType = row[SubtypeKey]
                for index,locationItem in enumerate(locationlist):
                    geometry = locationItem['geometry']
                    isIntersect = True
                    if len(geometry['coordinates']) == 0 or geometry['coordinates'][0] == '' or geometry['coordinates'][1] == '':  #去除坐标有错误的
                        continue
                    #去除locationList中的坐标不在传入的geometry中的
                    if len(locationlist) > 1:
                        isIntersect = False
                        for geometryStr in geometryStrArr:
                            geometryObj = json.loads(geometryStr)
                            isIntersect = GisStaticsFun.isIntersert(geometry,geometryObj)
                            if isIntersect:
                                break
                    if not isIntersect:   #判l断locationlist中的每一个地点是否落在所查询的范围内
                        continue
                    
                    X = str(geometry['coordinates'][0])
                    Y = str(geometry['coordinates'][1])
                    ident = "event&" + X + Y
                    heatAttr = GisStaticsFun.getHeatAttr(row,showHeatAttr,EventAttrKey)
                    Param = TheadFun.getParam(EventId,index,eventType,heatAttr)
                    location = geometry
                    TheadFun.getEventLocationInfo(Param,ident,location,localName,LocationInfo)
            except:
                print(row["_id"] + "失败！")
    
    @staticmethod
    def getParam(EventId,index,eventType,heatAttr):
        Param = {
                "ParamId":EventId+"#"+str(index),
                "QBId":EventId,
                'QBType':eventType,
                "heatAttr":heatAttr
            }
        return Param

    @staticmethod
    def getEventLocationInfo(Param,ident,location,localName,LocationInfo):
        if(ident in LocationInfo):
            EventArr = LocationInfo[ident]['Params']
            EventArr.append(Param)
        else:
            LocationInfo[ident] = {
                "Params":[Param],
                "location":location,
                "localName":localName 
            }
    
    @staticmethod
    def getFeaturesByLocationInfo(LocationInfo):
        features = []
        for k,v in LocationInfo.items():
            location = v['location']
            featureId = k
            params = v['Params']
            localname = v['localName']
            feature = {
                "type": "Feature",
                "id": featureId,
                "geometry": location,
                "properties": {
                    'Params':params,
                    'locationName':localname,
                    'selectedNum':len(params)
                }
            }
            features.append(feature)
        return features


        ####======================================####
    
