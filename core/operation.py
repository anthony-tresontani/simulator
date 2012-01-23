import copy
import logging
from types import MethodType
from core.constraint import HasWorkerConstraint, InputValidForSpecConstraint

from core.production_unit import IllegalStateToPerformAction, ProductionUnit, NoWorkerToPerformAction,\
    InvalidInputLoaded, CannotPerformOperation, ProductionUnitSTARTEDState, ProductionUnitIDLEState,\
    CannotProduce, ProductionUnitPRODUCINGState

logger = logging.getLogger()


class Operation(object):
    def __init__(self, production_unit=None, time_to_perform=1, worker=None):
        self.production_unit = production_unit
        self.constraints = []
        self.time_to_perform = time_to_perform
        self.elapsed_time = 0
        self.progress = 0.0
        self.worker = worker

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def check_all(self):
        self.check_valid_state()
        if hasattr(self, "constraints"):
            self.check_constraints()
        if hasattr(self, "static_constraints"):
            self.check_static_constraints()
        if hasattr(self, "check"):
            self.check()

    def check_valid_state(self):
        if hasattr(self, "valid_state") and not self.production_unit.get_state() in self.valid_state:
            raise IllegalStateToPerformAction(
                "Action %s cannot be perform while in state %s" % (self, self.production_unit.state))

    def check_constraints(self):
        for constraint in self.constraints:
            if not constraint.validate(self.worker):
                raise CannotPerformOperation(constraint.get_message())

    def check_static_constraints(self):
        for constraint in self.static_constraints:
            constraint(self).validate(self.worker)

    def perform(self, during=1):
        self.check_all()
        for i in range(during):
            logger.debug("###TIME### - %d" % i)
            self.do_step()

    def do_step(self):
        if self.is_operation_complete():
            self.progress = 0

        if self.operation_ready_to_be_performed():
            self._do_step()
            self.progress += self.get_progress_step()

        if self.is_operation_complete():
            self.on_operation_complete()

        if self.worker:
            self.worker.add_unit_of_work()

    def on_operation_complete(self):
        pass

    def get_progress_step(self):
        return 1.0 / self.time_to_perform

    def operation_ready_to_be_performed(self):
        return True

    def is_operation_complete(self):
        return self.progress == 1

    def _do_step(self):
        pass

class LoadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED, ProductionUnit.PRODUCING]
    static_constraints = [HasWorkerConstraint, InputValidForSpecConstraint]

    def __init__(self, inputs, *args, **kwargs):
        self.inputs = inputs
        super(LoadOperation, self).__init__(*args, **kwargs)

    def _do_step(self):
        input = copy.copy(self.inputs)
        input.quantity = self.inputs.quantity / self.time_to_perform
        self.production_unit.load(input)


class AllInOneLoadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]
    static_constraints = [HasWorkerConstraint, InputValidForSpecConstraint]

    def __init__(self, inputs, *args, **kwargs):
        self.inputs = inputs
        super(AllInOneLoadOperation, self).__init__(*args, **kwargs)

    def on_operation_complete(self):
        input = copy.copy(self.inputs)
        self.production_unit.load(input)


class UnloadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, quantity, zone, *args, **kwargs):
        self.quantity = quantity
        self.zone = zone
        super(UnloadOperation, self).__init__(*args, **kwargs)

    def _do_step(self):
        self.done = self.quantity * self.progress
        self.zone.add_to_stock(self.production_unit.output_stocking_zone.stock.popitem()[1])

    def operation_ready_to_be_performed(self):
        return bool(self.production_unit.output_stocking_zone.stock)

def create_operation(class_name, action, valid_states):
    def _do_step(self):
        getattr(self.production_unit, action)()
    return type(class_name, (Operation,), {'_do_step': _do_step, "valid_state": valid_states})

StartOperation = create_operation("StartOperation","start", [ProductionUnit.IDLE])
StopOperation = create_operation("StopOperation","stop", [ProductionUnit.STARTED])


class ProduceOperation(Operation):
    valid_state = [ProductionUnit.STARTED, ProductionUnit.PRODUCING]

    def get_progress_step(self):
        return self.production_unit.rate

    def _do_step(self):
        if not self.progress:
            self.progress += self.get_progress_step()
        if not self.production_unit.get_state() == ProductionUnit.PRODUCING:
            self.production_unit.set_state(ProductionUnitPRODUCINGState)

        inputs = self.production_unit.inputs
        spec = self.production_unit.spec
        if not spec.validate_all(inputs):
            self.production_unit.set_state(ProductionUnitSTARTEDState)
            raise CannotProduce("Inputs %s does not match constraints %s" % (inputs, spec))
        if self.progress == 1:
            self.production_unit.produce()
            self.progress = 0

    def on_operation_complete(self):
        logger.debug("Produce has completed a product")

    def is_operation_complete(self):
        return not bool(self.production_unit.inputs)


class Process(Operation):
    def __init__(self, production_unit, operations):
        super(Process, self).__init__(production_unit=production_unit)
        self.operations = operations
        self.queue = self.operations[:]
        self.current = self.queue.pop(0)

    def _do_step(self):
        logger.debug("Process: Current operation: %s" % self.current)
        self.current.do_step()
        if self.current.is_operation_complete():
            self.current = self.queue.pop(0)

    def is_operation_complete(self):
        return not bool(self.queue)

    def on_operation_complete(self):
        self.queue.extend(self.operations[:])

class ParallelProcess(Operation):
    def __init__(self, process_list):
        super(ParallelProcess, self).__init__(      )
        self.processes = process_list

    def _do_step(self):
        for process in self.processes:
            logger.debug("Running parallel process %s" % process)
            process.do_step()
