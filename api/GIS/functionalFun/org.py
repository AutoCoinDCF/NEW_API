from api.GIS.config import GIS_mgdb_config
from api.GIS.GIS_query.queryMongoDB import QueryMGO as QMGO
class GIS_Orgs():
    def __init__(self,type):
        self.type = type
        self.orgs = []
        self.orgType = GIS_mgdb_config.QBTypeConfig[type]

    def addOrgs_queryMongoByIds(self,ids):
        qmgo = QMGO()
        _orgs= qmgo.getOrgs('id',self.orgType,ids)
        self.orgs.extend(_orgs)

    def addOrgs_queryMongoByGeometries(self,Geometries):
        qmgo = QMGO()
        _events = qmgo.getOrgs('geometry',self.orgType,Geometries)
        self.orgs.extend(_events)

    def getFeatures(self):
        # try:
        #     assert len(self.events) == 0,"events未赋值！"
            featureInfo = {}
            features = []
            for org in self.orgs:
                Param = {
                    "ParamId":org['ParamId'],
                    "QBId":org['QBId'],
                    'QBName':org['QBName'],
                    "heatAttr":org['heatAttr']
                }
                ident = org['ident']
                location = org['geometry']
                localName = org['localName']
                if(ident in featureInfo):
                    EventArr = featureInfo[ident]['Params']
                    EventArr.append(Param)
                else:
                    featureInfo[ident] = {
                        "Params":[Param],
                        "location":location,
                        "localName":localName 
                    }
            for k,v in featureInfo.items():
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
