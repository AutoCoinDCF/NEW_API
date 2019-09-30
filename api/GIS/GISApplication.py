""" Geography Information System API """
from .database.postGIS import PGO
from .database.mongoDB import MGO
from .mapGraph.BezierLine import BezierLine as BL
import json
from bson.objectid import ObjectId
from .GISStaticsFun import GisStaticsFun
import configparser
from threading import Thread,Lock
from .functionalFun.thread_GIS import TheadFun
from .functionalFun.event import GIS_Events
from .functionalFun.org import GIS_Orgs
from .functionalFun.content import GIS_Content
from .config import GIS_pgdb_config
from api.GIS.GIS_query.queryMongoDB import QueryMGO as QMGO


class GISApplication(object):
    def __init__(self):
        self.dataBaseConfig={
            'org':[
                {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'coordinate'}
            ],
            'event':[
                {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'events'}
            ]
        }
        self.fieldConfig = {
            "QBData":{
                "events":{
                    "locationList":"location_list",
                    "geometry":"geometry",
                    "QBId":"_id",
                    "Subtype":"event_subtype"
                }
            }
        }

    def searchLocationName_n(self, localName):
        pg = PGO()
        if (PGO.is_Chinese(localName)):
            rows_countries = pg.select(
                r"SELECT id,country FROM world_states_countries WHERE country ~* '%s';" % (localName))
            rows_provinces = pg.select(
                r"SELECT objectid,enname FROM world_states_provinces WHERE enname ~* '%s';" % (localName))
        else:
            rows_countries = pg.select(
                r"SELECT id,enname FROM world_states_countries WHERE enname ~* '%s';" % (localName))
            rows_provinces = pg.select(
                r"SELECT objectid,name FROM world_states_provinces WHERE name ~* '%s';" % (localName))

        # rows_countries = pg.select(r"SELECT id,country FROM world_states_countries WHERE (country ~* '%s') or (enname ~* '%s');" %(localName,localName))
        # rows_provinces = pg.select(r"SELECT objectid,name FROM world_states_provinces WHERE name ~* '%s';" %(localName))
        suitableLocations = []
        """ suitableLocationO = {} """
        if (rows_provinces==None and rows_countries==None):
            return 'false'
        else:
            if (rows_provinces != None):
                for row in rows_provinces:
                    locN = {
                        "id": str(row[0]) + '_province',
                        "name": row[1].strip()
                    }
                    suitableLocations.append(locN)
            if (rows_countries != None):
                for row in rows_countries:
                    locN = {
                        "id": str(row[0]) + '_country',
                        "name": row[1].strip()
                    }
                    suitableLocations.append(locN)
            data = {
                "code": 0,
                "data": suitableLocations
            }
            return data

    def searchAreaByIds_n(self, aids):
        config = [
            {"tableName":'world_states_countries',"idSign":"world_states_countries_postgis","IdField":"id","queryFields":['id','country','enname'],"type":"country"},
            {"tableName":'world_states_provinces',"idSign":"world_states_provinces_postgis","IdField":"objectid","queryFields":['objectid','name','enname'],"type":"province"}]
        pg = PGO()
        ids = aids
        suitableLocations = []
        for cf in config:
            sids = ",".join([str(id.split(".")[1]) for id in ids if id.split(".")[0] == cf['idSign']])
            queryFields = ",".join(cf['queryFields'])
            sql =  "SELECT " + queryFields + " FROM " + cf['tableName'] +" WHERE " + cf['IdField'] + " in (" + sids + ")"
            rows = pg.select(sql)
            if(rows != None):
                for row in rows:
                    name = ''
                    if row[1] == None:
                        name = row[2]
                    else:
                        name = row[1]
                    locN = {
                        "id":cf['type']  + "." + str(row[0]),
                        "name":name.strip(),
                        "type":cf['type']
                    }
                    suitableLocations.append(locN)
        data = {
            "code":0,
            "data":suitableLocations
        }
        return data

    def exploreGeoTar_n(self, geometry):
        mg = MGO(user='root', pwd='111111')
        collName = 'coordinate'#'Organization'
        geometryStrArr = geometry
        findOrArr = []
        for geometryStr in geometryStrArr:
            geometryObj = json.loads(geometryStr)
            findO = {"location":{"$within":{"$geometry":geometryObj}}}
            findOrArr.append(findO)
        findObj = {'$and':[{'$or':findOrArr},{"Entity_type":"geographic_entity"}]}#{'$or':findOrArr}
        rows = mg.find(collName,findObj)
        features=[]
        Location = {}
        allrows = []
        for row in rows:
            GisStaticsFun.getOrgDictBySearRes(row,Location)

        for k,v in Location.items():
            location = v['location']
            featureId = k
            params = v['Params']
            feature = {
                "type": "Feature",
                "id":featureId,
                "geometry": location,
                "properties": {
                    'Params':params,
                    'selectedNum':len(params)
                }
            }
            features.append(feature)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }

    def exploreOrg_n(self, geometry):
        mg = MGO(user='root', pwd='111111')
        collName = 'coordinate'  # 'Organization'
        geometryStrArr = geometry
        findOrArr = []
        for geometryStr in geometryStrArr:
            geometryObj = json.loads(geometryStr)
            findO = {"location": {"$within": {"$geometry": geometryObj}}}
            findOrArr.append(findO)
        findObj = {'$and':[{'$or':findOrArr},{"Entity_type":"organization"}]}#{'$or': findOrArr}
        rows = mg.find(collName, findObj)
        features = []
        Location = {}
        for row in rows:
            X = str(row['location']['coordinates'][0])
            Y = str(row['location']['coordinates'][1])
            ident = X + Y
            Org = {
                "OrgName": row['Entity_name'],
                "id":row['Entity_id'],
            }
            location = row['location']
            if (ident in Location):
                OrgArr = Location[ident]['Orgs']
                OrgArr.append(Org)
            else:
                Location[ident] = {
                    "Orgs": [Org],
                    "location": location
                }

        for k, v in Location.items():
            location = v['location']
            featureId = k
            orgs = v['Orgs']
            feature = {
                "type": "Feature",
                "id": "org&" + featureId,
                "geometry": location,
                "properties": {
                    'Params': orgs,
                    'selectedNum': len(orgs)
                }
            }
            features.append(feature)
        data = {
            "code": 0,
            "data": {
                'Features': {
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def node2GIS(self, nodeIds):
        data = {
            "code": 0,
            "data": [{
                "eventGeoJson": {
                    "type": "FeatureCollection",
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "EPSG:4326"
                        }
                    },
                    "features": [
                        {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "id": "event_Feature_北京",
                             "coordinates": [116.3809433, 39.9236145]},
                         "properties": {
                             "Params": [{"id": "event_V104", "time": "2002-01-02"},
                                        {"id": "event_V105", "time": "2018-01-03"},
                                        {"id": "event_V102", "time": "2018-01-03"}],
                             "locationName": "北京",
                             "selectedNum": 3
                         }
                         },
                        {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "id": "event_Feature_纽约",
                             "coordinates": [74.0060, 40.7128]},
                         "properties": {
                             "Params": [{"id": "event_V108", "time": "2002-02-02"},
                                        {"id": "event_V109", "time": "2018-02-03"},
                                        {"id": "event_V120", "time": "2018-02-03"}],
                             "locationName": "纽约",
                             "selectedNum": 3
                         }
                         }
                    ]
                }
            }]
        }
        return data

    def exploreEvent_n(self, geometry):
        config=[
            {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'events'},
            ]
        features=[]
        Location = {}
        allrows = []
        for cf in config:
            mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
            collName = cf['collName']
            geometryStrArr = geometry
            findOrArr = []
            for geometryStr in geometryStrArr:
                geometryObj = json.loads(geometryStr)
                #findO_line = {"location_list.from.geometry":{"$within":{"$geometry":geometryObj}}}
                findO_fromLine = {"location_list.from":{'$elemMatch':{'geometry':{"$within":{"$geometry":geometryObj}}}}}
                findO_toLine = {"location_list.to":{'$elemMatch':{'geometry':{"$within":{"$geometry":geometryObj}}}}}
                findO_point = {"location_list.geometry":{"$within":{"$geometry":geometryObj}}}
                findOrArr.append(findO_fromLine)
                findOrArr.append(findO_toLine)
                findOrArr.append(findO_point)
            findObj = {'$or':findOrArr}
            #findObj = {"Entity_id":'Q1065'}
            rows = mg.find(collName,findObj)
            for row in rows:
                allrows.append(row)

        for row in allrows:
            if 'from' in row['location_list'][0].keys():
                froms = row['location_list'][0]['from']
                tos = row['location_list'][0]['to']
                locallineName = '线事件'
                EventId = str(row['_id'])
                linesGeometry = []
                linesName = []
                i = 0
                eventType = row['event_subtype']
                while i < len(froms):
                    fromName = froms[i]['name']
                    toName = tos[i]['name']
                    fromCoor = froms[i]['geometry']['coordinates']
                    toCoor = tos[i]['geometry']['coordinates']
                    bl = BL(fromCoor,toCoor,50)
                    lineGeometry = bl.getBezierPoints()
                    lineName = [fromName,toName]
                    linesGeometry.append(lineGeometry)
                    linesName.append(lineName)
                    i = i + 1
                feature = {
                    "type": "Feature",
                    "id":"event&" + EventId,
                    "geometry": {"type": "MultiLineString","coordinates":linesGeometry},
                    "properties": {
                        'Params':[{'id':EventId,'time':'','eventType':eventType}],
                        'selectedNum':1,
                        'locationName':locallineName
                    }
                }
                features.append(feature)
            else:
                EventId = str(row['_id'])
                localName = row['location_list'][0]['name']
                pointGeometry = row['location_list'][0]['geometry']
                X = str(pointGeometry['coordinates'][0])
                Y = str(pointGeometry['coordinates'][1])
                ident = X + Y
                eventType = row['event_subtype']
                completeEvent = ''
                time = ''
                Event = {
                    "id":EventId,
                    'time':time,
                    'eventType':eventType,
                }
                location = row['location_list'][0]['geometry']
                if(ident in Location):
                    EventArr = Location[ident]['Events']
                    EventArr.append(Event)
                else:
                    Location[ident] = {
                        "Events":[Event],
                        "location":location,
                        "localName":localName
                    }

        for k,v in Location.items():
            location = v['location']
            featureId = k
            events = v['Events']
            localname = v['localName']
            feature = {
                "type": "Feature",
                "id":"event&" + featureId,
                "geometry": location,
                "properties": {
                    'Params':events,
                    'locationName':localname,
                    'selectedNum':len(events)
                }
            }
            features.append(feature)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def getEventByIds_n(self, event_ids):
        config=[
            {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'coordinate'}
            ]
        features=[]
        Location = {}
        allrows = []
        for cf in config:
            mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
            collName = cf['collName']
            ids = event_ids
            findOrArr = []
            for id in ids:
                findO = {"_id":id}
                findOrArr.append(findO)
            findObj = {'$or':findOrArr}
            rows = mg.find(collName,findObj)
            for row in rows:
                allrows.append(row)

        for row in allrows:
            if len(row['location_list']) == 0 or (('from' not in row['location_list'][0]) and len(row['location_list'][0]['geometry']['coordinates']) == 0):
                continue
            if 'from' in row['location_list'][0].keys():
                froms = row['location_list'][0]['from']
                tos = row['location_list'][0]['to']
                locallineName = '线事件'
                EventId = str(row['_id'])
                linesGeometry = []
                linesName = []
                i = 0
                completeEvent = ''
                eventType = row['event_subtype']
                while i < len(froms):
                    fromName = froms[i]['name']
                    toName = tos[i]['name']
                    fromCoor = froms[i]['geometry']['coordinates']
                    toCoor = tos[i]['geometry']['coordinates']
                    bl = BL(fromCoor,toCoor,50)
                    lineGeometry = bl.getBezierPoints()
                    #lineGeometry = [fromCoor,toCoor]
                    lineName = [fromName,toName]
                    linesGeometry.append(lineGeometry)
                    #linesGeometry = lineGeometry
                    linesName.append(lineName)
                    i = i + 1
                feature = {
                    "type": "Feature",
                    "id":"event&" + EventId,
                    "geometry": {"type": "MultiLineString","coordinates":linesGeometry},
                    "properties": {
                        'Params':[{'id':EventId,'time':'','eventType':eventType}],
                        'locationName':locallineName,
                        'selectedNum':1
                    }
                }
                features.append(feature)
            else:
                EventId = str(row['_id'])
                pointGeometry = row['location_list'][0]['geometry']
                localName = row['location_list'][0]['name']
                X = str(pointGeometry['coordinates'][0])
                Y = str(pointGeometry['coordinates'][1])
                ident = X + Y
                arguments = row['argument_list']
                eventType = row['event_subtype']
                relatedEntities = []
                completeEvent = ''
                content = row['event_content']
                time = ''


                Event = {
                    "id":EventId,
                    'time':time,
                    'eventType':eventType
                }
                location = row['location_list'][0]['geometry']
                if(ident in Location):
                    EventArr = Location[ident]['Events']
                    EventArr.append(Event)
                else:
                    Location[ident] = {
                        "Events":[Event],
                        "location":location
                    }

        for k,v in Location.items():
            location = v['location']
            featureId = k
            events = v['Events']
            feature = {
                "type": "Feature",
                "id":"event&" + featureId,
                "geometry": location,
                "properties": {
                    'Params':events,
                    'locationName':localName,
                    'selectedNum':len(events)
                }
            }
            features.append(feature)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def getParamsByIds_n(self, param_ids):
        config=[
            {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'coordinate'},
            {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'events'}
            ]
        features=[]
        Location = {}
        allrows = []
        for cf in config:
            mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
            collName = cf['collName']
            ids = param_ids
            findOrArr = []
            for id in ids:
                findO = {}
                if len(id) < 20:
                    findO = {"Entity_id":id}
                else:
                    findO = {"_id":id}
                findOrArr.append(findO)
            findObj = {'$or':findOrArr}
            rows = mg.find(collName,findObj)
            for row in rows:
                allrows.append(row)

        for row in allrows:

            if 'Entity_id' in row:
                GisStaticsFun.getOrgDictBySearRes(row,Location)
            else:
                if len(row['location_list']) == 0 or ('geometry' not in row['location_list'][0]) or (('from' not in row['location_list'][0]) and len(row['location_list'][0]['geometry']['coordinates']) == 0):
                    continue
                GisStaticsFun.getEventDictBySearRes(row,Location)

        for k,v in Location.items():
            location = v['location']
            featureId = k
            params = v['Params']
            feature = {
                "type": "Feature",
                "id":featureId,
                "geometry": location,
                "properties": {
                    'Params':params,
                    'selectedNum':len(params)
                }
            }
            features.append(feature)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def getOrgByIds_n(self, org_ids):
        mg = MGO(user='root', pwd='111111')
        collName = 'coordinate'#'Organization'
        ids = org_ids
        findOrArr = []
        for id in ids:
            #geometryObj = json.loads(geometryStr)
            findO = {"Entity_id":id}
            findOrArr.append(findO)
        findObj = {'$or':findOrArr}
        #findObj = {"Entity_id":'Q1065'}
        rows = mg.find(collName,findObj)
        features=[]
        Location = {}
        for row in rows:
            X = str(row['location']['coordinates'][0])
            Y = str(row['location']['coordinates'][1])
            ident = X + Y
            Org = {
                "OrgName":row['Entity_name'],
                "id":row['Entity_id'],
            }
            location = row['location']
            if(ident in Location):
                OrgArr = Location[ident]['Orgs']
                OrgArr.append(Org)
            else:
                Location[ident] = {
                    "Orgs":[Org],
                    "location":location
                }

        for k,v in Location.items():
            location = v['location']
            featureId = k
            orgs = v['Orgs']
            feature = {
                "type": "Feature",
                "id":"org&" + featureId,
                "geometry": location,
                "properties": {
                    'Params':orgs,
                    'selectedNum':len(orgs)
                }
            }
            features.append(feature)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

