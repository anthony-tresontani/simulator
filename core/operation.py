import copy
import logging

from core.production_unit import IllegalStateToPerformAction, ProductionUnit, NoWorkerToPerformAction, \
    InvalidInputLoaded, CannotPerformOperation, ProductionUnitSTARTEDState, ProductionUnitIDLEState, \
    CannotProduce, ProductionUnitPRODUCINGState

logger = logging.getLogger()


class OperationalConstraint(object):
    def __init__(self, operation):
        self.operation = operation

class HasWorkerConstraint(OperationalConstraint):
    def validate(self, worker=None):
        if not worker:
            raise NoWorkerToPerformAction()

class InputValidForSpecConstraint(OperationalConstraint):
    def validate(self, worker=None):
        if not self.operation.production_unit.spec.validate_any(self.operation.inputs):
            raise InvalidInputLoaded()


class Operation(object):
    def __init__(self, production_unit=None, time_to_perform=0):
        self.production_unit = production_unit
        self.constraints = []
        self.time_to_perform = time_to_perform
        self.elapsed_time = 0
        self.progress = 0

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def check_all(self, worker=None):
        self.check_valid_state()
        self.check_constraints()
        if hasattr(self, "static_constraints"):
            self.check_static_constraints(worker)
        if hasattr(self, "check"):
            self.check(worker)

    def check_valid_state(self):
        if not self.production_unit.get_state() in self.valid_state:
            raise IllegalStateToPerformAction("State %s" % self.production_unit.get_state())

    def check_constraints(self):
        for constraint in self.constraints:
            if not constraint.validate(self.production_unit):
                raise CannotPerformOperation(constraint.get_message())

    def check_static_constraints(self, worker):
        for constraint in self.static_constraints:
            constraint(self).validate(worker)

    def perform(self, worker, during=1):
        self.check_all(worker)
        for i in range(during):
            self.do_step(worker)


class UnFragmentableOperation(Operation):

    def do_step(self, worker):
        self.progress += 1
        if self.progress == self.time_to_perform:
            self.do_complete_step(worker)

class LoadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]
    static_constraints = [HasWorkerConstraint, InputValidForSpecConstraint]

    def __init__(self, inputs, *args, **kwargs):
        self.inputs = inputs
        super(LoadOperation, self).__init__(*args, **kwargs)

    def check(self, worker=None):
        if not worker:
            raise NoWorkerToPerformAction()
        if not self.production_unit.spec.validate_any(self.inputs):
            raise InvalidInputLoaded()

    def do_step(self, worker):
        input = copy.copy(self.inputs)
        input.quantity = self.inputs.quantity / self.time_to_perform
        self.production_unit.inputs.append(input)

class AllInOneLoadOperation(UnFragmentableOperation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, inputs, all_in_one=False, *args, **kwargs):
        self.inputs = inputs
        super(AllInOneLoadOperation, self).__init__(*args, **kwargs)

    def check(self, worker=None):
        if not worker:
            raise NoWorkerToPerformAction()
        if not self.production_unit.spec.validate_any(self.inputs):
            raise InvalidInputLoaded()

    def do_complete_step(self, worker):
        input = copy.copy(self.inputs)
        self.production_unit.inputs.append(input)

class UnloadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, quantity, zone, *args, **kwargs):
        self.quantity = quantity
        self.zone = zone
        super(UnloadOperation, self).__init__(*args, **kwargs)

    def perform(self, worker, during=1):
        for i in range(self.quantity):
            outputs = self.production_unit.stocking_zone.stock
            if outputs:
                self.zone.add_to_stock(outputs.pop())
        self.elapsed_time = 1

    def get_elapsed_time(self):
        return self.elapsed_time

class StartOperation(Operation):
    valid_state = [ProductionUnit.IDLE]

    def do_step(self, *args, **kwargs):
        self.production_unit.set_state(ProductionUnitSTARTEDState)


class ProduceOperation(Operation):
    valid_state = [ProductionUnit.STARTED, ProductionUnit.PRODUCING]

    def __init__(self, production_time=None, *args, **kwargs):
        self.production_time = production_time
        self.infinite_production_time = self.production_time is None
        self.progress = 0
        super(ProduceOperation, self).__init__(*args, **kwargs)

    def do_step(self, worker):
        if not self.production_unit.get_state() == ProductionUnit.PRODUCING:
            self.production_unit.set_state(ProductionUnitPRODUCINGState)

        inputs = self.production_unit.inputs
        spec = self.production_unit.spec
        if not spec.validate_all(inputs):
            self.production_unit.set_state(ProductionUnitSTARTEDState)
            raise CannotProduce()

        self.progress += self.production_unit.rate
        if self.progress == 1:
            for input in inputs:
                input.consume(spec)
            self.production_unit.set_output(spec.output_materials)
            self.progress = 0

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
        while time >0:
            for operation in self.operations[self.progress:]:
                logger.debug("Running operation %s at %s" % ( operation, time))
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
            for index, process in enumerate(self.processes):
                logger.debug("%d-Running process %s at %s" % (index, process, time))
                process.run(1)