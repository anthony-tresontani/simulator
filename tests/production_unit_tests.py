import unittest
from unittest.case import TestCase
from core.operation import LoadOperation, StartOperation, StopOperation, ProduceOperation

from core.production_unit import ProductionUnit, StockingZone

from core.material import Material
from core.worker import Worker
from core.specification import Specification, MaterialInputConstraint, SkillConstraint
from core.event import Failure, Fix, Event, NoWorkerToPerformAction, IllegalStateToPerformAction, InvalidInputLoaded, CannotPerformOperation
from tests.utils import create_machine


class ProductionUnitTest(unittest.TestCase):
    def setUp(self):
        self.unaffected_production_unit, spec, zone = create_machine(material_type_input="yarn")

        self.worker = Worker()
        self.affected_production_unit = ProductionUnit(spec)

        self.inputs = Material("yarn")
        self.started_production_unit = ProductionUnit(spec)
        self.started_production_unit.perform_next_operation(self.worker)

        self.loaded_production_unit = ProductionUnit(spec)
        self.loaded_production_unit.perform_next_operation(self.worker)
        self.loaded_production_unit.perform_next_operation(self.worker)

        config = {'rate_by_minute': 0.2}
        spec_four = Specification()
        spec_four.add(MaterialInputConstraint(Material(type="flour", quantity=2)))
        spec_four.add(MaterialInputConstraint(Material(type="water", quantity=1)))
        spec_four.add_output_material(Material("bread", 1))

        self.four_a_pain = ProductionUnit(spec_four, config)

        self.four_a_pain.perform_next_operation(self.worker)
        self.four_a_pain.perform_next_operation(self.worker)

    def test_state_idle(self):
        self.assertEquals(self.unaffected_production_unit.get_state(), ProductionUnit.IDLE)

    def test_cannot_start_without_worker(self):
        self.assertRaises(NoWorkerToPerformAction, LoadOperation(self.inputs, self.unaffected_production_unit).run)

    def test_start_state(self):
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.STARTED)

    def test_stop_operation_return_to_idle_state(self):
        StopOperation(self.started_production_unit, worker=self.worker).run()
        self.assertEquals(self.started_production_unit.get_state(), ProductionUnit.IDLE)

    def test_illegal_state(self):
        self.assertRaises(IllegalStateToPerformAction, StopOperation(self.unaffected_production_unit, worker=self.worker).run)

    def test_produce_without_input(self):
        self.assertRaises(InvalidInputLoaded, ProduceOperation(production_unit=self.started_production_unit, worker=self.worker).run, during=1)

    def test_produce_operation(self):
        ProduceOperation(self.loaded_production_unit, worker=self.worker).run()
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.PRODUCING)
        self.assertEquals(len(self.loaded_production_unit.get_outputs()), 1)
        self.assertEquals(self.loaded_production_unit.get_outputs()[0].type, "output")

    def test_slower_machine_configuration(self):
        slower_gp, spec, zone = create_machine(material_type_input="yarn", rate=0.5)
        slower_gp.perform_next_operation(self.worker)
        slower_gp.perform_next_operation(self.worker)

        ProduceOperation(slower_gp, worker=self.worker).run(during=2)
        self.assertEquals(len(slower_gp.get_outputs()), 1)

    def test_invalid_input(self):
        input = Material("rocks")
        self.assertRaises(InvalidInputLoaded,
            LoadOperation(input, production_unit=self.affected_production_unit, worker=self.worker).run)

    def test_out_of_stock(self):
        self.assertRaises(InvalidInputLoaded, ProduceOperation(self.loaded_production_unit, worker=self.worker).run, during=3)

    def test_multiple_inputs(self):
        self.assertRaises(InvalidInputLoaded, ProduceOperation(self.four_a_pain,worker=self.worker).run, during=5)

    def test_complete_failure(self):
        ProduceOperation(production_unit=self.loaded_production_unit, worker=self.worker).run()
        self.loaded_production_unit.add_event(Failure())
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.FAILURE)

        self.loaded_production_unit.add_event(Fix())
        self.assertEquals(self.loaded_production_unit.get_state(), ProductionUnit.STARTED)

    def test_add_skill_constraint_to_operation(self):
        tech_production_unit, spec, zone = create_machine(material_type_input="iron")

        start_op = StartOperation(tech_production_unit, worker=self.worker)
        start_op.add_constraint(SkillConstraint(skill_name="blacksmith"))

        self.assertRaises(CannotPerformOperation, start_op.run)

        blacksmith = Worker()
        blacksmith.skills.append("blacksmith")
        StartOperation(tech_production_unit, worker=blacksmith).run()
        self.assertEquals(tech_production_unit.get_state(), ProductionUnit.STARTED)

    def test_produce_consume_inputs(self):
        LoadOperation(Material("water", 1), self.four_a_pain, worker=self.worker).run()
        ProduceOperation(self.four_a_pain, worker=self.worker).run(during=5)
        self.assertRaises(InvalidInputLoaded, ProduceOperation(self.four_a_pain, worker=self.worker).run, during=5)

    def test_production_unit_with_stocking_area(self):
        stock_zone = StockingZone()
        self.loaded_production_unit.output_stocking_zone = stock_zone

        ProduceOperation(self.loaded_production_unit, worker=self.worker).run()

        self.assertEquals(stock_zone.count(), 1)

    def test_production_unit_with_limited_stocking_area(self):
        stock_zone = StockingZone(size=3)
        self.loaded_production_unit.output_stocking_zone = stock_zone

        LoadOperation(Material("yarn", 10), self.loaded_production_unit, worker=self.worker).run()
        try:
            ProduceOperation(self.loaded_production_unit, worker=self.worker).run(during=5)
        except Event:
            pass

        self.assertEquals(stock_zone.count(), 3)

class TestProtocol(TestCase):

    def test_production_unit_create_a_protocol(self):
        self.machine, spec, zone = create_machine(material_type_input="yarn")
        self.assertEquals(self.machine.protocol.next(), StartOperation(production_unit=self.machine))
        self.assertEquals(self.machine.protocol.next(), LoadOperation(Material("yarn"), production_unit=self.machine))
        self.assertEquals(self.machine.protocol.next(), ProduceOperation(production_unit=self.machine))

class TestStock(unittest.TestCase):

    def test_count(self):
        stock_zone = StockingZone()
        stock_zone.add_to_stock(Material("something", 2))
        stock_zone.add_to_stock(Material("something", 1))
        stock_zone.add_to_stock(Material("other", 4))
        self.assertEquals(stock_zone.count(), 7)