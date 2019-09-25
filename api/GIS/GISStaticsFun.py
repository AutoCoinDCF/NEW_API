from .mapGraph.BezierLine import BezierLine as BL
from .database.postGIS import PGO
import json
class GisStaticsFun:
    def __init__(self):  
        pass

    @staticmethod
    def getOrgDictBySearRes(row,dicto):
        ident = GisStaticsFun.getIdentBySearRes(row)
        Org = {
            "OrgName":row['Entity_name'],
            "id":row['Entity_id'],
        }
        location = GisStaticsFun.getGeometryBySearRes(row)
        if(ident in dicto):
            OrgArr = dicto[ident]['Params']
            OrgArr.append(Org)
        else:
            dicto[ident] = {
                "Params":[Org],
                "location":location
            }
    @staticmethod
    def getIdentBySearRes(row):
        ident = ''
        if "Entity_id" in row:
            X = str(row['location']['coordinates'][0]) 
            Y = str(row['location']['coordinates'][1])
            ident = 'org&' + X + Y
        else:
            if 'from' in row['location_list'][0].keys():
                ident = 'event&' + str(row["_id"])
            else:
                X = str(row['location_list'][0]['geometry']['coordinates'][0]) 
                Y = str(row['location_list'][0]['geometry']['coordinates'][1])
                ident = 'event&' + X + Y
        return ident

    @staticmethod
    def getEventDictBySearRes(row,dicto):   #根据一条查询结果生成事件特定格式的字典
        EventId = str(row['_id'])
        ident = GisStaticsFun.getIdentBySearRes(row)
        eventType = row['event_subtype']
        Event = {
            "id": EventId,
            'eventType':eventType
        }
        location = GisStaticsFun.getGeometryBySearRes(row)
        
        if(ident in dicto):
            EventArr = dicto[ident]['Params']
            EventArr.append(Event)
        else:
            dicto[ident] = {
                "Params":[Event],
                "location":location
            }
    @staticmethod
    def getGeometryBySearRes(row):
        geometry = {}
        if "Entity_id" in row:
            geometry = row['location']
        else:
            if 'from' in row['location_list'][0].keys():
                froms = row['location_list'][0]['from']
                tos = row['location_list'][0]['to']
                linesGeometry = []
                i = 0
                while i < len(froms):
                    fromName = froms[i]['name']
                    toName = tos[i]['name']
                    fromCoor = froms[i]['geometry']['coordinates']
                    toCoor = tos[i]['geometry']['coordinates']
                    bl = BL(fromCoor,toCoor,50)
                    lineGeometry = bl.getBezierPoints()
                    linesGeometry.append(lineGeometry)
                    i = i + 1
                geometry = {"type": "MultiLineString","coordinates":linesGeometry}
            else:
                geometry = row['location_list'][0]['geometry']
        return geometry
    
    @staticmethod
    def isIntersert(geometry_a,geometry_b):
        isIntersect = False
        pg = PGO()
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

    @staticmethod
    def getHeatAttr(row,heatAttrConfig,EventAttrKey):
        heatAttr = {}
        for attr in heatAttrConfig:
            attrname = attr["attrName"]
            showname = attr["showName"]
            if attrname in row[EventAttrKey]:
                heatAttr[showname] = row[EventAttrKey][attrname]
        return heatAttr
    