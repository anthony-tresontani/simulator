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
        self.affected_production_unit.affect(self.worker)

        self.inputs = Material("yarn")
        self.started_production_unit = ProductionUnit(spec)
        self.started_production_unit.affect(self.worker)
        StartOperation(production_unit=self.started_production_unit).perform(self.worker)

        self.loaded_production_unit = ProductionUnit(spec)
        self.loaded_production_unit.affect(self.worker)
        StartOperation(production_unit=self.loaded_production_unit).perform(self.worker)
        LoadOperation(self.inputs, production_unit=self.loaded_production_unit).perform(self.worker)

        config = {'rate_by_minute': 0.2}
        spec_four = Specification()
        spec_four.add(MaterialInputConstraint(Material(type="flour", quantity=2)))
        spec_four.add(MaterialInputConstraint(Material(type="water", quantity=1)))
        spec_four.add_output_material(Material("bread", 1))

        self.four_a_pain = ProductionUnit(spec_four, config)

        self.four_a_pain.affect(self.worker)
        LoadOperation(Material("flour", 2), production_unit=self.four_a_pain).perform(self.worker)
        StartOperation(production_unit=self.four_a_pain).perform(self.worker)

    def test_state_idle(self):
        self.assertEquals(self.unaffected_production_unit.get_state(), ProductionUnit.IDLE)

    def test_cannot_start_without_worker(self):
        self.assertRaises(NoWorkerToPerformAction, LoadOperation(self.inputs, self.unaffected_production_unit).perform)

    def test_start_with_worker(self):
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.STARTED)

    def test_stop_good_producer(self):
        StopOperation(self.started_production_unit).perform(self.worker)
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.IDLE)

    def test_illegal_state(self):
        self.assertRaises(IllegalStateToPerformAction, StopOperation(self.unaffected_production_unit).perform, self.worker)

    def test_produce_without_input(self):
        self.assertRaises(CannotProduce, ProduceOperation(production_unit=self.started_production_unit).perform, self.worker, during=1)

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
        spec.add(MaterialInputConstraint(Material(type="yarn", quantity=1)))
        spec.add_output_material(Material("twisted yarn", 1))

        slower_gp = ProductionUnit(spec, config)

        slower_gp.affect(self.worker)
        LoadOperation(self.inputs, slower_gp).perform(self.worker)

        StartOperation(slower_gp).perform(self.worker)
        ProduceOperation(slower_gp).perform(self.worker, during=2)
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
        spec.add(MaterialInputConstraint(Material(type="iron", quantity=1)))

        tech_production_unit = ProductionUnit(spec)

        start_op = StartOperation(tech_production_unit)
        start_op.add_constraint(SkillConstraint(skill_name="blacksmith"))

        worker = Worker()

        self.assertRaises(CannotPerformOperation, start_op.perform, worker)

        worker.skills.append("blacksmith")
        start_op.perform(worker)
        self.assertEquals(tech_production_unit.get_state(), ProductionUnit.STARTED)

    def test_produce_consume_inputs(self):
        self.four_a_pain.perform_operation(LoadOperation(Material("water", 1)))
        self.four_a_pain.perform_operation(ProduceOperation(5))
        self.assertRaises(CannotProduce, self.four_a_pain.perform_operation, ProduceOperation(5))


    def test_produce_right_output(self):
        self.four_a_pain.perform_operation(LoadOperation(Material("water", 1)))
        self.four_a_pain.perform_operation(ProduceOperation(5))
        self.assertEquals(self.four_a_pain.get_outputs()[0].type, "bread")

    def test_production_unit_with_stocking_area(self):
        stock_zone = StockingZone()
        self.loaded_production_unit.add_stocking_zone(stock_zone)

        self.loaded_production_unit.perform_operation(ProduceOperation(1))

        self.assertEquals(stock_zone.count(), 1)

    def test_production_unit_with_limited_stocking_area(self):
        stock_zone = StockingZone(size=3)
        self.loaded_production_unit.add_stocking_zone(stock_zone)

        self.loaded_production_unit.perform_operation(LoadOperation(Material("yarn", 10)))
        try:
            self.loaded_production_unit.perform_operation(ProduceOperation(5))
        except Event:
            pass

        self.assertEquals(stock_zone.count(), 3)
