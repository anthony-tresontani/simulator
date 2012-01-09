from unittest import TestCase

from core.specification import Specification, InputConstraint
from core.input import Input

class SpecificationTest(TestCase):

    def setUp(self):
        self.spec = Specification()
        self.spec.add(InputConstraint(type="flour", quantity=1))
        self.spec.add(InputConstraint(type="water", quantity=2))

    def test_validate_all_spec(self):
        input1 = Input("flour", quantity=3)
        input2 = Input("water", quantity=2)
        input3 = Input("water", quantity=1)
        self.assertFalse(self.spec.validate_all([input1]))
        self.assertFalse(self.spec.validate_all([input1, input3]))
        self.assertTrue(self.spec.validate_all([input1, input2]))

    def test_str(self):
        self.assertEquals(self.spec.__str__(), "Validate input is type of flour\nValidate input is type of water")
