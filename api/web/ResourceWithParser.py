"""My encapsulated Resource."""

from flask_restful import Resource, reqparse


class ResourceWithParser(Resource):
    """
    My encapsulated Resource. Resource offered by flask-restful do not have an arg_parser
    itself , so I combine Resource with an arg_parser, and automatically add arguments
    """
    _parser = None

    def __init__(self):
        super(ResourceWithParser, self).__init__()

    @classmethod
    def add_argument(cls, *args, **kwargs):
        """
        add argument for Resource's _parser
        :param args: name of the argument
        :param kwargs: config of the argument (see flask-restful reqparse.RequestParser())
        :return: None
        """
        cls._parser = cls._parser if cls._parser else reqparse.RequestParser()
        cls._parser.add_argument(*args, **kwargs)
