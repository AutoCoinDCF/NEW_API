from .api_resource import *

"""
Config of my restful resources, my resources automatically add arguments for their
RequestParser, and my api automatically bind resources to url
These resources are defined in api_resource.py

the optional config parameters are the same as flask_restful.reqparse.Argument .

class reqparse.Argument(name, default=None, dest=None, required=False,
                        ignore=False, type=<function <lambda> at 0x1065c6c08>,
                        location=('json', 'values'), choices=(), action='store',
                        help=None, operators=('=', ), case_sensitive=True,
                        store_missing=True)
Optional Parameters:
:param name – Either a name or a list of option strings, e.g. foo or -f, –foo.
:param default – The value produced if the argument is absent from the request.
:param dest – The name of the attribute to be added to the object returned by parse_args().
:param required (bool) – Whether or not the argument may be omitted (optionals only).
:param action – The basic type of action to be taken when this argument is encountered
in the request. Valid options are “store” and “append”.
:param ignore – Whether to ignore cases where the argument fails type conversion
:param type – The type to which the request argument should be converted. If a type raises
a ValidationError, the message in the error will be returned in the response. Defaults to
unicode in python2 and str in python3.
:param location – The attributes of the flask.Request object to source the arguments from
(ex: headers, args, etc.), can be an iterator. The last item listed takes precedence in the
result set.
:param choices – A container of the allowable values for the argument.
:param help – A brief description of the argument, returned in the response when the argument
is invalid with the name of the argument and the message passed to a ValidationError raised
by a type converter.
:param case_sensitive (bool) – Whether the arguments in the request are case sensitive or not
:param store_missing (bool) – Whether the arguments default value should be stored if the
argument is missing from the request.
"""

