from unittest.case import TestCase

from core.material import Material
from core.operation import StartOperation, LoadOperation, ProduceOperation, Process, UnloadOperation, ParallelProcess
from core.production_unit import ProductionUnit, CannotProduce, StockingZone
from core.specification import Specification, MaterialInputConstraint
from core.worker import Worker

class TestScenario(TestCase):

    def setUp(self):
        spec = Specification()
        spec.add(MaterialInputConstraint(Material(type="input", quantity=1)))
        spec.add_output_material(Material(type="transformed", quantity=1))
        self.machine = ProductionUnit(spec)
        self.stock_zone = StockingZone(size=40)
        self.machine.add_stocking_zone(self.stock_zone)
        self.worker = Worker()
        StartOperation(production_unit=self.machine, time_to_perform=1).perform(self.worker, during=1)

    def test_process_step_by_step(self):
        # load then produce then load, etc
        # 1 minute to load, 1 minute to produce 1, sequentially
        # leading to 30 produce in one hour
        load_op = LoadOperation(Material(type="input", quantity=1), time_to_perform=1, production_unit=self.machine)
        product_op = ProduceOperation(production_unit=self.machine)

        operation_list = [load_op, product_op]
        process = Process(self.machine, operation_list)
        process.perform(self.worker, 1)

        self.assertEquals(self.stock_zone.count(), 0)

        process.perform(self.worker, 1)
        self.assertEquals(self.stock_zone.count(), 1)

    def test_hour_of_production_scenario(self):
        # load then produce then load, etc
        # 1 minute to load, 1 minute to produce 1, sequentially
        # leading to 30 produce in one hour
        load_op = LoadOperation(Material(type="input", quantity=1), production_unit=self.machine)
        product_op = ProduceOperation(production_unit=self.machine)

        operation_list = [load_op, product_op]
        process = Process(self.machine, operation_list)
        process.perform(self.worker, 60)

        self.assertEquals(self.stock_zone.count(), 30)

    def test_hour_of_production_scenario_with_more_load(self):
        # load then produce then load, etc
        # 1 minute to load 2, 2 minutes to produce 2, sequentially
        # leading to 40 produce in one hour
        load_op = LoadOperation(Material(type="input", quantity=2), time_to_perform=1, production_unit=self.machine)
        product_op = ProduceOperation(production_unit=self.machine)

        operation_list = [load_op, product_op]
        process = Process(self.machine, operation_list)
        process.perform(self.worker, 60)

        self.assertEquals(self.stock_zone.count(), 40)

    def test_hour_of_production_with_unloading(self):
        # Load for 1 minute, produce for 1 minute, unload for 1 minute
        load_op = LoadOperation(Material(type="input", quantity=1), time_to_perform=1, production_unit=self.machine)

        secondary_area = StockingZone()
        unload_op = UnloadOperation(quantity=1, zone=secondary_area, time_to_perform=1, production_unit=self.machine)
        product_op = ProduceOperation(production_unit=self.machine)

        operation_list = [load_op, product_op, unload_op]
        process = Process(self.machine, operation_list)
        process.perform(self.worker, 180)

        self.assertEquals(secondary_area.count(), 60)

    def test_parallel_process(self):
        load_op = LoadOperation(Material(type="input", quantity=1), production_unit=self.machine)

        secondary_area = StockingZone()
        unload_op = UnloadOperation(quantity=10, zone=secondary_area, production_unit=self.machine)
        product_op = ProduceOperation(production_unit=self.machine)

        process_1_operations = [load_op, product_op]
        process_2_operations = [unload_op]
        process_1 = Process(self.machine, process_1_operations)
        process_2 = Process(self.machine, process_2_operations)

        main_process = ParallelProcess([process_1, process_2])
        main_process.perform(self.worker, 1)

        self.assertEquals(secondary_area.count(), 0)

        main_process.perform(self.worker, 3)
        self.assertEquals(secondary_area.count(), 2)

        main_process.perform(self.worker, 56)
        self.assertEquals(secondary_area.count(), 30)
