import unittest
from core.operation import LoadOperation, StartOperation, StopOperation, ProduceOperation

from core.production_unit import ProductionUnit, CannotPerformOperation, StockingZone, Event
from core.production_unit import IllegalStateToPerformAction, InvalidInputLoaded, CannotProduce, NoWorkerToPerformAction

from core.material import Material
from core.worker import Worker
from core.specification import Specification, MaterialInputConstraint, SkillConstraint
from core.event import Failure, Fix


class ProductionUnitTest(unittest.TestCase):
    def setUp(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(Material(type="yarn", quantity=1)))
        spec.add_output_material(Material("whatever", 1))
        self.unaffected_production_unit = ProductionUnit(spec)

        self.worker = Worker()
        self.affected_production_unit = ProductionUnit(spec)

        self.inputs = Material("yarn")
        self.started_production_unit = ProductionUnit(spec)
        StartOperation(production_unit=self.started_production_unit).perform(self.worker)

        self.loaded_production_unit = ProductionUnit(spec)
        StartOperation(production_unit=self.loaded_production_unit).perform(self.worker)
        LoadOperation(self.inputs, production_unit=self.loaded_production_unit).perform(self.worker)

        config = {'rate_by_minute': 0.2}
        spec_four = Specification()
        spec_four.add(MaterialInputConstraint(Material(type="flour", quantity=2)))
        spec_four.add(MaterialInputConstraint(Material(type="water", quantity=1)))
        spec_four.add_output_material(Material("bread", 1))

        self.four_a_pain = ProductionUnit(spec_four, config)

        LoadOperation(Material("flour", 2), production_unit=self.four_a_pain).perform(self.worker)
        StartOperation(production_unit=self.four_a_pain).perform(self.worker)

    def test_state_idle(self):
        self.assertEquals(self.unaffected_production_unit.get_state(), ProductionUnit.IDLE)

    def test_cannot_start_without_worker(self):
        self.assertRaises(NoWorkerToPerformAction, LoadOperation(self.inputs, self.unaffected_production_unit).perform, None)

    def test_start_state(self):
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.STARTED)

    def test_stop_operation_return_to_idle_state(self):
        StopOperation(self.started_production_unit).perform(self.worker)
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.IDLE)

    def test_illegal_state(self):
        self.assertRaises(IllegalStateToPerformAction, StopOperation(self.unaffected_production_unit).perform, self.worker)

    def test_produce_without_input(self):
        self.assertRaises(CannotProduce, ProduceOperation(production_unit=self.started_production_unit).perform, self.worker, during=1)

    def test_produce_operation(self):
	ProduceOperation(self.loaded_production_unit).perform(self.worker)
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.PRODUCING)
	self.assertEquals(len(self.loaded_production_unit.get_outputs()), 1)
	self.assertEquals(self.loaded_production_unit.get_outputs()[0].type, "whatever")

    def test_slower_machine_configuration(self):
        config = {'rate_by_minute': 0.5,
                  "input_types": [("yarn", 1)], }
        spec = Specification()
        spec.add(MaterialInputConstraint(Material(type="yarn", quantity=1)))
        spec.add_output_material(Material("twisted yarn", 1))

        slower_gp = ProductionUnit(spec, config)

        LoadOperation(self.inputs, slower_gp).perform(self.worker)

        StartOperation(slower_gp).perform(self.worker)
        ProduceOperation(slower_gp).perform(self.worker, during=2)
        self.assertEquals(len(slower_gp.get_outputs()), 1)

    def test_invalid_input(self):
        input = Material("rocks")
        self.assertRaises(InvalidInputLoaded, LoadOperation(input, production_unit=self.affected_production_unit).perform, self.worker)

    def test_out_of_stock(self):
        self.assertRaises(CannotProduce, ProduceOperation(self.loaded_production_unit).perform, self.worker, during=3)

    def test_multiple_inputs(self):
        self.assertRaises(CannotProduce, ProduceOperation(self.four_a_pain).perform, self.worker, during=5)

    def test_complete_failure(self):
	ProduceOperation(production_unit=self.loaded_production_unit).perform(self.worker)
        self.loaded_production_unit.add_event(Failure())
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.FAILURE)

        self.loaded_production_unit.add_event(Fix())
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.STARTED)

    def test_add_skill_constraint_to_operation(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(Material(type="iron", quantity=1)))

        tech_production_unit = ProductionUnit(spec)

        start_op = StartOperation(tech_production_unit)
        start_op.add_constraint(SkillConstraint(skill_name="blacksmith"))

        worker = Worker()

        self.assertRaises(CannotPerformOperation, start_op.perform, worker)

	blacksmith = Worker()
        blacksmith.skills.append("blacksmith")
        start_op.perform(blacksmith)
        self.assertEquals(tech_production_unit.get_state(), ProductionUnit.STARTED)

    def test_produce_consume_inputs(self):
	LoadOperation(Material("water", 1), self.four_a_pain).perform(self.worker)
	ProduceOperation(self.four_a_pain).perform(self.worker, during=5)
        self.assertRaises(CannotProduce, ProduceOperation(self.four_a_pain).perform, self.worker, during=5)

    def test_production_unit_with_stocking_area(self):
        stock_zone = StockingZone()
        self.loaded_production_unit.add_stocking_zone(stock_zone)

	ProduceOperation(self.loaded_production_unit).perform(self.worker)

        self.assertEquals(stock_zone.count(), 1)

    def test_production_unit_with_limited_stocking_area(self):
        stock_zone = StockingZone(size=3)
        self.loaded_production_unit.add_stocking_zone(stock_zone)

	LoadOperation(Material("yarn", 10), self.loaded_production_unit).perform(self.worker)
        try:
	    ProduceOperation(self.loaded_production_unit).perform(self.worker, during=5)
        except Event:
            pass

        self.assertEquals(stock_zone.count(), 3)
