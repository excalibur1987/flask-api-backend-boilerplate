from flask_restx.reqparse import RequestParser

offset_parser = RequestParser()
offset_parser.add_argument("offset", type=int, location="args", required=False)
offset_parser.add_argument("limit", type=int, location="args", required=False)
