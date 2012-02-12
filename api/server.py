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
        report = Report()
        self.write(report.get_factory_data(int(factory_ID)))

class ProductionUnit(FactoryHandler):
    def get(self, factory_ID, pu_name):
        # respond to a GET
        report = Report()
        self.write(report.get_production_unit_data(int(factory_ID), pu_name))


class RemoteCommand(FactoryHandler):
    def post(self, factory_ID):
        self.factory = self.get_factory(factory_ID)
        action = self.get_argument("command")
        if action == "run":
            self.run()

    def run(self):
        time = int(self.get_argument("time"))
        self.factory.run(during=time)


application = tornado.web.Application([
    (r"/reports/([0-9]+)", FactoryConfiguration),
    (r"/reports/([0-9]+)/productionunit/([a-z0-9]+)", ProductionUnit),
    (r"/command/([0-9]+)", RemoteCommand),
])

def start_server(application):
    application.listen(8889)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start_server(application)
