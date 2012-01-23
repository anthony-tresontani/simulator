import core.entity

from unittest import TestCase

from core.entity import Entity
from core.production_unit import ProductionUnit

class TestEntities(TestCase):

    @classmethod
    def setUpClass(cls):
        core.entity.ref_counter = 1

    def setUp(self):
        self.pu = ProductionUnit(None)
        self.pu2 = ProductionUnit(None)

    def test_entities(self):
        self.assertEquals(self.pu.reference, 1)
        self.assertEquals(self.pu2.reference, 2)


    def test_get_by_ref(self):
        self.assertEquals(Entity.get_by_ref(self.pu.reference), self.pu)
