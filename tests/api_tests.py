from unittest.case import TestCase
import simplejson
from api.server import  application
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web
from hamcrest import *
from configuration import get_factory
from tests.utils import create_machine
from urllib import urlencode

def in_python(expression):
    return simplejson.loads(expression)

config = """
name: textil
production_units:
    - name: wiremachine
      inputs:
          - input_type: wood
            input_quantity: 1
      outputs:
          - input_type: wire
            input_quantity: 1
workers:
    - type: generic
      number: 1
      working_hour: 8
"""

class TestApi(TestCase):
    @classmethod
    def setUpClass(cls):
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8888)

    def setUp(self):
        machine, spec, stock = create_machine(stocking_zone_size=None)
        self.factory = get_factory(config)
        self.http_client = tornado.httpclient.AsyncHTTPClient()

    def tearDown(self):
        self.response = None

    def handle_request(self, response):
        self.response = response
        tornado.ioloop.IOLoop.instance().stop()

    def test_GET_report(self):
        self.http_client.fetch('http://localhost:8888/reports/%d' % self.factory.reference,
            self.handle_request)
        tornado.ioloop.IOLoop.instance().start()

        assert_that(self.response.error, is_(none()))

        result_dict = in_python(self.response.body)
        assert_that(result_dict, has_entries({"number of production unit": 1}))
        assert_that(result_dict, has_entries({"number of workers": 1}))
        assert_that(result_dict, has_entries({"Current time": 0}))

    def test_get_production_unit_info(self):
        self.http_client.fetch('http://localhost:8888/reports/%d/productionunit/wiremachine' % self.factory.reference,
            self.handle_request)
        tornado.ioloop.IOLoop.instance().start()

        assert_that(self.response.error, is_(none()))

        result_dict = in_python(self.response.body)
        assert_that(result_dict, has_entries({"produce": ["wire"]}))
        assert_that(result_dict, has_entries({"units_produced": 0}))

    def test_POST_report(self):
        post_data = {"command":"run", "time":2}
        self.http_client.fetch(tornado.httpclient.HTTPRequest('http://localhost:8888/command/%d' % self.factory.reference,
                                                              method="POST", body=urlencode(post_data)),
            self.handle_request)
        tornado.ioloop.IOLoop.instance().start()
        assert_that(self.response.error, is_(none()))
        assert_that(self.factory.time, is_(2))

































