import unittest
from core.operation import LoadOperation, StartOperation, StopOperation, ProduceOperation

from core.production_unit import ProductionUnit, CannotPerformOperation
from core.production_unit import IllegalStateToPerformAction, InvalidInputLoaded, CannotProduce, NoWorkerToPerformAction

from core.material import Material
from core.worker import Worker
from core.specification import Specification, MaterialInputConstraint, SkillConstraint
from core.event import Failure, Fix


class ProductionUnitTest(unittest.TestCase):
    def setUp(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(type="yarn", quantity=1))
        spec.add_output_material(Material("whatever", 1))
        self.unaffected_production_unit = ProductionUnit(spec)

        self.worker = Worker()
        self.affected_production_unit = ProductionUnit(spec)
        self.affected_production_unit.affect(self.worker)

        self.inputs = Material("yarn")
        self.started_production_unit = ProductionUnit(spec)
        self.started_production_unit.affect(self.worker)
        self.started_production_unit.perform_operation(StartOperation())

        self.loaded_production_unit = ProductionUnit(spec)
        self.loaded_production_unit.affect(self.worker)
        self.loaded_production_unit.perform_operation(StartOperation())
        self.loaded_production_unit.perform_operation(LoadOperation(self.inputs))

        config = {'rate_by_minute': 0.2}
        spec = Specification()
        spec.add(MaterialInputConstraint(type="flour", quantity=2))
        spec.add(MaterialInputConstraint(type="water", quantity=1))
        spec.add_output_material(Material("bread", 1))

        self.four_a_pain = ProductionUnit(spec, config)

        self.four_a_pain.affect(self.worker)
        self.four_a_pain.perform_operation(LoadOperation(Material("flour", 2)))
        self.four_a_pain.perform_operation(StartOperation())

    def test_state_idle(self):
        self.assertEquals(self.unaffected_production_unit.get_state(), ProductionUnit.IDLE)

    def test_cannot_start_without_worker(self):
        self.assertRaises(NoWorkerToPerformAction, self.unaffected_production_unit.perform_operation, LoadOperation(self.inputs))

    def test_start_with_worker(self):
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.STARTED)

    def test_stop_good_producer(self):
        self.started_production_unit.perform_operation(StopOperation())
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.IDLE)

    def test_illegal_state(self):
        self.assertRaises(IllegalStateToPerformAction, self.unaffected_production_unit.perform_operation, StopOperation())

    def test_produce_without_input(self):
        produce = ProduceOperation(1)
        self.assertRaises(CannotProduce, self.started_production_unit.perform_operation, produce)

    def test_produce_with_input(self):
        self.loaded_production_unit.perform_operation(ProduceOperation(1))
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.PRODUCING)

    def test_production_output(self):
        self.loaded_production_unit.perform_operation(ProduceOperation(1))
        self.assertEquals(len(self.loaded_production_unit.get_outputs()), 1)

    def test_slower_machine(self):
        config = {'rate_by_minute': 0.5,
                  "input_types": [("yarn", 1)], }
        spec = Specification()
        spec.add(MaterialInputConstraint(type="yarn", quantity=1))
        spec.add_output_material(Material("twisted yarn", 1))

        slower_gp = ProductionUnit(spec, config)

        slower_gp.affect(self.worker)
        slower_gp.perform_operation(LoadOperation(self.inputs))

        slower_gp.perform_operation(StartOperation())
        slower_gp.perform_operation(ProduceOperation(2))
        self.assertEquals(len(slower_gp.get_outputs()), 1)

    def test_invalid_input(self):
        input = Material("rocks")
        self.assertRaises(InvalidInputLoaded, self.affected_production_unit.perform_operation, LoadOperation(input))

    def test_out_of_stock(self):
        self.assertRaises(CannotProduce, self.loaded_production_unit.perform_operation, ProduceOperation(3))

    def test_multiple_inputs(self):
        self.assertRaises(CannotProduce, self.four_a_pain.perform_operation, ProduceOperation(5))

    def test_complete_failure(self):
        self.loaded_production_unit.perform_operation(ProduceOperation(1))
        self.loaded_production_unit.add_event(Failure())
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.FAILURE)

        self.loaded_production_unit.add_event(Fix())
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.STARTED)

    def test_technical_machine(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(type="iron", quantity=1))

        start = StartOperation()
        start.add_constraint(SkillConstraint(skill_name="blacksmith"))

        tech_production_unit = ProductionUnit(spec)
        tech_production_unit.affect(Worker())

        self.assertRaises(CannotPerformOperation, tech_production_unit.perform_operation, start)

        tech_production_unit.worker.skills.append("blacksmith")
        tech_production_unit.perform_operation(start)
        self.assertEquals(tech_production_unit.get_state(), ProductionUnit.STARTED)

    def test_produce_consume_inputs(self):
        self.four_a_pain.perform_operation(LoadOperation(Material("water", 1)))
        self.four_a_pain.perform_operation(ProduceOperation(5))
        self.assertRaises(CannotProduce, self.four_a_pain.perform_operation, ProduceOperation(5))


    def test_produce_right_output(self):
        self.four_a_pain.perform_operation(LoadOperation(Material("water", 1)))
        self.four_a_pain.perform_operation(ProduceOperation(5))
        self.assertEquals(self.four_a_pain.get_outputs()[0].type, "bread")