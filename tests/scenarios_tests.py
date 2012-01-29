from pdb import set_trace
from unittest.case import TestCase, SkipTest
from core.event import Event, EventManager
from core.factory import Factory

from core.material import Material
from core.operation import StartOperation, LoadOperation, ProduceOperation, Process, UnloadOperation, ParallelProcess
from core.production_unit import ProductionUnit, StockingZone
from core.specification import Specification, MaterialInputConstraint
from core.worker import Worker
from tests.utils import create_machine

class TestScenario(TestCase):

    def setUp(self):
        self.machine, spec, self.stock_zone = create_machine(material_type_input="wood", material_type_output="plank")
        self.worker = Worker()
        StartOperation(production_unit=self.machine, time_to_perform=1, worker=self.worker).perform(during=1)

    def test_process_step_by_step(self):
        # load then produce then load, etc
        # 1 minute to load, 1 minute to produce 1, sequentially
        # leading to 30 produce in one hour
        load_op = LoadOperation(Material(type="wood", quantity=1), time_to_perform=1, production_unit=self.machine, worker=self.worker)
        product_op = ProduceOperation(production_unit=self.machine, worker=self.worker)

        operation_list = [load_op, product_op]
        process = Process(self.machine, operation_list)
        process.perform( 1)

        self.assertEquals(self.stock_zone.count(), 0)

        process.perform(1)
        self.assertEquals(self.stock_zone.count(), 1)

    def test_hour_of_production_scenario(self):
        # load then produce then load, etc
        # 1 minute to load, 1 minute to produce 1, sequentially
        # leading to 30 produce in one hour
        load_op = LoadOperation(Material(type="wood", quantity=1), production_unit=self.machine, worker=self.worker)
        product_op = ProduceOperation(production_unit=self.machine, worker=self.worker)

        operation_list = [load_op, product_op]
        process = Process(self.machine, operation_list)
        process.perform(60)

        self.assertEquals(self.stock_zone.count(), 30)

    def test_hour_of_production_scenario_with_more_load(self):
        # load then produce then load, etc
        # 1 minute to load 2, 2 minutes to produce 2, sequentially
        # leading to 40 produce in one hour
        load_op = LoadOperation(Material(type="wood", quantity=2), time_to_perform=1, production_unit=self.machine, worker=self.worker)
        product_op = ProduceOperation(production_unit=self.machine)

        operation_list = [load_op, product_op]
        process = Process(self.machine, operation_list)
        process.perform(60)

        self.assertEquals(self.stock_zone.count(), 40)

    def test_hour_of_production_with_unloading(self):
        # Load for 1 minute, produce for 1 minute, unload for 1 minute
        load_op = LoadOperation(Material(type="wood", quantity=1), time_to_perform=1, production_unit=self.machine, worker=self.worker)

        secondary_area = StockingZone()
        unload_op = UnloadOperation(quantity=1, zone=secondary_area, time_to_perform=1, production_unit=self.machine, worker=self.worker)
        product_op = ProduceOperation(production_unit=self.machine)

        operation_list = [load_op, product_op, unload_op]
        process = Process(self.machine, operation_list)
        process.perform(180)

        self.assertEquals(secondary_area.count(), 60)

    def test_parallel_process(self):
        load_op = LoadOperation(Material(type="wood", quantity=1), production_unit=self.machine, worker=self.worker)

        secondary_area = StockingZone()
        unload_op = UnloadOperation(quantity=10, zone=secondary_area, production_unit=self.machine, worker=self.worker)
        product_op = ProduceOperation(production_unit=self.machine, worker=self.worker)

        process_1_operations = [load_op, product_op]
        process_2_operations = [unload_op]
        process_1 = Process(self.machine, process_1_operations)
        process_2 = Process(self.machine, process_2_operations)

        main_process = ParallelProcess([process_1, process_2])
        main_process.perform(1)

        self.assertEquals(secondary_area.count(), 0)

        main_process.perform(3)
        self.assertEquals(secondary_area.count(), 2)

        main_process.perform(56)
        self.assertEquals(secondary_area.count(), 30)

    def test_chained_production_in_sequence(self):
        # Machine A -> Machine B
        machine_b, spec, stock_zone = create_machine(material_type_input="plank", material_type_output="furniture")
        machine_b.inputs_stocking_zone = self.machine.output_stocking_zone
        StartOperation(production_unit=machine_b, time_to_perform=1, worker=self.worker).perform(during=1)
        LoadOperation(Material(type="wood", quantity=1), production_unit=self.machine, worker=self.worker).perform()
        ProduceOperation(production_unit=self.machine, worker=self.worker).perform()
        ProduceOperation(production_unit=machine_b, worker=self.worker).perform()
        self.assertEquals(len(machine_b.get_outputs()), 1)

    def test_working_hour(self):
        eight_hour_worker = Worker(working_hour = 8 * 60)
        self.assertRaises(Event, LoadOperation(Material(type="wood", quantity=1), production_unit=self.machine, worker=eight_hour_worker).perform, during=8*60 + 1)

    def test_24_hours_shifts(self):
        factory = Factory()
        ev = EventManager(factory)
        ev.add_worker(Worker(working_hour = 8 * 60))
        ev.add_worker(Worker(working_hour = 8 * 60))
        ev.add_worker(Worker(working_hour = 8 * 60))
        raise SkipTest("Not implemented")
        factory.add_production_unit(self.machine)
        factory.run(24 * 60)
