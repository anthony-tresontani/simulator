from unittest import TestCase

from core.specification import Specification, InputConstraint
from core.input import Input

class SpecificationTest(TestCase):

    def test_validate_all_spec(self):
	spec = Specification()
        spec.add(InputConstraint(type="flour", quantity=1))
	spec.add(InputConstraint(type="water", quantity=2))

	input1 = Input("flour", quantity=3)
	input2 = Input("water", quantity=2)
	input3 = Input("water", quantity=1)
 	self.assertFalse(spec.validate_all([input1]))
 	self.assertFalse(spec.validate_all([input1, input3]))
 	self.assertTrue(spec.validate_all([input1, input2]))
