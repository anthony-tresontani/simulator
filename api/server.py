import tornado.web
import tornado.ioloop
from core import Entity
from reporting.report import Report

class FactoryHandler(tornado.web.RequestHandler):
    def get_factory(self, factory_ID):
        factory = Entity.get_by_ref(int(factory_ID))
        if not factory:
            raise Exception
        return factory

class FactoryConfiguration(FactoryHandler):
    def get(self, factory_ID):
        # respond to a GET
        report = Report(self.get_factory(factory_ID))
        self.write(report.get_data())


class RemoteCommand(FactoryHandler):
    def post(self, factory_ID):
        factory = self.get_factory(factory_ID)
        action = self.get_argument("action")
        if action == "run":




application = tornado.web.Application([
    (r"/reports/([0-9]+)", FactoryConfiguration),
    (r"/command/([0-9]+)", RemoteCommand),
])

def start_server(application):
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start_server(application)
