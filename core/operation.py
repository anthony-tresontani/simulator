import copy
from core.material import Material
from core.output import Output
from core.production_unit import IllegalStateToPerformAction, ProductionUnit, NoWorkerToPerformAction, InvalidInputLoaded, CannotPerformOperation, ProductionUnitSTARTEDState, ProductionUnitIDLEState, CannotProduce, ProductionUnitPRODUCINGState

class Operation(object):
    def __init__(self, production_unit=None, time_to_perform=0):
        self.production_unit = production_unit
        self.constraints = []
        self.time_to_perform = time_to_perform
        self.elapsed_time = 0

    def get_elapsed_time(self):
        return self.time_to_perform

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def check_all(self):
        self.check_valid_state()
        if hasattr(self, "check"):
            self.check()

    def check_valid_state(self):
        if not self.production_unit.get_state() in self.valid_state:
            raise IllegalStateToPerformAction()

    def check_constraints(self):
        for constraint in self.constraints:
            if not constraint.validate(self.production_unit):
                raise CannotPerformOperation(constraint.get_message())


class LoadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, inputs, production_unit=None, time_to_perform=0):
        self.inputs = inputs
        super(LoadOperation, self).__init__(production_unit, time_to_perform)

    def check(self):
        if not self.production_unit.worker:
            raise NoWorkerToPerformAction()
        if not self.production_unit.spec.validate_any(self.inputs):
            raise InvalidInputLoaded()

    def perform(self):
        self.production_unit.inputs.append(copy.copy(self.inputs))


class UnloadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, quantity, zone, *args, **kwargs):
        self.quantity = quantity
        self.zone = zone
        super(UnloadOperation, self).__init__(*args, **kwargs)

    def perform(self):
        for i in range(self.quantity):
            outputs = self.production_unit.stocking_zone.stock
            if outputs:
                self.zone.add_to_stock(outputs.pop())
        self.elapsed_time = 1

    def get_elapsed_time(self):
        return self.elapsed_time

class StartOperation(Operation):
    valid_state = [ProductionUnit.IDLE]

    def check(self):pass

    def perform(self):
        for constraint in self.constraints:
            if not constraint.validate(self.production_unit):
                raise CannotPerformOperation()
        self.production_unit.set_state(ProductionUnitSTARTEDState)


class ProduceOperation(Operation):
    valid_state = [ProductionUnit.STARTED, ProductionUnit.PRODUCING]

    def __init__(self, production_time=None, production_unit=None):
        self.production_time = production_time
        self.infinite_production_time = self.production_time is None
        self.progress = 0
        super(ProduceOperation, self).__init__(production_unit)

    def check(self):pass

    def do_step(self, inputs, spec):
        self.progress += self.production_unit.rate
        if self.progress == 1:
            for input in inputs:
                input.consume(spec)
            self.production_unit.set_output(spec.output_materials)
            self.progress = 0


    def perform(self):
        self.elapsed_time = 0
        if not self.production_unit.get_state() == ProductionUnit.PRODUCING:
            self.production_unit.set_state(ProductionUnitPRODUCINGState)

        inputs = self.production_unit.inputs
        spec = self.production_unit.spec
        while self.infinite_production_time or self.production_time > 0:
            if not spec.validate_all(inputs):
                self.production_unit.set_state(ProductionUnitSTARTEDState)
                raise CannotProduce()

            self.do_step(inputs, spec)

            self.elapsed_time += 1
            if self.production_time:
                self.production_time -= 1

    def get_elapsed_time(self):
        return self.elapsed_time

class StopOperation(Operation):
    valid_state = [ProductionUnit.STARTED]
    def check(self):pass

    def perform(self):
        self.production_unit.set_state(ProductionUnitIDLEState)

class Process(object):

    def __init__(self, production_unit, operations):
        self.production_unit = production_unit
        self.operations = operations
        self.progress = 0

    def run(self, time):
        progress = self.progress
        import pdb; pdb.set_trace()
        while time >0:
            for operation in self.operations[self.progress:]:
                print "operation", operation
                if time >0:
                    try:
                        self.production_unit.perform_operation(operation)
                    except CannotProduce:
                        pass
                    time -= 1
                    progress +=1
        self.progress = (self.progress + 1) %  len(self.operations)

class MainProcess(object):
    def __init__(self, process_list):
        self.processes = process_list

    def run(self, time):
        for time in range(time):
            print "time", time
            for index, process in enumerate(self.processes):
                print "process", process, "index", index
                process.run(1)
