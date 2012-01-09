from unittest.case import TestCase
from core.material import Material
from core.specification import Specification, MaterialInputConstraint

class InputTest(TestCase):

    def test_consume(self):
        input = Material("input", 3)
        spec = Specification()
        spec.add(MaterialInputConstraint("input", 2))

        input.consume(spec)
        self.assertEquals(input.quantity, 1)