import json
import os

from .configs import *


def load_config_dict(config_file_name: str, choice: str) -> dict:
    """ return config dict from .json config file"""
    with open(config_file_name, encoding='utf-8') as f:
        config_dict = json.load(f)
    return config_dict[choice]


class MiddleEndConfig(object):
    """ global configs """

    def __init__(self):
        self.WebAPIConfig: WebAPIConfig = None
        self.GraphAPIConfig: GraphAPIConfig = None
        self.ESAPIConfig: ESAPIConfig = None
        self.ESSearchConfig: ESSearchConfig = None
        self.MongoAPIConfig: MongoAPIConfig = None

    def choose_config(self,
                      WebAPI_choice: str = "test",
                      GraphAPI_choice: str = "test",
                      ESAPI_choice: str = "test",
                      ESSearch_choice: str = "test",
                      MongoAPI_choice: str = "test") -> None:
        """
        choose config from config_file, inputs are the config choice index in config file
        :param WebAPI_choice: should be "test" or "dev" or "product"
        :param GraphAPI_choice: should be "test" or "dev" or "product"
        :return: None
        """
        file_pattern = os.path.dirname(__file__) + '/config_files/config_%s.json'
        self.WebAPIConfig = WebAPIConfig(**load_config_dict(file_pattern % "WebAPI", WebAPI_choice))
        self.GraphAPIConfig = GraphAPIConfig(**load_config_dict(file_pattern % "GraphAPI", GraphAPI_choice))
        self.ESAPIConfig = ESAPIConfig(**load_config_dict(file_pattern % "ESAPI", ESAPI_choice))
        self.ESSearchConfig = ESSearchConfig(**load_config_dict(file_pattern % "ESSearch", ESSearch_choice))
        self.MongoAPIConfig = MongoAPIConfig(**load_config_dict(file_pattern % "MongoAPI", MongoAPI_choice))


# use this singleton obj CONFIG outside this file
CONFIG = MiddleEndConfig()
