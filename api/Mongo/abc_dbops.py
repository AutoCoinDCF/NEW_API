'''AbstractDbOps: 数据库操作接口抽象类

@author: shishidun@ict.ac.cn
@last_modified: 2019.6.20
'''

from abc import ABC, abstractmethod


class AbstractDbOps(ABC):
    @abstractmethod
    def __init__(self):
        '''初始化

        eg: Initialize db instance
        '''
        raise NotImplementedError
