#import pytest
from api.web import WebAPI


def test_webapi():
    test = WebAPI()
    assert test is not None
    test.run()
