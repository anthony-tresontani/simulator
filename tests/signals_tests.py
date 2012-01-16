from unittest import TestCase

from core.production_unit import ProductionUnit

class TestSignals(TestCase):

    def test_signals_generated(self):
	pu = ProductionUnit(None)
