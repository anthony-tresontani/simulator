from unittest.case import TestCase
from core.material import Material
from core.operation import LoadOperation, ProduceOperation, StartOperation, AllInOneLoadOperation
from core.production_unit import ProductionUnit
from core.specification import MaterialInputConstraint, Specification
from core.worker import Worker

class TestOperation(TestCase):

    def setUp(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(Material(type="wood", quantity=1)))
        spec.add_output_material(Material("Furniture", 1))
        self.machine = ProductionUnit(spec, config={"rate_by_minute":0.25})
        self.worker = Worker()
        self.input = Material("wood", quantity=3)

    def test_equals(self):
        self.assertEquals(StartOperation(self.machine, self.worker), StartOperation(self.machine, self.worker))

    def test_load_equals(self):
        op1 = LoadOperation(Material("input"),self.machine, self.worker)
        op2 = LoadOperation(Material("other"),self.machine, self.worker)
        op3 = LoadOperation(Material("input"),self.machine, self.worker)
        self.assertFalse(op1==op2)
        self.assertEquals(op1, op3)

    def test_load_operation(self):
        load_op = LoadOperation(self.input, production_unit=self.machine, time_to_perform=3, worker=self.worker)

        load_op.perform(during=1)
        self.assertEquals(self.machine.inputs.count(), 1)

        load_op.perform(during=2)
        self.assertEquals(self.machine.inputs.count(), 3)

    def test_load_all_in_one_operation(self):
        load_op = AllInOneLoadOperation(self.input, production_unit=self.machine, time_to_perform=3, worker=self.worker)

        load_op.perform(during=1)
        self.assertEquals(self.machine.inputs.count(), 0)

        load_op.perform(during=2)
        self.assertEquals(self.machine.inputs.count(), 3)

    def test_produce_operation(self):
        StartOperation(production_unit=self.machine,worker=self.worker).perform(during=1)
        LoadOperation(self.input, production_unit=self.machine, time_to_perform=1, worker=self.worker).perform(during=1)
        produce_op = ProduceOperation(production_unit=self.machine)

        produce_op.perform(during=1)
        self.assertEquals(len(self.machine.get_outputs()), 0)

        produce_op.perform(during=3)
        self.assertEquals(len(self.machine.get_outputs()), 1)
