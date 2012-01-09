from unittest.case import TestCase

from core.material import Material
from core.operation import StartOperation, LoadOperation, ProduceOperation, Process
from core.production_unit import ProductionUnit, CannotProduce
from core.specification import Specification, MaterialInputConstraint
from core.worker import Worker

class TestScenario(TestCase):

    def setUp(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(type="input", quantity=1))
        spec.add_output_material(Material(type="transformed", quantity=1))
        self.machine = ProductionUnit(spec)
        worker = Worker()
        self.machine.affect(worker)
        self.machine.perform_operation(StartOperation())

    def test_hour_of_production_scenario(self):
        # load then produce then load, etc
        # 1 minute to load, 1 minute to produce 1, sequentially
        # leading to 30 produce in one hour
        load_op = LoadOperation(Material(type="input", quantity=1), time_to_perform=1)
        produce_op = ProduceOperation()
        operation_list = [load_op, ProduceOperation()]
        process = Process(self.machine, operation_list)
        process.run(60)

        self.assertEquals(len(self.machine.get_outputs()), 30)

    def test_hour_of_production_scenario_with_more_load(self):
        # load then produce then load, etc
        # 1 minute to load, 1 minute to produce 1, sequentially
        # leading to 30 produce in one hour
        load_op = LoadOperation(Material(type="input", quantity=2), time_to_perform=1)
        produce_op = ProduceOperation()
        operation_list = [load_op, ProduceOperation()]
        process = Process(self.machine, operation_list)
        process.run(60)

        self.assertEquals(len(self.machine.get_outputs()), 40)