####=================================================####

    def searchLocationName(self, localName):
        pg = PGO()
        if (PGO.is_Chinese(localName)):
            rows_countries = pg.select(
                r"SELECT gid,zhname FROM country_osm WHERE zhname ~* '%s';" % (localName))
            rows_provinces = pg.select(
                r"SELECT gid,zhname FROM province_osm WHERE zhname ~* '%s';" % (localName))
        else:
            rows_countries = pg.select(
                r"SELECT gid,enname FROM country_osm WHERE enname ~* '%s';" % (localName))
            rows_provinces = pg.select(
                r"SELECT gid,enname FROM province_osm WHERE enname ~* '%s';" % (localName))

        # rows_countries = pg.select(r"SELECT id,country FROM world_states_countries WHERE (country ~* '%s') or (enname ~* '%s');" %(localName,localName))
        # rows_provinces = pg.select(r"SELECT objectid,name FROM world_states_provinces WHERE name ~* '%s';" %(localName))
        suitableLocations = []
        """ suitableLocationO = {} """
        if (rows_provinces==None and rows_countries==None):
            return 'false'
        else:
            if (rows_provinces != None):
                for row in rows_provinces:
                    locN = {
                        "id": str(row[0]) + '_province',
                        "name": row[1].strip()
                    }
                    suitableLocations.append(locN)
            if (rows_countries != None):
                for row in rows_countries:
                    locN = {
                        "id": str(row[0]) + '_country',
                        "name": row[1].strip()
                    }
                    suitableLocations.append(locN)
            data = {
                "code": 0,
                "data": suitableLocations
            }
            return data

    def searchAreaByIds(self, aids):
        config = GIS_pgdb_config.dataBaseConfig
        pg = PGO()
        ids = aids
        suitableLocations = []
        for cf in config:
            sids = ",".join([str(id.split('.')[1]) for id in ids if id.split('.')[0] == cf['type']])
            queryFields = ",".join(cf['queryFields'])
            sql =  "SELECT " + queryFields + " FROM " + cf['tableName'] +" WHERE " + cf['IdField'] + " in (" + sids + ")"
            rows = pg.select(sql)
            if(rows != None):
                for row in rows:
                    name = ''
                    if row[1] == None:
                        name = row[2]
                    else:
                        name = row[1]
                    locN = {
                        "id":cf['type']  + "." + str(row[0]),
                        "name":name.strip(),
                        "type":cf['type']
                    }
                    suitableLocations.append(locN)
        data = {
            "code":0,
            "data":suitableLocations
        }
        return data   

    def searchthematic(self, queryWord):
        pg = PGO()
        collName = 'thematicconfig'
        thematicConfigs = []
        rows = pg.select(r"SELECT name,thematicname,extent from " + collName +" WHERE name ~* '%s';" %(queryWord))
        for row in rows:
            config = {
                "name":row[0],
                "thematicName":row[1],
                "extent":row[2]
            }
            thematicConfigs.append(config)
        data = {
            "code":0,
            "data":thematicConfigs
        }
        return data
    
    def recomThematics(self):
        pg = PGO()
        collName = 'thematicconfig'
        thematicConfigs = []
        rows = pg.select(r"select name,thematicname,extent from %s order by id desc limit 10" % (collName))
        #select name,thematicname,extent from thematicconfig order by id desc limit 10
        for row in rows:
            config = {
                "name":row[0],
                "thematicName":row[1],
                "extent":row[2]
            }
            thematicConfigs.append(config)
        data = {
            "code":0,
            "data":thematicConfigs
        }
        return data

    def raiseThematicWeight(self,thematicNames):
        pg = PGO()
        collName = 'thematicconfig'
        Names = ["'" + v + "'"  for v in thematicNames]
        names = ",".join(Names)
        pg.updata(r'''update %s set "clickCount"="clickCount"+1 where thematicname in (%s)''' % (collName,names))

    def exploreAll(self, geometry):
        geometryObj = []
        for geo in geometry:
            geoObj = json.loads(geo)
            geometryObj.append(geoObj)
        orgs = GIS_Orgs('org')
        orgs.addOrgs_queryMongoByGeometries(geometry)
        features_orgs = orgs.getFeatures()
        events = GIS_Events()
        events.addEvents_queryMongoByGeometries(geometry)
        features_events = events.getFeatures()
        orgs = GIS_Orgs('GeoTar')
        orgs.addOrgs_queryMongoByGeometries(geometry)
        features_geotar = orgs.getFeatures()
        features_events.extend(features_orgs)
        features_events.extend(features_geotar)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features_events
                }
            }
        }
        return data
    
    def exploreEvent(self,geometry):
        events = GIS_Events()
        geometryObj = []
        for geo in geometry:
            geoObj = json.loads(geo)
            geometryObj.append(geoObj)
        events.addEvents_queryMongoByGeometries(geometry)
        features = events.events
        # Tg = TheadFun()
        # features = Tg.exploreEvents(geometry)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def exploreOrg(self, geometry):
        orgs = GIS_Orgs('org')
        geometryObj = []
        for geo in geometry:
            geoObj = json.loads(geo)
            geometryObj.append(geoObj)
        orgs.addOrgs_queryMongoByGeometries(geometry)
        features = orgs.getFeatures()
        # Tg = TheadFun()
        # features = Tg.exploreEvents(geometry)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def exploreGeoTar(self, geometry):
        orgs = GIS_Orgs('GeoTar')
        geometryObj = []
        for geo in geometry:
            geoObj = json.loads(geo)
            geometryObj.append(geoObj)
        orgs.addOrgs_queryMongoByGeometries(geometry)
        features = orgs.getFeatures()
        # Tg = TheadFun()
        # features = Tg.exploreEvents(geometry)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def getParamsByIds(self,orgIds, eventIds, contentIds):
        ids_event = eventIds
        ids_org = orgIds
        ids_content = contentIds
        contents = GIS_Content(ids_content)
        eventIdsFromContentIds = contents.relatedEventIds()
        ids_event.extend(eventIdsFromContentIds)
        orgs = GIS_Orgs('org')
        orgs.addOrgs_queryMongoByIds(ids_org)
        features_orgs = orgs.getFeatures()
        events = GIS_Events()
        events.addEvents_queryMongoByIds(ids_event)
        features_events = events.getFeatures()
        features_events.extend(features_orgs)
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features_events
                }
            }
        }
        return data
    
    def getEventByIds(self, param_ids):  
        events = GIS_Events()
        events.addEvents_queryMongoByIds(param_ids)
        features = events.getFeatures()
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def getOrgByIds(self, org_ids):
        orgs = GIS_Orgs('org')
        orgs.addOrgs_queryMongoByIds(org_ids)
        features = orgs.getFeatures()
        data = {
            "code":0,
            "data":{
                'Features':{
                    "type": "FeatureCollection",
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
                        }
                    },
                    "features": features
                }
            }
        }
        return data

    def createLouce(self,ids):
        Events = GIS_Events()
        idsByType = Events.classifyIdByDB(ids)
        Rows = []
        featureOrder = []
        for item in idsByType:
            rows = []
            config = item['config']
            ids = item['ids']
            qmgo = QMGO()
            qmgo.getRowsByIds(config,ids,rows,outField = ['QBId','Time','locationList'])
            Rows = Rows + rows
            pass
        Rows.sort(key=lambda x:x['row'][x['fieldConfig']['Time']])

        for row in Rows:
            locationlistFieldName = row['fieldConfig']['locationList']
            geometryFieldName = row['fieldConfig']['geometry']
            coors = row['row'][locationlistFieldName][0][geometryFieldName]['coordinates']  #取locationlist中的第一个位置
            featureId = 'event&' + str(coors[0])+ str(coors[1])
            featureOrder.append(featureId)
        
        data = {
            'code':0,
            'data':featureOrder
        }
        return data