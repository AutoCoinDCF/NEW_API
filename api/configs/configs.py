""" configs of webapi, sqlgraph, es """
from dataclasses import dataclass


@dataclass(frozen=True)
class WebAPIConfig(object):
    CORS_resources: str
    CORS_origins: str
    run_host: str
    run_port: int
    run_debug: bool


@dataclass(frozen=True)
class GraphAPIConfig(object):
    address: str
    port: int
    img_url_template: str
    database_name: str
    graph_name: str
    event_graph_database_name: str
    event_graph_graph_name: str


@dataclass(frozen=True)
class ESAPIConfig(object):
    host: str
    port: str
    timeout: int


@dataclass(frozen=True)
class ESSearchConfig(object):
    entity_index: str
    entity_doc_type: str


@dataclass(frozen=True)
class MongoAPIConfig(object):
    host: str
    port: int
    usr: str
    pwd: str
