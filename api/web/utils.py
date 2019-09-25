# %%
""" Some useful functions"""
import json
import time
from functools import wraps
from typing import Dict

# from line_profiler import LineProfiler
from pandas import DataFrame
import threading
import time
import api.configs.dynamic_config as dy_config
from api.log.QBLog import QBLog
from api.fake.FakeAPI import FakeApplication

logger = QBLog({
    'LOG_LEVEL': dy_config.LOG_LEVEL
})


# %%
def get_fake_data(data_name: str) -> Dict:
    """
    When front-end wanting some data, but haven't been offered by database ,
    use some fake data for front-end to test UI

    :param data_name: the fake data's name
    :return: a dict of fake data
    """
    with open("./fake_data/%s.json" % data_name, encoding='utf-8') as f:
        data = json.load(f)
    return data


# %%
def group_by_node_type(NodeIds: list, NodeTypes: list) -> dict:
    df = DataFrame(zip(NodeIds, NodeTypes), columns=["id", "meta_type"])
    groups = {name: group["id"].tolist() for name, group in df.groupby(["meta_type"])}
    return groups


def new_response(code: int = 0, message: str = "", data: list = None):
    response = {
        "code": code,
        "message": message,
        "data": data if data is not None else []
    }
    return response


# def func_line_time(f):
#     '''
#     Query the time of execution of each line of code in the interface
#     '''
#
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         func_return = f(*args, **kwargs)
#         lp = LineProfiler()
#         lp_wrap = lp(f)
#         lp_wrap(*args, **kwargs)
#         lp.print_stats()
#         return func_return
#
#     return decorator


def totalTime(func):
    def run(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        logger.info("该接口的运行时间为： {0}".format(time.time() - start))
        return result
    return run


def while_true_loop(func):
    '''无线循环装饰器
    '''
    @wraps(func)
    def _wraps(*args, **kwargs):
        while True:
            func(*args, **kwargs)

    return _wraps


def asynchronous_task(func):
    # return返回后异步执行装饰器
    def wrapper(*args, **kwargs):
        def content(val):
            ex = FakeApplication()
            ex.attr_pretreatment(val)
        data = func(*args, **kwargs)
        threading.Thread(target=content, args=(data, )).start()
        return data
    return wrapper
