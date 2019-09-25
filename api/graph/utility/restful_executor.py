import os, requests

from ast import literal_eval

import api.configs.dynamic_config as dy_config
from api.log.QBLog import QBLog


class Executor(object):
    """
    execute sql , this executor use SQLGraph's restful api
    """

    def __init__(self, user: str = None, password: str = None, ip: str = '10.60.1.142', port: int or str = 8123,
                 database_name: str = 'default'):
        self._config = {
            "user": user,
            "password": password,
            "ip": ip,
            "port": port,
            "database_name": database_name,
        }
        self.s_url = "http://{ip}:{port}/".format(**self._config)
        self.logger = QBLog({'LOG_LEVEL': dy_config.LOG_LEVEL}, self.__class__.__name__)

    @property
    def _restful_url_prefix(self):
        if self._config["user"] is not None:
            return "http://{user}:{password}@{ip}:{port}/{database_name}/".format(**self._config)
        else:
            return "http://{ip}:{port}/{database_name}/".format(**self._config)

    @property
    def _restful_url_prefix_post(self):
        if self._config["user"] is not None:
            return "http://{user}:{password}@{ip}:{port}".format(**self._config)
        else:
            return "http://{ip}:{port}/".format(**self._config)

    def execute(self, query, format="Graph", insert=False):
        if not insert:
            return requests.get(self._restful_url_prefix,
                                params={"query": query + "format %s" % format}) \
                if format != "" \
                else \
                requests.post(self._restful_url_prefix_post,
                              params={"query": query})
        else:
            try:
                os.popen('curl -d "%s" %s' % (query, self.s_url)).readlines()
                self.logger.info('Insert the success!')
            except Exception as error:
                self.logger.error(f'Insert the failed error: {error}')

    def execute_related(self, query, format="Graph"):
        '''
        备注： requests.get的参数极限是314参, 当前方法参数极限时2966参，如需更大请求，采用分批申请后相加
        '''
        try:
            res = os.popen('''echo "%s" | POST "%s"''' % (query + "format %s" % format, self.s_url)).read()
            return literal_eval(res)
        except:
            raise
