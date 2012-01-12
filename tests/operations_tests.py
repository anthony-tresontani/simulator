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

    def test_load_operation(self):
        load_op = LoadOperation(self.input, production_unit=self.machine, time_to_perform=3)

        load_op.perform(self.worker, during=1)
        self.assertEquals(len(self.machine.inputs), 1)

        load_op.perform(self.worker, during=2)
        self.assertEquals(len(self.machine.inputs), 3)

    def test_load_all_in_one_operation(self):
        load_op = AllInOneLoadOperation(self.input, production_unit=self.machine, time_to_perform=3)

        load_op.perform(self.worker, during=1)
        self.assertEquals(len(self.machine.inputs), 0)

        load_op.perform(self.worker, during=2)
        self.assertEquals(len(self.machine.inputs), 1)

    def test_produce_operation(self):
        StartOperation(production_unit=self.machine).perform(self.worker, during=1)
        LoadOperation(self.input, production_unit=self.machine, time_to_perform=1).perform(self.worker, during=1)
        produce_op = ProduceOperation(production_unit=self.machine)

        produce_op.perform(self.worker, during=1)
        self.assertEquals(len(self.machine.get_outputs()), 0)

        produce_op.perform(self.worker, during=3)
        self.assertEquals(len(self.machine.get_outputs()), 1)