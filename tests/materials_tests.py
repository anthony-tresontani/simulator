from unittest.case import TestCase
from core.material import Material
from core.specification import Specification, MaterialInputConstraint

class InputTest(TestCase):

    def setUp(self):
        self.input = Material("input", 3)

    def test_consume(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(Material("input", 2)))

        self.input.consume(spec)
        self.assertEquals(self.input.quantity, 1)

    def test_sum_material(self):
        sum_material = self.input + self.input	
        self.assertEquals(sum_material.type, "input")
        self.assertEquals(sum_material.quantity, 2 * self.input.quantity)

    def test_sum_different_type(self):
        other = Material("other", 2)
	sum_material = self.input + other
        self.assertEquals(sum_material, (self.input, other))
	
