""" a namespace of all backend APIs, include SQLGraph, ES, etc..."""

from api.GIS.GISApplication import GISApplication as GIS_API
from api.Mongo.mongo_application import MongoApplication as Mongo_API
# global config
from api.configs.MiddleEndConfig import CONFIG
from api.es.esObj import esObj as EsObj_API
from api.es.set_and_project import SetProject as EsUtils_API
from api.fake.FakeAPI import FakeApplication as Fake_API
from api.Operator.operator_graph import OperatorGraph as OperatorGraph_API
from api.Operator.operator_doc import OperatorDoc as OperatorDoc_API
# all API
from api.graph.application.graph_application import GraphApplication as Graph_API


# base class of SpaceBackendAPI


class SpaceBackendAPI(object):
    """
    all backend APIs are placed in this class, these APIs are readonly outside the class
    use
        with self._context_allow_change():
    to change self.xxx, or it would raise an read-only error
    """

    def __init__(self):
        """
        init all APIs as None
        """
        pass

    @property
    def EsObj_API(self) -> EsObj_API:
        return EsObj_API(
            host=CONFIG.ESAPIConfig.host,
            port=CONFIG.ESAPIConfig.port,
            timeout=CONFIG.ESAPIConfig.timeout)

    @property
    def Graph_API(self) -> Graph_API:
        return Graph_API(
            ip=CONFIG.GraphAPIConfig.address,
            port=CONFIG.GraphAPIConfig.port,
            database_name=CONFIG.GraphAPIConfig.database_name,
            graph_name=CONFIG.GraphAPIConfig.graph_name,
            event_graph_database_name=CONFIG.GraphAPIConfig.event_graph_database_name,
            event_graph_graph_name=CONFIG.GraphAPIConfig.event_graph_graph_name
        )

    @property
    def Mongo_API(self) -> Mongo_API:
        return Mongo_API(
            host=CONFIG.MongoAPIConfig.host,
            port=CONFIG.MongoAPIConfig.port,
            usr=CONFIG.MongoAPIConfig.usr,
            pwd=CONFIG.MongoAPIConfig.pwd
        )

    @property
    def GIS_API(self) -> GIS_API:
        return GIS_API()

    @property
    def Fake_API(self) -> Fake_API:
        return Fake_API()

    @property
    def EsUtils_API(self) -> EsUtils_API:
        return EsUtils_API()  # a model, not a class

    @property
    def OperatorGraph_API(self) -> OperatorGraph_API:
        return OperatorGraph_API()

    @property
    def OperatorDoc_API(self) -> OperatorDoc_API:
        return OperatorDoc_API()

# use object SPACE_BACKEND_API instead of class SpaceBackendAPI outside this model
SPACE_BACKEND_API = SpaceBackendAPI()
