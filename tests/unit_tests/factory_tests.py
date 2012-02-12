from unittest.case import TestCase
from core.factory import Factory
from core.production_unit import ProductionUnit
from core.worker import Worker
from hamcrest import *

class TestFactory(TestCase):

    def test_factory_add_worker(self):
        factory = Factory()
        factory.add_worker(Worker())
        self.assertEquals(len(factory.workers), 1)

    def test_factory_add_production_unit(self):
        factory = Factory()
        factory.add_production_unit(ProductionUnit(None))
        self.assertEquals(len(factory.production_units), 1)

    def test_factory_is_aware_of_time(self):
        factory = Factory()
        factory.run()
        assert_that(factory.time, is_(1))