config_resource = {

    #  -----------------------------------------search----------------------------------
    FuzzyMatch: {
        'url': '/fuzzy-match/',
        'args': {
            "pattern": {
                "type": str,
                "required": True},
            "size": {
                "type": int,
                "default": 100},
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },
    QBSearch: {
        'url': '/qb-search/',
        'args': {
            "keyword": {
                "type": str,
                "required": True
            },
            "type": {
                "type": str,
                "default": "net"
            },
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },

    # -----------------------------------------entity----------------------------------
    EntityInfo: {
        'url': '/entity-info/',
        'args': {
            "nodeIds": {
                "type": str,
                "action": "append",
                "required": True}
        }
    },
    EntityDetail: {
        'url': '/entity-detail/',
        'args': {
            "nodeIds": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },

    # -----------------------------------------event----------------------------------
    EventDetail: {
        "url": "/event-detail/",
        "args": {
            "EventIds": {
                "type": str,
                "action": "append",
                "required": True},
        }
    },
    EventDoc2Time: {
        "url": "/event-2-time/",
        "args": {
            "eventIds": {
                "type": str,
                "action": "append",
                "default": list
            },
            "docIds": {
                "type": str,
                "action": "append",
                "default": list
            },
        }
    },

    # -----------------------------------------document----------------------------------
    ContextById: {
        'url': '/context-by-id/',
        'args': {
            "idValue": {
                "type": str,
                "required": True}
        }
    },
    DocumentDetail: {
        "url": "/doc-detail/",
        "args": {
            "docIds": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    Translate: {
        "url": "/translate/",
        "args": {
            "id": {
                "type": str,
                "required": True}
        }
    },
    ContextByText: {
        "url": "/context-by-text/",
        "args": {
            "query": {
                "type": str,
                "required": True},
            "page": {
                "type": int,
                "required": True},
            "timeStart": {
                "type": int,
                "default": -1},
            "timeEnd": {
                "type": int,
                "default": -1},
            "isSortByTime": {
                "type": str,
                "default": "",
                "choices": ("asc", "desc", "")},
            "PageSize": {
                "type": int,
                "default": 2},
            "limit": {
                "type": str,
                "default": ""
            }
        }
    },
    ContextSectionSearch: {
        "url": "/context-section-search/",
        "args": {
            "keyword": {
                "type": str,
                "required": True
            }
        }
    },
    RowDocTop: {
        'url': '/row_doc-top/',
        'args': {
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "typeLabel": {
                "type": str,
                "default": "single"
            },
            "word": {
                "type": str,
                "default": "keywords"
            }
        }
    },
    DocTop: {
        'url': '/doc-top/',
        'args': {
            "idList": {
                "type": list,
                "action": "append",
                "default": list
            },
            "ids": {
                "type": str,
                "action": "append",
                "default": list
            },
            "names": {
                "type": str,
                "action": "append",
                "default": list
            }
        }
    },
    DocTopTime: {
        'url': '/doc-top-time/',
        'args': {
            "idList": {
                "type": str,
                "action": "append",
                "required": True
            },
            "times": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    WordDoc: {
        'url': '/word-doc/',
        'args': {
            "idList": {
                "type": str,
                "action": "append",
                "required": True
            },
            "word": {
                "type": str,
                "action": "append",
                "required": True
            },
            "speech": {
                "type": str,
                "default": True
            }
        }
    },

    # -----------------------------------------GIS----------------------------------
    getParamByIds: {
        "url": "/param-exploration/",
        "args": {
            "orgIds": {
                "type": str,
                "action": "append",
                "default": list
            },
            "eventIds": {
                "type": str,
                "action": "append",
                "default": list
            },
            "contentIds": {
                "type": str,
                "action": "append",
                "default": list
            }
        }
    },

    searchAreaByIds: {
        "url": "/search-Area/",
        "args": {
            "nodeIds": {
                "type": str,
                "action": "append",
                "required": True}
        }
    },
    Node2GIS: {
        "url": "/node-to-GIS/",
        "args": {
            "nodeIds": {
                "type": str,
                "action": "append",
                "required": True},
        }
    },
    LocationName: {
        "url": "/search-location-name/",
        "args": {
            "localName": {
                "type": str,
                "required": True}
        }
    },
    ExploreOrg: {
        "url": "/exploreOrg/",
        "args": {
            "geometry": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    ExploreGeoTar: {
        "url": "/exploreGeoTar/",
        "args": {
            "geometry": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    exploreEvent: {
        "url": "/exploreEvent/",
        "args": {
            "geometry": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    getEventByIds: {
        "url": "/getEventByIds/",
        "args": {
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    getOrgByIds: {
        "url": "/getOrgByIds/",
        "args": {
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    searchthematic: {
        "url": "/searchthematic/",
        "args": {
            "queryWord": {
                "type": str,
                "required": True
            }
        }
    },

    recommendThematics:{
        "url":"/recommend-thematics/",
        "args": {
            # "localName": {
            #     "type": str,
            #     "required": True}
        }
    },

    raiseThematicClickCount: {
        "url": "/raise-thematic-clickcount/",
        "args": {
            "thematicNames": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },

    createLouce: {
        "url": "/create-Locus/",
        "args": {
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },

    # -----------------------------------------set&project----------------------------------
    IndexSetData: {
        "url": "/index-set-data/",
        "args": {
            "IdList": {
                "type": str,
                "action": "append",
                "default": None},
            "TypeLabel": {
                "type": str,
                "default": None},
            "isAcc": {
                "type": bool,
                "default": True},
            "data": {
                "type": dict,
                "default": None},
            "timestamp": {
                "type": str,
                "default": None}
        }
    },
    LoadSetData: {
        "url": "/load-set-data/",
        "args": {
            "idlist": {
                "type": str,
                "action": "append",
                "default": None},
            "label": {
                "type": str,
                "default": None},
            "query": {
                "type": str,
                "default": None},
            "page": {
                "type": int,
                "default": 1},
            "pagesize": {
                "type": int,
                "default": 30},
            "timestamp": {
                "type": str,
                "default": None},
            "limit": {
                "type": bool,
                "default": False
            }
        }
    },
    DeleteSetData: {
        "url": "/delete-set-data/",
        "args": {
            "idlist": {
                "type": str,
                "action": "append",
                "default": None},
            "label": {
                "type": str,
                "default": None},
            "type": {
                "type": str,
                "default": None},
            "timestamp": {
                "type": str,
                "default": None}
        }
    },
    IndexProjectData: {
        "url": "/index-project-data/",
        "args": {
            "IdList": {
                "type": str,
                "action": "append",
                "default": None},
            "TypeLabel": {
                "type": str,
                "default": None},
            "isAcc": {
                "type": bool,
                "default": True},
            "data": {
                "type": dict,
                "default": None},
            "timestamp": {
                "type": str,
                "default": None}
        }
    },

    # -----------------------------------------related----------------------------------
    FindPath: {
        'url': '/all-path-data/',
        'args': {
            'start': {
                "type": str,
                "required": True},
            'end': {
                "type": str,
                "required": True},
            'step': {
                "type": int}
        }
    },
    CalculateBFSTree: {
        "url": "/hierarchical-node-structure/",
        "args": {
            "nodeIds": {
                "type": str,
                "action": "append",
                "required": True},
            "RootNodeIdList": {
                "type": str,
                "action": "append",
                "required": True},
            "EdgeList": {
                "type": dict,
                "action": "append"},
            "edge_from_backend": {
                "type": bool,
                "default": True}
        }
    },
    RelatedAll: {
        "url": "/related-all/",
        "args": {
            "NodeIds": {
                "type": str,
                "action": "append",
                "required": True},
            "Group": {
                "type": bool,
                "default": False},
            "TypeLabel": {
                "type": str,
                "default": "all"},
        },
    },
    ShortPath: {
        'url': '/ShortPath/',
        'args': {
            "NodeIds_single": {
                "type": str,
                "action": "append",
                "required": True},
            "NodeIds_double": {
                "type": str,
                "action": "append",
                "default": None
            },
            "typeLabel": {
                "type": str,
                "default": "all"},
            "step": {
                "type": int,
                "default": 5
            }
        }
    },
    CommonAll: {
        "url": "/commonAll/",
        "args": {
            "NodeIds": {
                "type": str,
                "action": "append",
                "required": True},
            "ComLabel": {
                "type": str,
                "default": "all"},
        },
    },
    Community: {
        'url': '/community/',
        'args': {
            "from_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "to_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "method": {
                "type": str,
                "default": "community"
            },
            "num": {
                "type": int,
                "action": "append",
                "default": list
            }
        }
    },

    # -----------------------------------------Statistics----------------------------------
    GraphAttr: {
        "url": "/graph-attr/",
        "args": {
            "entityIds": {
                "type": str,
                "action": "append",
                "default": list
            },
            "eventIds": {
                "type": str,
                "action": "append",
                "default": list
            },
            "docIds": {
                "type": str,
                "action": "append",
                "default": list
            },
            "type": {
                "type": str,
                "default": None}
        }
    },
    Aggregation: {
        'url': '/aggregation/',
        'args': {
            "allNodeIds": {
                "type": str,
                "action": "append",
                "required": True
            },
            "selectNodeIds": {
                "type": str,
                "action": "append",
                "required": True
            },
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },
    FieldTranslate: {
        'url': '/FieldTranslate/',
        'args': {
            "type": {
                "type": str,
                "default": "all"
            },
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },
    KeywordMatch: {
        'url': '/KeywordMatch/',
        'args': {
            "type": {
                "type": str,
                "default": "all"
            },
            "Attr": {
                "type": dict,
                "action": "append",
                "required": True
            },
            "page": {
                "type": int,
                "default": 1
            },
            "pageSize": {
                "type": int,
                "default": 3
            },
            "max": {
                "type": int,
                "default": 25
            },
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },
    NodeDetail: {
        'url': '/node-detail/',
        'args': {
            "type": {
                "type": str,
                "default": "entity"
            },
            "nodeIds": {
                "type": str,
                "action": "append",
                "required": True
            },
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },

    # -----------------------------------------other----------------------------------
    NodeStatisticsInType: {
        'url': '/node-statistics-in-type/',
        'args': {
            "nodeIds": {
                "type": str,
                "action": "append",
                "required": True},
            "typename": {
                "type": str,
                "required": True},
        }
    },
    DocStatistics: {
        "url": "/doc-statistics/",
        "args": {
            "query": {
                "type": str,
                "required": True
            }
        }
    },

    # -----------------------------------------元搜索----------------------------------

    DataSearch: {
        "url": "/data-search/",
        "args": {
            "query": {
                "type": str,
                "required": True
            },
            "website": {
                "type": str,
                "default": "必应"
            },
            "requestNumber": {
                "type": int,
                "default": 30
            }
        }
    },
    IndexDataSet: {
        "url": "/index-data-set/",
        "args": {
            "name": {
                "type": str,
                "required": True
            },
            "des": {
                "type": str,
                "required": True
            },
            "source": {
                "type": str,
                "required": True
            },
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "titles": {
                "type": str,
                "action": "append",
                "required": True
            },
            "urls": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    SearchTask: {
        "url": "/search_task/",
        "args": {
            "status": {
                "type": str,
                "default": "全部状态"
            },
            "source": {
                "type": str,
                "default": "全部来源"
            },
            "page": {
                "type": int,
                "default": 0
            },
            "pageSize": {
                "type": int,
                "default": 0
            },
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },
    ToDoTask: {
        "url": "/to_do_task/",
        "args": {
            "task_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            # 选参: del, uninstall, install
            "dispose_type": {
                "type": str,
                "required": True
            },
            "timestamp": {
                "type": str,
                "default": None
            }
        }
    },
    UploadTask: {
        "url": "/upload_task/",
        "args": {
            "name": {
                "type": str,
                "required": True
            },
            "des": {
                "type": str,
                "required": True
            },
            "content": {
                "type": dict,
                "action": "append",
                "required": True
            },
            "source": {
                "type": str,
                "default": "文件上传"
            }
        }
    },
    SearchAttr: {
        "url": "/search_attr/",
        "args": {
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "ses": {
                "type": list,
                "action": "append",
                "required": True
            }
        }
    },
    SeAttr: {
        "url": "/se_attr/",
        "args": {
            "search_id": {
                "type": str,
                "required": True
            },
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    Test: {
        "url": "/test/",
        "args": {
            "source_str": {
                "type": str,
                "default": "12345"
            },
            "source_dict": {
                "type": str,
                "action": "append",
                "default": {"key": "value"}
            }
        }
    },
    DocHighlight: {
        "url": "/doc_highlight/",
        "args": {
            "doc_id": {
                "type": str,
                "required": True
            }
        }
    },
    GetEntity: {
        "url": "/get_entity/",
        "args": {
            "ids": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    DocSentimentTime: {
        "url": "/doc_sentiment_time/",
        "args": {
            "idList": {
                "type": str,
                "action": "append",
                "required": True
            },
            "Time": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    DocSentiment: {
        "url": "/doc_sentiment/",
        "args": {
            "idList": {
                "type": list,
                "action": "append",
                "default": list
            },
            "ids": {
                "type": str,
                "action": "append",
                "default": list
            },
            "names": {
                "type": str,
                "action": "append",
                "default": list
            }
        }
    },
    StrongConnectedSubgraph: {
        "url": "/strong_connected_subgraph/",
        "args": {
            "from_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "to_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "node_num": {
                "type": int,
                "required": True
            }
        }
    },
    CommunityDetect: {
        "url": "/community_detect/",
        "args": {
            "from_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "to_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "community_num": {
                "type": int,
                "required": True
            }
        }
    },
    NodeImportance: {
        "url": "/node_importance/",
        "args": {
            "from_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "to_ids": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    EdgeImportance: {
        "url": "/edge_importance/",
        "args": {
            "from_ids": {
                "type": str,
                "action": "append",
                "required": True
            },
            "to_ids": {
                "type": str,
                "action": "append",
                "required": True
            }
        }
    },
    TextClustering: {
        "url": "/text_clustering/",
        "args": {
            "text_dict": {
                "type": dict,
                "required": True
            },
            "class_num": {
                "type": int,
                "required": True
            }
        }
    },
}
