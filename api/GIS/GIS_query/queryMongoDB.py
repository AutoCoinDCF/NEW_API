from api.GIS.database.mongoDB import MGO
from api.GIS.database.postGIS import PGO
from api.GIS.config import GIS_mgdb_config
from threading import Thread
import json

class QueryMGO():
    def __init__(self):
        pass

    def getConfigs(self,Type):
        DBConfig = []
        dataBaseConfig = GIS_mgdb_config.dataBaseConfig
        
        for cf in dataBaseConfig:
            ctype = cf['type']
            if ctype == Type:
                DBConfig.append(cf)
        return DBConfig

    def getRowsByIds(self, dbconfig, ids, Rows, outField= [],queryField='QBId'): ##查询一张表
        mg = MGO(host=dbconfig['host'], port=dbconfig['port'], user=dbconfig['user'], pwd=dbconfig['pwd'],dbname=dbconfig['dbname'])
        dbname = dbconfig['dbname']
        collname = dbconfig['collName']
        if dbname in GIS_mgdb_config.fieldConfig and collname in GIS_mgdb_config.fieldConfig[dbname]:
            fieldConfig = GIS_mgdb_config.fieldConfig[dbname][collname]
        outfield = {}
        for file in outField:
            dbfile = fieldConfig[file]
            outfield[dbfile] = 1
        QBIdKey = fieldConfig[queryField]
        findObj = {QBIdKey:{'$in':ids}}
        rows = mg.find(collname,findObj,outField = outfield)
        for row in rows:
            Row = {
                "fieldConfig":fieldConfig,
                "row":row
            }
            Rows.append(Row)

    def getEventRowsByGeometries(self, dbconfig, geometries, Rows): ##查询一张表
        mg = MGO(host=dbconfig['host'], port=dbconfig['port'], user=dbconfig['user'], pwd=dbconfig['pwd'],dbname=dbconfig['dbname'])
        dbname = dbconfig['dbname']
        collname = dbconfig['collName']
        fieldConfig = GIS_mgdb_config.fieldConfig[dbname][collname]
        locationListKey = fieldConfig["locationList"]
        geometryKey = fieldConfig["geometry"]
        findOrArr= []
        for geometry in geometries:
            geoObj = json.loads(geometry)
            findO_point = {locationListKey:{'$elemMatch':{geometryKey:{"$within":{"$geometry":geoObj}}}}}
            findOrArr.append(findO_point)
        findObj = {'$or':findOrArr}
        rows = mg.find(collname,findObj)
        for row in rows:
            Row = {
                "fieldConfig":fieldConfig,
                "row":row
            }
            Rows.append(Row)

    def getOrgRowsByGeometries(self, dbconfig, geometries, orgType, Rows):
        mg = MGO(host=dbconfig['host'], port=dbconfig['port'], user=dbconfig['user'], pwd=dbconfig['pwd'],dbname=dbconfig['dbname'])
        dbname = dbconfig['dbname']
        collname = dbconfig['collName']
        fieldConfig = GIS_mgdb_config.fieldConfig[dbname][collname]
        locationListKey = fieldConfig["locationList"]
        TypeKey = fieldConfig["type"]
        findOrArr= []
        for geometry in geometries:
            geoObj = json.loads(geometry)
            findO_point = {locationListKey:{"$within":{"$geometry":geoObj}}}#{locationListKey:{'$elemMatch':{"$within":{"$geometry":geoObj}}}}
            findOrArr.append(findO_point)
        findObj = {'$and':[{'$or':findOrArr},{TypeKey:orgType}]}# {'$or':findOrArr}   
        rows = mg.find(collname,findObj)
        for row in rows:
            Row = {
                "fieldConfig":fieldConfig,
                "row":row
            }
            Rows.append(Row)

    def getParam(self, ident, QBId, index, QBName,heatAttr, geometry,localName):
        Param = {
                "ident":ident,
                "ParamId":QBId+"#"+str(index),
                "QBId":QBId,
                'QBName':QBName,
                "heatAttr":heatAttr,
                'geometry':geometry,
                "localName":localName 
            }
        return Param

    def isIntersert(self,geometry_a,geometry_b):
        isIntersect = False
        pg = PGO()
        withinGeo_a = {}
        withinGeo_b = {}
        if 'crs' in geometry_a:
            withinGeo_a = geometry_a
        else:
            withinGeo_a = {
                "type":geometry_a['type'],
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                },
                "coordinates":geometry_a['coordinates']
            }
        if 'crs' in geometry_b:
            withinGeo_b = geometry_b
        else:
            withinGeo_b = {
                "type":geometry_b['type'],
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                },
                "coordinates":geometry_b['coordinates']
            }
        sql = "select ST_Intersects(ST_GeomFromGeoJSON('%s'),ST_GeomFromGeoJSON('%s'))"%(json.dumps(withinGeo_a),json.dumps(withinGeo_b),)
        result = pg.Intersect(sql)
        if result:
            isIntersect = True
        return isIntersect

    def getEvents(self,Type,param):
        rows = []
        events = []
        DBConfig = self.getConfigs('event')
        if Type == "id":
            threads = [Thread(target=self.getRowsByIds,args=(cf,param,rows)) for  cf in DBConfig]
        else :
            threads = [Thread(target=self.getEventRowsByGeometries,args=(cf,param,rows)) for  cf in DBConfig]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        for Row in rows:
            try:
                fieldConfig = Row["fieldConfig"]
                row= Row["row"]
                print(row['_id'])
                QBIdKey = fieldConfig["QBId"]
                NameKey = fieldConfig["Name"]
                locationListKey = fieldConfig["locationList"]
                geometryKey = fieldConfig["geometry"]
                SubtypeKey = fieldConfig["Subtype"]
                EventAttrKey = fieldConfig["EventAttr"]
                showHeatAttr = fieldConfig["showHeatAttr"]
                EventId = str(row[QBIdKey])
                localName = row[locationListKey][0][NameKey]
                locationlist = row[locationListKey]
                print(locationlist)
                eventType = row[SubtypeKey]
                for index,locationItem in enumerate(locationlist):
                    geometry = locationItem[geometryKey]
                    isIntersect = True
                    if len(geometry['coordinates']) == 0 or geometry['coordinates'][0] == '' or geometry['coordinates'][0] == 360 or geometry['coordinates'][1] == ''or geometry['coordinates'][1] == 360:  #去除坐标有错误的
                        continue
                    #去除locationList中的坐标不在传入的geometry中的
                    if  Type == "geometry":
                        if len(locationlist) > 1:
                            isIntersect = False
                            for geometryp in param:
                                isIntersect = self.isIntersert(geometry,geometryp)
                                if isIntersect:
                                    break
                    if not isIntersect:   #判l断locationlist中的每一个地点是否落在所查询的范围内
                        continue
                    
                    print(geometry)
                    X = str(geometry['coordinates'][0])
                    Y = str(geometry['coordinates'][1])
                    ident = "event&" + X + Y
                    heatAttr = {}
                    print(showHeatAttr)
                    for attr in showHeatAttr:
                        attrname = attr["attrName"]
                        showname = attr["showName"]
                        if attrname in row[EventAttrKey]:
                            heatAttr[showname] = row[EventAttrKey][attrname]
                    event = self.getParam(ident,EventId,index,eventType,heatAttr,geometry,localName)
                    events.append(event)
            except:
                print(row[QBIdKey]+"失败！")
        return events

    def getOrgs(self,queryType,orgType,param):
        rows = []
        orgs = []
        DBConfig = self.getConfigs('org')
        if queryType == "id":
            threads = [Thread(target=self.getRowsByIds,args=(cf,param,rows)) for  cf in DBConfig]
        else :
            threads = [Thread(target=self.getOrgRowsByGeometries,args=(cf,param,orgType,rows)) for  cf in DBConfig]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        for Row in rows:
            try:
                fieldConfig = Row["fieldConfig"]
                row= Row["row"]
                QBIdKey = fieldConfig["QBId"]
                locationListKey = fieldConfig["locationList"]
                locationNameKey = fieldConfig["locationName"]
                showHeatAttr = fieldConfig["showHeatAttr"]
                QBNameKey = fieldConfig["QBName"]
                QBEnNameKey = fieldConfig["QBEnName"]
                TypeKey = fieldConfig["type"]
                locationlist = row[locationListKey]
                EventId = str(row[QBIdKey])
                localName = row[locationNameKey]
                Type = row[TypeKey]
                QBName = row[QBNameKey]
                QBEnName = row[QBEnNameKey]
                identType = ''
                name = QBEnName
                if Type == 'geographic_entity':
                    identType = 'GeoTar'
                else:
                    identType = 'org'
                if QBEnName == '':
                    name = QBName
                # for index,locationItem in enumerate(locationlist):
                #     geometry = locationItem
                #     isIntersect = True
                #     if len(geometry['coordinates']) == 0 or geometry['coordinates'][0] == '' or geometry['coordinates'][1] == '':  #去除坐标有错误的
                #         continue
                #     #去除locationList中的坐标不在传入的geometry中的
                #     if  queryType == "geometry":
                #         if len(locationlist) > 1:
                #             isIntersect = False
                #             for geometryp in param:
                #                 isIntersect = self.isIntersert(geometry,geometryp)
                #                 if isIntersect:
                #                     break
                #     if not isIntersect:   #判l断locationlist中的每一个地点是否落在所查询的范围内
                #         continue
                geometry = locationlist
                
                X = str(geometry['coordinates'][0])
                Y = str(geometry['coordinates'][1])
                ident = identType + "&" + X + Y
                heatAttr = {}
                for attr in showHeatAttr:
                    attrname = attr["attrName"]
                    showname = attr["showName"]
                    if attrname in row[EventAttrKey]:
                        heatAttr[showname] = row[EventAttrKey][attrname]
                org = self.getParam(ident,EventId,0,name,heatAttr,geometry,localName)
                orgs.append(org)
            except:
                print(row[QBIdKey]+"失败！")
        return orgs

    def queryEventIdsByDocIds(self, dbconfig, ids, Rows): ##查询一张表
        mg = MGO(host=dbconfig['host'], port=dbconfig['port'], user=dbconfig['user'], pwd=dbconfig['pwd'],dbname=dbconfig['dbname'])
        dbname = dbconfig['dbname']
        collname = dbconfig['collName']
        if dbname in GIS_mgdb_config.fieldConfig and collname in GIS_mgdb_config.fieldConfig[dbname]:
            fieldConfig = GIS_mgdb_config.fieldConfig[dbname][collname]
        outfield = {}
        outfield[fieldConfig['QBId']] = 1
        queryKey = fieldConfig['DocId']
        findObj = {queryKey:{'$in':ids}}
        rows = mg.find(collname,findObj,outField = outfield)
        for row in rows:
            Row = {
                "fieldConfig":fieldConfig,
                "row":row
            }
            Rows.append(Row)