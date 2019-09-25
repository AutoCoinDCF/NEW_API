""" a context to get codes' executing time"""

import datetime
from contextlib import contextmanager


@contextmanager
def code_timer(msg: str="code execute time: ", show_start=False) -> datetime.time:
    """"a context function to count code executing time"""
    start = datetime.datetime.now()
    if show_start:
        print(msg + '  start running')
    try:
        yield datetime.datetime.now
    finally:
        end = datetime.datetime.now()
        print(msg + str(end-start))

#  test
# import time
# with code_timer("sleeping time:"):
#     time.sleep(65)