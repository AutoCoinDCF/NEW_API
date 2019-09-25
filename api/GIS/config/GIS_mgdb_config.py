dataBaseConfig=[
        {'id':"mg_1",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'entity','type':'org'},
        {'id':"mg_2",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'events_gtd','type':'event'},
        {'id':"mg_3",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'events_labeled','type':'event'},
        {'id':"mg_4",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'events_taiwan','type':'event'},
        {'id':"mg_5",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'document_darpa','type':'doc'},
        {'id':"mg_6",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'document_gtd','type':'doc'},
        {'id':"mg_7",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'document_labeled','type':'doc'},
        {'id':"mg_8",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'document_humanrights','type':'doc'},
        {'id':"mg_9",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'document_taiwan','type':'doc'},
        {'id':"mg_10",'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'QBData', 'collName':'events_sg_4','type':'event'},
        
]

idMapColl= {
    'ca8fcda5':'mg_2',
    'd713ba29': 'mg_3',
    '37836765':'mg_4',
    '7e3bb7cb':'mg_10'
}

contentIdMapColl={
    'e7764954':'mg_5',
    'ca8fcda5':'mg_6',
    'd713ba29':'mg_7',
    'def57351':'mg_8',
    '37836765':'mg_9'
}

fieldConfig = {
    "QBData":{
        "entity":{
            "QBId":"Entity_id",
            "QBName":"Entity_name",
            "locationList":"location",
            "QBEnName":"Chinese_name",
            "type":"Entity_type",
            "locationName":"Entity_name",
            "showHeatAttr":[
            ]
        },
        "coordinate":{
            "QBId":"Entity_id",
            "QBName":"Entity_name",
            "locationList":"location",
            "QBEnName":"Chinese_name",
            "type":"Entity_type",
            "locationName":"Entity_name",
            "showHeatAttr":[
            ]
        },
        "events_gtd":{
            "locationList":"location_list",
            "geometry":"geometry",
            "QBId":"_id",
            'DocId':"doc_id",
            "Name":"name",
            "Subtype":"event_subtype",
            "EventAttr":"event_attribute", 
            "Time":"publish_time",
            "showHeatAttr":[
                {"attrName":"nkill","showName":"死亡人数"}
            ]
        },
        "events_labeled":{
            "locationList":"location_list",
            "geometry":"geometry",
            "QBId":"_id",
            'DocId':"doc_id",
            "Name":"name",
            "Subtype":"event_subtype",
            "EventAttr":"event_attribute", 
            "Time":"publish_time",
            "showHeatAttr":[
                {"attrName":"nkill","showName":"死亡人数"}
            ]
        },
        "events_taiwan":{
            "locationList":"location_list",
            "geometry":"geometry",
            "QBId":"_id",
            'DocId':"doc_id",
            "Name":"name",
            "Subtype":"event_subtype",
            "EventAttr":"event_attribute", 
            "Time":"publish_time",
            "showHeatAttr":[
                {"attrName": "nkill", "showName": "死亡人数"}
            ]
        },
        "events_sg_4": {
            "locationList": "location_list",
            "geometry": "geometry",
            "QBId":"_id",
            'DocId':"doc_id",
            "Name":"name",
            "Subtype":"event_subtype",
            "EventAttr":"event_attribute", 
            "Time":"publish_time",
            "showHeatAttr": [
                {"attrName": "nkill", "showName": "死亡人数"},
                {"attrName": "number_person", "showName": "参与人数"}
            ]
        },
        "document_darpa":{
            'DocId':''
        }
    }
}

QBTypeConfig = {
    "org":"organization",
    "GeoTar":"geographic_entity"
}
