import unittest
from core.operation import LoadOperation, StartOperation, StopOperation

from core.production_unit import ProductionUnit, CannotPerformOperation
from core.production_unit import IllegalStateToPerformAction, InvalidInputLoaded, CannotProduce, NoWorkerToPerformAction

from core.input import Input
from core.worker import Worker
from core.specification import Specification, InputConstraint, SkillConstraint
from core.event import Failure, Fix


class ProductionUnitTest(unittest.TestCase):
    def setUp(self):
        spec = Specification()
        spec.add(InputConstraint(type="yarn", quantity=1))
        self.gp = ProductionUnit(spec)
        self.worker = Worker()
        self.inputs = Input("yarn")

    def test_state_idle(self):
        self.assertEquals(self.gp.get_state(), ProductionUnit.IDLE)

    def test_cannot_start_without_worker(self):
        self.assertRaises(NoWorkerToPerformAction, self.gp.perform_operation, LoadOperation(self.inputs))

    def test_start_with_worker(self):
        self.gp.affect(self.worker)
        self.gp.perform_operation(StartOperation())
        self.assertEquals(self.gp.get_state(), ProductionUnit.STARTED)

    def test_stop_good_producer(self):
        self.gp.affect(self.worker)
        self.gp.perform_operation(StartOperation())

        self.gp.perform_operation(StopOperation())
        self.assertEquals(self.gp.get_state(), ProductionUnit.IDLE)

    def test_illegal_state(self):
        self.assertRaises(IllegalStateToPerformAction, self.gp.perform_operation, StopOperation())

    def test_produce_without_input(self):
        self.gp.affect(self.worker)
        self.gp.perform_operation(StartOperation())
        self.assertRaises(CannotProduce, self.gp.produce, 1)

    def test_produce_with_input(self):
        self.gp.affect(self.worker)
        self.gp.perform_operation(LoadOperation(self.inputs))

        self.gp.perform_operation(StartOperation())
        self.gp.produce(1)
        self.assertEquals(self.gp.get_state(), ProductionUnit.PRODUCING)

    def test_production_output(self):
        self.gp.affect(self.worker)
        self.gp.perform_operation(LoadOperation(self.inputs))

        self.gp.perform_operation(StartOperation())
        self.gp.produce(1)
        self.assertEquals(len(self.gp.get_outputs()), 1)

    def test_slower_machine(self):
        config = {'rate_by_minute': 0.5,
                  "input_types": [("yarn", 1)], }
        spec = Specification()
        spec.add(InputConstraint(type="yarn", quantity=1))

        slower_gp = ProductionUnit(spec, config)

        slower_gp.affect(self.worker)
        slower_gp.perform_operation(LoadOperation(self.inputs))

        slower_gp.perform_operation(StartOperation())
        slower_gp.produce(2)
        self.assertEquals(len(slower_gp.get_outputs()), 1)

    def test_invalid_input(self):
        input = Input("rocks")
        self.gp.affect(self.worker)
        self.assertRaises(InvalidInputLoaded, self.gp.perform_operation, LoadOperation(input))

    def test_out_of_stock(self):
        self.gp.affect(self.worker)
        self.gp.perform_operation(LoadOperation(self.inputs))

        self.gp.perform_operation(StartOperation())
        self.assertRaises(CannotProduce, self.gp.produce, 3)

    def test_multiple_inputs(self):
        config = {'rate_by_minute': 0.2}
        spec = Specification()
        spec.add(InputConstraint(type="flour", quantity=2))
        spec.add(InputConstraint(type="water", quantity=1))

        four_a_pain = ProductionUnit(spec, config)

        four_a_pain.affect(self.worker)
        four_a_pain.perform_operation(LoadOperation(Input("flour", 2)))
        four_a_pain.perform_operation(StartOperation())

        self.assertRaises(CannotProduce, four_a_pain.produce, 5)

    def test_complete_failure(self):
        self.gp.affect(self.worker)
        self.gp.perform_operation(LoadOperation(self.inputs))

        self.gp.perform_operation(StartOperation())
        self.gp.produce(1)
        self.gp.add_event(Failure())
        self.assertEquals(self.gp.get_state(), ProductionUnit.FAILURE)

        self.gp.add_event(Fix())
        self.assertEquals(self.gp.get_state(), ProductionUnit.STARTED)

    def test_technical_machine(self):
        spec = Specification()
        spec.add(InputConstraint(type="iron", quantity=1))

        start = StartOperation()
        start.add_constraint(SkillConstraint(skill_name="blacksmith"))

        self.assertRaises(CannotPerformOperation, self.gp.perform_operation, start)

