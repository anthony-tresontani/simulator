from unittest import TestCase

from core.specification import Specification, MaterialInputConstraint
from core.material import Material

class SpecificationTest(TestCase):

    def setUp(self):
        self.spec = Specification()
        self.spec.add(MaterialInputConstraint(Material(type="flour", quantity=1)))
        self.spec.add(MaterialInputConstraint(Material(type="water", quantity=2)))

    def test_validate_all_spec(self):
        input1 = Material("flour", quantity=3)
        input2 = Material("water", quantity=2)
        input3 = Material("water", quantity=1)
        self.assertFalse(self.spec.validate_all([input1]))
        self.assertFalse(self.spec.validate_all([input1, input3]))
        self.assertTrue(self.spec.validate_all([input1, input2]))

    def test_str(self):
        self.assertEquals(self.spec.__str__(), "Validate input is type of flour\nValidate input is type of water")

    def test_get_inputs(self):
        self.assertEquals(self.spec.get_inputs()[0], Material("flour", 1))
        self.assertEquals(self.spec.get_inputs()[1], Material("water", 2))