"""Define the web api and offer the run() method """

import typing
import logging
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
import json
import os

from .config_resource import config_resource
from ..configs.MiddleEndConfig import CONFIG
from api.BackendAPI.BackendAPI import SPACE_BACKEND_API


class WebAPI(object):
    """Web-API Model, handle http request and call Graph-API to operate database """

    def __init__(self):
        """
        Init a  Model. Create an APP and an API for running ,and automatically bind
        url to Resource through config_resource.py
        """
        self.logger = logging.getLogger('logger')
        self._app = Flask(__name__)
        self._api = Api(self._app)
        self.client = self._app.test_client()
        self._config = {}

        # auto bind url to resource
        for resource, resource_config in config_resource.items():
            for arg_name, arg_config in resource_config["args"].items():
                resource.add_argument(arg_name, **arg_config)
            self._api.add_resource(resource, resource_config['url'])

    def run(self) -> None:
        """
        load the config for this project, handle Cross Origin Resource Sharing (CORS)
        offer a handle for running web api
        """
        # SPACE_BACKEND_API.set_after_CONFIG()

        CORS(self._app,
             resources=CONFIG.WebAPIConfig.CORS_resources,
             origins=CONFIG.WebAPIConfig.CORS_origins)  # cross field
        self._app.run(host=CONFIG.WebAPIConfig.run_host,
                      port=CONFIG.WebAPIConfig.run_port,
                      debug=CONFIG.WebAPIConfig.run_debug)

    # def url_for(self, resource_type, params=None, **kwargs):
    #     if params and type(params) == dict:
    #         return self._api.url_for(resource_type, **params)
    #     elif params and type(params) != dict:
    #         raise TypeError("params should be a dict. param=", params)
    #     else:
    #         return self._api.url_for(resource_type, **kwargs)

    # def test(self, input: str) -> str:
    #     """Process input data.
    #
    #     :param input: raw input.
    #     :return result: result.
    #     """
    #     self.logger.info('test')
    #     result = input
    #     return result
